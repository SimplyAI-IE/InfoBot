import os
import json
import logging
import importlib
from typing import Optional, Dict, Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel
from uuid import uuid4
from dotenv import load_dotenv
from weasyprint import HTML
from io import BytesIO

from backend.gpt_engine import get_gpt_response  # ✅
from backend.memory import MemoryManager
from backend.models import init_db, User, SessionLocal, ChatHistory
from backend.logging_config import setup_logging
from backend.apps.base_app import BaseApp
from backend.apps.pension_guru.flow_engine import PensionFlow
from backend.apps.concierge.concierge_api import router as concierge_router

from fastapi.staticfiles import StaticFiles
import os

setup_logging()

logger = logging.getLogger(__name__)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://infobot-h7cr.onrender.com",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend static files from ../public/
current_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(current_dir, "..", "..", "public")
app.mount("/", StaticFiles(directory=os.path.join(current_dir, "..", "public"), html=True), name="static")



os.environ["G_MESSAGES_DEBUG"] = ""
load_dotenv()

logger.info("Initializing database...")
init_db()
logger.info("Database initialized.")

db = SessionLocal()
memory = MemoryManager(db)


class ChatRequest(BaseModel):
    user_id: Optional[str] = None
    message: str
    tone: str = ""


app_id: Optional[str] = os.getenv("ACTIVE_APP")
if not app_id:
    raise RuntimeError("ACTIVE_APP environment variable not set.")

config: Dict[str, Any] = json.load(open(f"backend/apps/{app_id}/config.json"))

try:
    module = importlib.import_module(f"backend.apps.{app_id}.extract")
    class_name: str = config.get("class_name", "PensionGuruApp")
    extract_class = getattr(module, class_name)
    extract_instance: BaseApp = extract_class()
except (ImportError, AttributeError, FileNotFoundError) as e:
    logger.error(f"Failed to load app '{app_id}': {e}", exc_info=True)
    raise RuntimeError(
        f"Could not load application '{app_id}'. Check configuration and file paths."
    ) from e

if not isinstance(extract_instance, BaseApp):
    raise TypeError(
        f"{app_id} extract module's class '{class_name}' does not implement required BaseApp interface."
    )

logger.info(f"✅ Loaded app: {app_id} using class {class_name}")
app.include_router(concierge_router)


@app.post("/chat")
async def chat(req: ChatRequest, request: Request) -> dict[str, str]:
    user_id: str = req.user_id or f"anon_{uuid4().hex[:10]}"
    user_message: str = req.message.strip()
    tone: str = req.tone or config.get("tone_instruction_default", "adult")

    logger.info(
        f"--- New Chat Request --- User: {user_id}, Tone: {tone}, Message: '{user_message}'"
    )

    if user_message == "__INIT__":
        profile = memory.get_user_profile(user_id)
        flow = PensionFlow(profile, user_id)
        scripted = flow.step()
        if scripted:
            memory.save_chat_message(user_id, "assistant", scripted)
            return {"response": scripted, "user_id": user_id}

        reply = get_gpt_response("__INIT__", user_id, tone=tone)
        memory.save_chat_message(user_id, "assistant", reply)
        return {"response": reply, "user_id": user_id}

    try:
        profile = extract_instance.extract_user_data(user_id, user_message)
    except Exception as e:
        logger.error(f"Data extraction error for {user_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Extraction failed")

    block_msg = extract_instance.block_response(user_message, profile)
    if block_msg:
        memory.save_chat_message(user_id, "user", user_message)
        memory.save_chat_message(user_id, "assistant", block_msg)
        return {"response": block_msg, "user_id": user_id}

    history = memory.get_chat_history(user_id, limit=2)
    if extract_instance.wants_tips(profile, user_message.lower(), history):
        reply = extract_instance.tips_reply()
        memory.save_chat_message(user_id, "user", user_message)
        memory.save_chat_message(user_id, "assistant", reply)
        memory.save_user_profile(user_id, {"pending_action": None})
        return {"response": reply, "user_id": user_id}

    flow = PensionFlow(profile, user_id)
    scripted_response = flow.step()
    if scripted_response:
        memory.save_chat_message(user_id, "user", user_message)
        memory.save_chat_message(user_id, "assistant", scripted_response)
        return {"response": scripted_response, "user_id": user_id}

    if getattr(profile, "pending_step", None) is None:
        calc = extract_instance.get_pension_calculation_reply(user_id)
        if calc:
            memory.save_chat_message(user_id, "user", user_message)
            memory.save_chat_message(user_id, "assistant", calc)
            return {"response": calc, "user_id": user_id}

    try:
        reply = get_gpt_response(user_message, user_id, tone=tone)
        memory.save_chat_message(user_id, "user", user_message)
        if reply:
            memory.save_chat_message(user_id, "assistant", reply)

            if extract_instance.should_offer_tips(reply):
                memory.save_user_profile(user_id, {"pending_action": "offer_tips"})
            elif getattr(profile, "pending_action", None):
                memory.save_user_profile(user_id, {"pending_action": None})

        return {"response": reply or "...", "user_id": user_id}
    except Exception as e:
        logger.error(f"GPT error for {user_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="I'm sorry, something broke. Please try again shortly.",
        )


