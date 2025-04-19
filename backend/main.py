# --- main.py ---
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
from dotenv import load_dotenv
from gpt_engine import get_gpt_response # Keep gpt_engine import
from memory import get_user_profile, save_user_profile, save_chat_message, get_chat_history
from models import init_db, User, SessionLocal, UserProfile, ChatHistory
from fastapi.responses import StreamingResponse, JSONResponse # Added JSONResponse
from weasyprint import HTML
from io import BytesIO
import re
import logging
import importlib
from typing import Optional
from uuid import uuid4
from backend.apps.base_app import BaseApp
from backend.apps.pension_guru.flow_engine import PensionFlow # Import FlowEngine here

os.environ["G_MESSAGES_DEBUG"] = ""
logging.basicConfig(level=logging.INFO) # Use INFO for more visibility during dev
logger = logging.getLogger(__name__)

load_dotenv()
app = FastAPI()

# --- CORS Middleware (remains unchanged) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://infobot-h7cr.onrender.com",
        "http://localhost:5500",
        "http://127.0.0.1:5500" # Added explicit loopback IP
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
print("✅ CORS enabled for:", ["https://infobot-h7cr.onrender.com", "http://localhost:5500", "http://127.0.0.1:5500"])


logger.info("Initializing database...")
init_db()
logger.info("Database initialized.")

class ChatRequest(BaseModel):
    user_id: Optional[str] = None
    message: str
    tone: str = ""

# --- App Loading Logic (remains unchanged) ---
app_id = os.getenv("ACTIVE_APP")
if not app_id:
     raise RuntimeError("ACTIVE_APP environment variable not set.")
config = json.load(open(f"backend/apps/{app_id}/config.json"))

try:
    module = importlib.import_module(f"backend.apps.{app_id}.extract")
    class_name = config.get("class_name", "PensionGuruApp") # Default added for safety
    extract_class = getattr(module, class_name)
    # Instantiate the app class
    extract_instance: BaseApp = extract_class()
except (ImportError, AttributeError, FileNotFoundError) as e:
     logger.error(f"Failed to load app '{app_id}': {e}", exc_info=True)
     raise RuntimeError(f"Could not load application '{app_id}'. Check configuration and file paths.") from e


if not isinstance(extract_instance, BaseApp):
    raise TypeError(f"{app_id} extract module's class '{class_name}' does not implement required BaseApp interface.")
logger.info(f"✅ Loaded app: {app_id} using class {class_name}")


