# --- gpt_engine.py ---
from openai import OpenAI
from memory import get_user_profile, get_chat_history
from importlib import import_module
from models import SessionLocal, User
import json
import os
import logging

# Configure logging
logger = logging.getLogger(__name__)



# Ensure API key is loaded
from dotenv import load_dotenv
load_dotenv()

app_id = os.getenv("ACTIVE_APP")

if not app_id:
    raise RuntimeError("Missing ACTIVE_APP in .env")

app_path = f"apps.{app_id}"

extract = import_module(f"{app_path}.extract")

# Check if API key is available
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logger.critical("OPENAI_API_KEY environment variable not set!")
client = OpenAI(api_key=api_key)

config = json.load(open(f"apps/{app_id}/config.json"))

prompt_path = f"apps/{app_id}/{config['system_prompt_file']}"
with open(prompt_path, encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()


CHAT_HISTORY_LIMIT = 5  # Reduced to focus on recent context


def get_gpt_response(user_input, user_id, tone=""):
    logger.info(f"get_gpt_response called for user_id: {user_id}")
    profile = get_user_profile(user_id)
    if user_input != "__INIT__":
     block_msg = extract.block_response(user_input, profile)
    if block_msg:
        return block_msg
    if block_msg:
        return block_msg
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    db.close()
    name = user.name if user and user.name else "there"

    if user_input.strip() == "__INIT__":
        logger.info(f"Handling __INIT__ message for user_id: {user_id}")
        if profile:
            summary = extract.format_user_context(profile)
            return f"Welcome back, {name}! Here's what I remember: {summary}. What would you like to explore today?"
        else:
            return config.get("init_message", "Welcome! How can I assist you today?")

    logger.info(f"Processing regular message for user_id: {user_id}")
    history = get_chat_history(user_id, limit=CHAT_HISTORY_LIMIT)
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

    try:
        logger.info(f"Calling OpenAI API for user_id: {user_id}...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Change to "gpt-4.1" if available
            messages=messages,
            temperature=0.7
        )
        reply = response.choices[0].message.content
        logger.info(f"OpenAI API call successful for user_id: {user_id}")
        logger.debug(f"OpenAI Response: {reply}")
    except Exception as e:
        logger.error(f"Error calling OpenAI API for user_id {user_id}: {e}", exc_info=True)
        reply = "I'm sorry, but I encountered a technical difficulty while processing your request. Please try again in a few moments."

    return reply
# --- End of gpt_engine.py ---