@app.post("/auth/google")
async def auth_google(user_data: Dict[str, Any]) -> Dict[str, str]:
    if not user_data or "sub" not in user_data:
        logger.error("Invalid user data received in /auth/google")
        raise HTTPException(status_code=400, detail="Invalid user data received")

    user_id: str = user_data["sub"]
    logger.info(f"Processing Google auth for user_id: {user_id}")
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.info(
                f"New user detected, creating user and profile entry for user_id: {user_id}"
            )
            user = User(
                id=user_id,
                name=user_data.get("name", "Unknown User"),
                email=user_data.get("email"),
            )
            db.add(user)
            db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database error during auth for {user_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Database operation failed")
    finally:
        db.close()

    return {"status": "ok", "user_id": user_id}


@app.get("/export-pdf")
async def export_pdf(user_id: str) -> StreamingResponse:
    profile = memory.get_user_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="No profile found for PDF export.")

    db = SessionLocal()
    try:
        messages = (
            db.query(ChatHistory)
            .filter(ChatHistory.user_id == user_id)
            .order_by(ChatHistory.timestamp)
            .all()
        )
    finally:
        db.close()

    profile_fields: list[str] = config.get("profile_fields", [])
    profile_text = (
        f"<h1>{config.get('pdf_title', 'Assistant Summary')}</h1><h2>User Info</h2><ul>"
    )
    for field in profile_fields:
        label = field.replace("_", " ").title()
        rendered = extract_instance.render_profile_field(field, profile)
        profile_text += f"<li>{label}: {rendered}</li>"
    profile_text += "</ul>"

    chat_log = "<h2>Chat History</h2><ul>"
    if messages:
        for m in messages:
            role = "You" if m.role == "user" else config.get("name", "Assistant")
            content = getattr(m, "content", "") or ""
            content_escaped = (
                content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            )
            chat_log += f"<li><strong>{role}:</strong> {content_escaped}</li>"
    else:
        chat_log += "<li>No chat history found.</li>"
    chat_log += "</ul>"

    pdf_buffer = BytesIO()
    try:
        html = HTML(string=profile_text + chat_log)
        html.write_pdf(pdf_buffer)
        pdf_buffer.seek(0)
    except Exception as e:
        logger.error(f"Error generating PDF for user {user_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate PDF report.")

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={app_id}_report_{user_id}.pdf"
        },
    )


@app.post("/chat/forget")
async def forget_chat_history(request: Request) -> Dict[str, str]:
    data: Dict[str, Any] = await request.json()
    user_id: Optional[str] = data.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="Missing user_id")

    logger.info(f"Received request to forget data for user {user_id}")
    db = SessionLocal()
    try:
        deleted_chats = (
            db.query(ChatHistory)
            .filter(ChatHistory.user_id == user_id)
            .delete(synchronize_session=False)
        )
        logger.info(f"Deleted {deleted_chats} chat messages for user {user_id}")

        deleted_profile = memory.repo.delete_user_profile(user_id)
        logger.info(f"Deleted profile entry for user {user_id}: {deleted_profile}")

        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting data for {user_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to clear history")
    finally:
        db.close()

    return {"status": "ok", "message": "Chat history and profile cleared."}


# Static file mount setup
static_dir: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../public"))

if os.path.isdir(static_dir):
    logger.info(f"Serving static files from: {static_dir}")
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
async def serve_index() -> FileResponse:
    file_path: str = os.path.join(static_dir, "index.html")
    if os.path.exists(file_path):
        return FileResponse(file_path)
    else:
        raise HTTPException(status_code=404, detail="Frontend not found")


@app.get("/healthz")
async def healthz() -> Dict[str, str]:
    return {"status": "ok"}