@app.post("/chat")
async def chat(req: ChatRequest, request: Request):
    user_id = req.user_id or f"anon_{uuid4().hex[:10]}"
    user_message = req.message.strip()
    user_message_lower = user_message.lower()
    tone = req.tone or config.get("tone_instruction_default", "adult") # Use default tone if none provided

    logger.info(f"--- New Chat Request --- User: {user_id}, Tone: {tone}, Message: '{user_message}'")

    # --- Refactored Logic Flow ---

    # 1. Handle INIT message separately first
    if user_message == "__INIT__":
        logger.info(f"Handling __INIT__ command for user_id: {user_id}")
        profile = get_user_profile(user_id) # Get profile for init message
        flow = PensionFlow(profile, user_id)
        scripted_response = flow.step() # Check if flow dictates initial message

        if scripted_response:
             logger.info(f"INIT - Flow provided initial response for {user_id}.")
             # Don't save __INIT__ itself, just the response
             save_chat_message(user_id, 'assistant', scripted_response)
             return {"response": scripted_response, "user_id": user_id}
        else:
             # If flow doesn't handle INIT, use default GPT init logic
             logger.info(f"INIT - Flow did not provide response, using default GPT init for {user_id}.")
             reply = get_gpt_response("__INIT__", user_id, tone=tone) # Use specific __INIT__ call
             save_chat_message(user_id, 'assistant', reply) # Save the welcome message
             return {"response": reply, "user_id": user_id}

    # 2. Extract Data & Get Updated Profile
    try:
        # Pass the instance, not the class
        profile = extract_instance.extract_user_data(user_id, user_message)
        logger.info(f"Data extraction complete for {user_id}. Profile updated.")
    except Exception as e:
        logger.error(f"Error during data extraction for user {user_id}: {e}", exc_info=True)
        # Decide how to handle critical extraction errors - maybe return an error message?
        raise HTTPException(status_code=500, detail="Error processing your message data.")

    # 3. Check for Blocking Conditions (e.g., unsupported region AFTER extraction)
    block_msg = extract_instance.block_response(user_message, profile)
    if block_msg:
        logger.warning(f"Response blocked for user {user_id}. Reason: {block_msg}")
        # Save user message potentially? Or just return block? Let's save both.
        save_chat_message(user_id, 'user', user_message)
        save_chat_message(user_id, 'assistant', block_msg)
        return {"response": block_msg, "user_id": user_id}

    # 4. Handle "Wants Tips" Logic (if applicable)
    history = get_chat_history(user_id, limit=2)
    if extract_instance.wants_tips(profile, user_message_lower, history):
        logger.info(f"User {user_id} requested tips.")
        reply = extract_instance.tips_reply()
        save_chat_message(user_id, 'user', user_message)
        save_chat_message(user_id, 'assistant', reply)
        save_user_profile(user_id, "pending_action", None) # Clear pending action
        return {"response": reply, "user_id": user_id}

    # 5. Process Conversation Flow
    flow = PensionFlow(profile, user_id)
    scripted_response = flow.step() # Get the *next* scripted step/prompt

    if scripted_response:
        logger.info(f"Flow provided scripted response for user {user_id}: '{scripted_response[:50]}...'")
        save_chat_message(user_id, 'user', user_message)
        save_chat_message(user_id, 'assistant', scripted_response)
        # Profile state (pending_step) was updated inside flow.step()
        return {"response": scripted_response, "user_id": user_id}

    # 6. Check if Calculation is Ready (Example for Ireland)
    #    (This check happens *after* the flow step returns None, meaning the flow part is done)
    current_step = getattr(profile, "pending_step", None) # Re-check step after flow.step()
    if current_step is None: # Flow finished, ready for calculation or GPT
         logger.info(f"Flow finished or paused for user {user_id}. Checking for calculation trigger.")
         # Use the instance method we added in extract.py
         calculation_reply = extract_instance.get_pension_calculation_reply(user_id)
         if calculation_reply:
              logger.info(f"Pension calculation generated for user {user_id}.")
              save_chat_message(user_id, 'user', user_message)
              save_chat_message(user_id, 'assistant', calculation_reply)
              # Pending step should be None already, pending_action might be set by get_pension_calculation_reply
              return {"response": calculation_reply, "user_id": user_id}
         else:
              logger.info(f"Conditions for calculation not met for user {user_id}.")
              # Proceed to GPT if no calculation was triggered


    # 7. If no scripted response and no calculation, proceed to GPT
    logger.info(f"No scripted response/calculation, proceeding with GPT for user {user_id}")
    try:
        # Pass user_message (not __INIT__), user_id, tone
        reply = get_gpt_response(user_message, user_id, tone=tone)
        logger.info(f"GPT response generated successfully for user_id: {user_id}")

        # Save interaction
        save_chat_message(user_id, 'user', user_message)
        if reply: # Ensure reply is not empty/None
            save_chat_message(user_id, 'assistant', reply)

            # Check if GPT reply suggests offering tips
            if extract_instance.should_offer_tips(reply):
                 logger.info(f"GPT response triggered offer_tips for user {user_id}")
                 save_user_profile(user_id, "pending_action", "offer_tips")
            # Clear pending action if GPT reply doesn't offer tips and an action was pending
            elif getattr(profile, "pending_action", None):
                 save_user_profile(user_id, "pending_action", None)

        return {"response": reply or "...", "user_id": user_id}

    except Exception as e:
        logger.error(f"Error during GPT flow for user_id: {user_id}: {e}", exc_info=True)
        # Return a generic error message, don't save potentially faulty interaction
        return JSONResponse(
             status_code=500,
             content={"response": "I'm sorry, I encountered a technical issue. Please try rephrasing or wait a moment.", "user_id": user_id}
        )


