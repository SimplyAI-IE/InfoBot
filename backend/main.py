# --- main.py ---
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from fastapi import FastAPI
from pydantic import BaseModel
import json
from dotenv import load_dotenv
from gpt_engine import get_gpt_response
from memory import get_user_profile, save_user_profile, save_chat_message, get_chat_history
from models import init_db, User, SessionLocal, UserProfile, ChatHistory
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from weasyprint import HTML
from io import BytesIO
import re
import logging
import os
from typing import Optional
from gpt_engine import extract  # already imported dynamically

os.environ["G_MESSAGES_DEBUG"] = ""
# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

load_dotenv()
app = FastAPI()

# Allow CORS so frontend can connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create DB table(s)
logger.info("Initializing database...")
init_db()
logger.info("Database initialized.")

class ChatRequest(BaseModel):
    user_id: str
    message: str
    tone: str = ""

# Set of affirmative responses for state checking
affirmative_responses = {"sure", "yes", "ok", "okay", "fine", "yep", "please", "yes please"}


app_id = os.getenv("ACTIVE_APP")
config = json.load(open(f"apps/{app_id}/config.json"))

@app.post("/chat")
async def chat(req: ChatRequest):
    user_id = req.user_id
    user_message = req.message.strip()
    user_message_lower = user_message.lower()
    extract.extract_user_data(user_id, user_message)
    logger.info(f"Received chat request from user_id: {user_id}, message: '{user_message}'")

    # --- Handle __INIT__ separately ---
    if user_message == "__INIT__":
        logger.info(f"Handling __INIT__ command for user_id: {user_id}")
        reply = get_gpt_response(user_message, user_id, tone=req.tone)
        return {"response": reply}

    if not user_message:
        logger.warning(f"Received empty message from user_id: {user_id}")
        profile = get_user_profile(user_id)
        history = get_chat_history(user_id, limit=2)

        if hasattr(extract, "handle_empty_input"):
            reply = extract.handle_empty_input(user_id, history, profile, req.tone)
            if reply:
                return {"response": reply}

        raise HTTPException(status_code=400, detail="Message cannot be empty")


    # --- State Handling Logic ---
    profile = get_user_profile(user_id)
    give_tips_directly = False
    history = get_chat_history(user_id, limit=2)
    if hasattr(extract, "wants_tips") and extract.wants_tips(profile, user_message_lower, history):
        reply = extract.tips_reply()
        save_chat_message(user_id, 'user', user_message)
        save_chat_message(user_id, 'assistant', reply)
        save_user_profile(user_id, "pending_action", None)
        return {"response": reply}

    # --- Standard Chat Flow ---
    logger.info(f"Proceeding with standard chat flow for user {user_id}")
    try:
        extract.extract_user_data(user_id, user_message)
        profile = get_user_profile(user_id)
    except Exception as e:
        logger.error(f"Error extracting data for user {user_id}: {e}", exc_info=True)

    reply = ""
    try:
        reply = get_gpt_response(user_message, user_id, tone=req.tone)
        logger.info(f"GPT response generated successfully for user_id: {user_id}")
    except Exception as e:
        logger.error(f"Error getting GPT response for user_id: {user_id}: {e}", exc_info=True)
        reply = "I'm sorry, I encountered a technical issue trying to process that. Could you try rephrasing?"

    save_chat_message(user_id, 'user', user_message)
    if reply:
        save_chat_message(user_id, 'assistant', reply)

    # --- State Setting Logic ---
    if hasattr(extract, "should_offer_tips") and extract.should_offer_tips(reply):
        save_user_profile(user_id, "pending_action", "offer_tips")
    elif profile and not hasattr(profile, 'pending_action'):
        logger.warning(f"Profile for user {user_id} exists but missing 'pending_action' attribute. Cannot set state.")

    return {"response": reply}

