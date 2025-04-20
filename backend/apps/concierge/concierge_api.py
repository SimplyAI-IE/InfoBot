from fastapi import APIRouter, Body
from pydantic import BaseModel
from pathlib import Path
import yaml

from backend.apps.concierge.concierge_gpt import concierge_gpt_response # Make sure this exists

from backend.apps.concierge.whitesands_scraper import scrape_whitesands_raw, parse_whitesands_content
from backend.apps.concierge.whitesands_scraper import get_cached_whitesands_facts
from backend.apps.concierge.intent_gpt import resolve_intent



router = APIRouter()



@router.get("/concierge/facts")
def get_whitesands_facts(force: bool = False):
    return {"facts": get_cached_whitesands_facts(force=force)}

@router.get("/concierge/facts")
def get_whitesands_facts():
    return {"facts": get_cached_whitesands_facts()}

# --- Models ---
class ConciergeQuery(BaseModel):
    message: str

# --- Load Knowledge Base ---
with open(Path(__file__).parent / "concierge_knowledge.yaml", "r", encoding="utf-8") as f:
    knowledge = yaml.safe_load(f)

# --- Load Follow-Up Flow ---
with open(Path(__file__).parent / "concierge_flow.yaml", "r", encoding="utf-8") as f:
    concierge_flow = yaml.safe_load(f)["intents"]

# --- Intent Matching (simple substring search) ---
def match_intent(message: str):
    msg = message.lower()

    # Check hotel keys
    for key in knowledge["hotel"]:
        if key in msg:
            return key

    # Check area keys
    for key in knowledge["area"]["ballyheigue"]:
        if key in msg:
            return key

    return None

# --- Main Endpoint ---
@router.post("/concierge")
async def handle_concierge(req: ConciergeQuery):
    
    intent = resolve_intent(req.message)

    if intent in knowledge["hotel"]:
        response = knowledge["hotel"][intent]

    elif intent in knowledge["area"]["ballyheigue"]:
        val = knowledge["area"]["ballyheigue"][intent]
        response = "\n".join(val) if isinstance(val, list) else val

    else:
        # fallback if intent wasn't matched
        response = concierge_gpt_response(req.message)

    # Add follow-up if we have a match
    follow_up = concierge_flow.get(intent, {}).get("follow_up")
    if follow_up:
        response += f" {follow_up}"

    return {"response": response}


    # GPT Fallback
    gpt_reply = concierge_gpt_response(req.message)
    return {"response": gpt_reply}