# --- Auth Endpoint (remains unchanged) ---
@app.post("/auth/google")
async def auth_google(user_data: dict):
    # ... (existing code) ...
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
            user = User(id=user_id, name=user_data.get("name", "Unknown User"), email=user_data.get("email"))
            db.add(user)
            if not profile:
                # Ensure profile exists or create it when user is created
                profile = UserProfile(user_id=user_id)
                # You might want to pre-populate profile fields here if applicable
                db.add(profile)
            db.commit()
            db.refresh(user)
            if profile: db.refresh(profile) # Refresh profile too if added
        elif not profile: # Existing user but missing profile somehow
             logger.warning(f"User {user_id} exists but profile missing. Creating profile.")
             profile = UserProfile(user_id=user_id)
             db.add(profile)
             db.commit()
             db.refresh(profile)

    except Exception as e:
        db.rollback()
        logger.error(f"Database error during auth for user_id {user_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Database operation failed")
    finally:
        db.close()

    return {"status": "ok", "user_id": user_id}

# --- PDF Export Endpoint (remains unchanged, uses instance) ---
@app.get("/export-pdf")
async def export_pdf(user_id: str):
    profile = get_user_profile(user_id)
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

    def safe_get(obj, attr, default="—"):
        val = getattr(obj, attr, None)
        return val if val is not None else default

    profile_fields = config.get("profile_fields", [])
    profile_text = f"<h1>{config.get('pdf_title', 'Assistant Summary')}</h1><h2>User Info</h2><ul>"

    for field in profile_fields:
        label = field.replace("_", " ").title()
        # Use the instance method for rendering
        rendered = extract_instance.render_profile_field(field, profile)
        profile_text += f"<li>{label}: {rendered}</li>"

    profile_text += "</ul>"

    chat_log = "<h2>Chat History</h2><ul>"
    if messages:
        for m in messages:
            role = "You" if m.role == "user" else config.get("name", "Assistant")
            content = getattr(m, 'content', '') or ''
            content_escaped = content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
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


# --- Forget Endpoint (remains unchanged) ---
@app.post("/chat/forget")
async def forget_chat_history(request: Request):
    # ... (existing code) ...
    data = await request.json()
    user_id = data.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="Missing user_id")

    logger.info(f"Received request to forget data for user {user_id}")
    db = SessionLocal()
    try:
        # Delete chat history
        deleted_chats = db.query(ChatHistory).filter(ChatHistory.user_id == user_id).delete(synchronize_session=False)
        logger.info(f"Deleted {deleted_chats} chat messages for user {user_id}")
        # Delete user profile data (or reset fields)
        # Option 1: Delete the profile row entirely
        deleted_profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).delete(synchronize_session=False)
        logger.info(f"Deleted {deleted_profile} profile entry for user {user_id}")
        # Option 2: Reset specific fields (if you want to keep the user_id association)
        # profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        # if profile:
        #     profile.age = None
        #     profile.income = None
        #     # ... reset other fields ...
        #     profile.pending_step = None # Reset flow state
        #     profile.pending_action = None
        #     logger.info(f"Reset profile fields for user {user_id}")

        db.commit()
        logger.info(f"Successfully cleared data for user {user_id}")
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting data for user {user_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to clear history")
    finally:
        db.close()

    # Re-create a basic profile shell after deletion? Or let auth handle it on next login?
    # Let auth handle it seems cleaner.

    return {"status": "ok", "message": "Chat history and profile cleared."}

# --- Static Files & Healthz (remains unchanged) ---
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../public"))

# Check if static directory exists
if not os.path.isdir(static_dir):
     logger.error(f"Static files directory not found: {static_dir}")
     # Decide how to handle this - raise error or just log?
     # For now, log and proceed, but frontend won't load.
else:
     logger.info(f"Serving static files from: {static_dir}")
     app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def serve_index():
    file_path = os.path.join(static_dir, "index.html")
    if os.path.exists(file_path):
        logger.debug(f"Serving index.html from: {file_path}")
        return FileResponse(file_path)
    else:
        logger.error(f"index.html not found at: {file_path}")
        raise HTTPException(status_code=404, detail="Frontend not found")


@app.get("/healthz")
async def healthz():
    # Add db check?
    # db = SessionLocal()
    # try:
    #     db.execute(text("SELECT 1"))
    #     db_status = "ok"
    # except Exception:
    #     db_status = "error"
    # finally:
    #     db.close()
    # return {"status": "ok", "database": db_status}
    return {"status": "ok"}

# --- End of main.py ---