@app.post("/auth/google")
async def auth_google(user_data: dict):
    if not user_data or "sub" not in user_data:
        logger.error("Invalid user data received in /auth/google")
        raise HTTPException(status_code=400, detail="Invalid user data received")

    user_id = user_data["sub"]
    logger.info(f"Processing Google auth for user_id: {user_id}")
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

        if not user:
            logger.info(f"New user detected, creating user and profile entry for user_id: {user_id}")
            user = User(
                id=user_id,
                name=user_data.get("name", "Unknown User"),
                email=user_data.get("email")
            )
            db.add(user)
            if not profile:
                profile = UserProfile(user_id=user_id)
                db.add(profile)
            db.commit()
            db.refresh(user)
            logger.info(f"Successfully created user and profile entry for user_id: {user_id}")
        else:
            logger.info(f"Existing user found for user_id: {user_id}")
            if not profile:
                logger.warning(f"Existing user {user_id} found, but profile missing. Creating profile.")
                profile = UserProfile(user_id=user_id)
                db.add(profile)
                db.commit()

    except Exception as e:
        db.rollback()
        logger.error(f"Database error during auth for user_id {user_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Database operation failed")
    finally:
        db.close()

    return {"status": "ok", "user_id": user_id}

@app.get("/")
async def root():
    return {"message": f"{config.get('name', 'Assistant')} API is running"}

@app.get("/export-pdf")
async def export_pdf(user_id: str):
    profile = get_user_profile(user_id)

    if not profile:
        raise HTTPException(status_code=404, detail="No profile found for PDF export.")

    db = SessionLocal()
    messages = []
    try:
        messages = (
            db.query(ChatHistory)
            .filter(ChatHistory.user_id == user_id)
            .order_by(ChatHistory.timestamp)
            .all()
        )
    except Exception as e:
        logger.error(f"Failed to retrieve chat history for PDF export for user {user_id}: {e}")
    finally:
        db.close()

    def safe_get(obj, attr, default="—"):
        val = getattr(obj, attr, None)
        return val if val is not None else default

    income_str = "—"
    if hasattr(profile, 'income') and profile.income is not None:
        region = getattr(profile, 'region', None)
        currency = '£' if region == 'UK' else '€'
        try:
            income_str = f"{currency}{profile.income:,}"
        except (TypeError, ValueError):
            income_str = f"{currency}{profile.income}"

    profile_fields = config.get("profile_fields", [])
    profile_text = f"<h1>{config.get('pdf_title', 'Assistant Summary')}</h1><h2>User Info</h2><ul>"

    for field in profile_fields:
        label = field.replace("_", " ").title()
        if hasattr(extract, "render_profile_field"):
            rendered = extract.render_profile_field(field, profile)
        else:
            rendered = safe_get(profile, field)
        profile_text += f"<li>{label}: {rendered}</li>"

    profile_text += "</ul>"

    chat_log = "<h2>Chat History</h2><ul>"
    if messages:
        for m in messages:
            role = "You" if m.role == "user" else config.get("name", "Assistant")
            content = getattr(m, 'content', '') or ''
            content_escaped = content.replace("&", "&").replace("<", "<").replace(">", ">")
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

    return StreamingResponse(pdf_buffer, media_type="application/pdf", headers={
        "Content-Disposition": f"attachment; filename={app_id}_report_{user_id}.pdf"
    })

@app.post("/chat/forget")
async def forget_chat_history(request: Request):
    data = await request.json()
    user_id = data.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="Missing user_id")

    db = SessionLocal()
    try:
        deleted_chats = db.query(ChatHistory).filter(ChatHistory.user_id == user_id).delete(synchronize_session=False)
        logger.info(f"Deleted {deleted_chats} chat messages for user_id: {user_id}")
        deleted_profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).delete(synchronize_session=False)
        logger.info(f"Deleted {deleted_profile} profile entries for user_id: {user_id}")
        db.commit()
        logger.info(f"Successfully cleared chat history and profile for user_id: {user_id}")
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting data for user {user_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to clear history")
    finally:
        db.close()

    return {"status": "ok", "message": "Chat history and profile cleared."}

    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse
    import os

    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../public"))

    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/")
    async def serve_index():
        return FileResponse(os.path.join(static_dir, "index.html"))
    
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse
    import os

    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../public"))

    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/")
    async def serve_index():
        return FileResponse(os.path.join(static_dir, "index.html"))

# --- End of main.py ---