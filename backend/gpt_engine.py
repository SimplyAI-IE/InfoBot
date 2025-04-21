# --- gpt_engine.py ---
import sys
import os
import json
import logging
import importlib
from backend.models import SessionLocal, User
from dotenv import load_dotenv
from openai import OpenAI
from backend.memory import MemoryManager
from backend.apps.base_app import BaseApp  # ✅ updated import

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Add project root to sys.path (optional fallback)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Load app config
app_id = os.getenv("ACTIVE_APP")
print(f"DEBUG: ACTIVE_APP loaded as: {app_id}")  # ✅ add this to confirm env var loading

if not app_id:
    raise RuntimeError("Missing ACTIVE_APP in .env")

app_path = f"backend.apps.{app_id}"
config_path = f"backend/apps/{app_id}/config.json"
if not os.path.exists(config_path):
    raise FileNotFoundError(f"Missing config.json for app: {app_id}")
config = json.load(open(config_path))

# Load the prompt
prompt_path = f"backend/apps/{app_id}/{config['system_prompt_file']}"
if not os.path.exists(prompt_path):
    raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
with open(prompt_path, encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()

# Dynamically load app plugin
module = importlib.import_module(f"{app_path}.extract")
class_name = config.get("class_name", "PensionGuruApp")
extract_class = getattr(module, class_name)
extract: BaseApp = extract_class()

if not isinstance(extract, BaseApp):
    raise TypeError(f"{class_name} must implement BaseApp interface")

# Load OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logger.critical("OPENAI_API_KEY environment variable not set!")
client = OpenAI(api_key=api_key)

CHAT_HISTORY_LIMIT = 5

def get_gpt_response(user_input, user_id, tone=""):
    logger.info(f"get_gpt_response called for user_id: {user_id}")
    db = SessionLocal()
    memory = MemoryManager(db)
    try:
        profile = memory.get_user_profile(user_id)
        history = memory.get_chat_history(user_id, limit=CHAT_HISTORY_LIMIT)
    finally:
        db.close()

    # --- Removed initial pre_prompt call here ---

    # Optional pre-GPT flow from app - handle __INIT__ or block
    # Note: The primary flow check now happens in main.py *before* calling this function
    if user_input.strip() == "__INIT__":
        scripted_prompt = extract.pre_prompt(profile, user_id) # Keep for explicit INIT handling if needed by app
        if scripted_prompt:
             return scripted_prompt
        # Fallback __INIT__ logic if pre_prompt doesn't handle it
        db = SessionLocal()
        user = db.query(User).filter(User.id == user_id).first()
        db.close()
        name = user.name if user and user.name else "there"
        if profile:
            summary = extract.format_user_context(profile)
            return f"Welcome back, {name}! Here's what I remember: {summary}. What would you like to explore today?"
        return config.get("init_message", "Welcome! How can I assist you today?")

    block_msg = extract.block_response(user_input, profile)
    if block_msg:
        return block_msg

    # Proceed with standard GPT call if not blocked and not handled by flow in main.py
    logger.info(f"Processing regular message for user_id: {user_id}")
    history = memory.get_chat_history(user_id, limit=CHAT_HISTORY_LIMIT)
    logger.debug(f"Retrieved {len(history)} messages from history for user_id: {user_id}")

    summary = extract.format_user_context(profile)
    tone_map = {
        "7": "Use very simple language, short sentences, and relatable examples a 7-year-old could understand.",
        "14": "Explain ideas like you're talking to a 14-year-old. Be clear and concrete, avoid jargon.",
        "adult": "Use plain English suitable for an average adult. Assume no special knowledge.",
        "pro": "Use financial terminology and industry language for a professional audience.",
        "genius": "Use technical depth and precision appropriate for a professor. Do not simplify."
    }
    tone_instruction = tone_map.get(tone, "")
    system_message = SYSTEM_PROMPT.replace("{{tone_instruction}}", tone_instruction) + "\n\n" + summary

    logger.debug(f"Formatted profile summary: {summary}")

    messages = [{"role": "system", "content": system_message}]
    for msg in history:
        if msg["role"] in ['user', 'assistant']:
            messages.append(msg)
        else:
            logger.warning(f"Skipping history message with invalid role '{msg['role']}' for user_id: {user_id}")

    messages.append({"role": "user", "content": user_input})

    # --- Calculation Logic moved to extract.py / triggered from main.py if needed ---
    # (The pension calculation display logic was previously here but is better placed
    # within the app's logic or triggered explicitly after flow completion)

    try:
        logger.info(f"Calling OpenAI API for user_id: {user_id}...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7
        )
        reply = response.choices[0].message.content
        logger.info(f"OpenAI API call successful for user_id: {user_id}")
        logger.debug(f"OpenAI Response: {reply}")
        return reply
    except Exception as e:
        logger.error(f"Error calling OpenAI API for user_id {user_id}: {e}", exc_info=True)
        return "I'm sorry, but I encountered a technical difficulty while processing your request. Please try again in a few moments."

# --- End of gpt_engine.py ---