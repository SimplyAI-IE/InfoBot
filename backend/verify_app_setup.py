import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import os
import json
from importlib import import_module
from dotenv import load_dotenv


# Load .env
load_dotenv()

# Grab app ID
app_id = os.getenv("ACTIVE_APP")
if not app_id:
    raise RuntimeError("❌ Missing ACTIVE_APP in .env")

# Load app config
config_path = f"apps/{app_id}/config.json"
if not os.path.exists(config_path):
    raise FileNotFoundError(f"❌ Missing config file: {config_path}")

config = json.load(open(config_path))

# Check prompt file
prompt_path = f"apps/{app_id}/{config['system_prompt_file']}"
if not os.path.exists(prompt_path):
    raise FileNotFoundError(f"❌ Missing system prompt file: {prompt_path}")

with open(prompt_path, encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()

# Check extractor module
try:
    extract = import_module(f"apps.{app_id}.extract")
except ImportError as e:
    raise ImportError(f"❌ Could not import extractor for app '{app_id}': {e}")

# Check OpenAI key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("❌ OPENAI_API_KEY is not set in .env")

print("✅ All components loaded successfully!")
print(f"🔁 ACTIVE_APP: {app_id}")
print(f"🧠 System prompt: {SYSTEM_PROMPT[:80]}...")
