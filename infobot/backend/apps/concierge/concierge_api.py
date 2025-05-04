from fastapi import APIRouter
from pydantic import BaseModel
from pathlib import Path
from typing import Optional, Dict
import yaml

from backend.apps.concierge.facebook_feed import fetch_facebook_posts
from backend.apps.concierge.concierge_gpt import concierge_gpt_response
from backend.apps.concierge.whitesands_scraper import get_cached_whitesands_facts
from backend.apps.concierge.intent_gpt import resolve_intent

router = APIRouter()


# --- Models ---
class ConciergeQuery(BaseModel):
    message: str


# --- Load Knowledge Base ---
with open(
    Path(__file__).parent / "concierge_knowledge.yaml", "r", encoding="utf-8"
) as f:
    knowledge = yaml.safe_load(f)

# --- Load Follow-Up Flow ---
with open(Path(__file__).parent / "concierge_flow.yaml", "r", encoding="utf-8") as f:
    concierge_flow = yaml.safe_load(f)["intents"]


# --- Facts endpoint ---
@router.get("/concierge/facts")
def get_whitesands_facts(force: bool = False) -> Dict[str, str]:
    return {"facts": get_cached_whitesands_facts(force=force)}


# --- Intent Matching (simple substring search) ---
def match_intent(message: str) -> Optional[str]:
    msg = message.lower()

    for key in knowledge["hotel"]:
        if key in msg:
            return key

    for key in knowledge["area"]["ballyheigue"]:
        if key in msg:
            return key

    return None


# --- Main Endpoint ---
@router.post("/concierge")
async def handle_concierge(req: ConciergeQuery) -> Dict[str, str]:
    intent = resolve_intent(req.message)

    if intent in knowledge["hotel"]:
        response = knowledge["hotel"][intent]

    elif intent in knowledge["area"]["ballyheigue"]:
        val = knowledge["area"]["ballyheigue"][intent]
        response = "\n".join(val) if isinstance(val, list) else val

    else:
        if intent == "events":
            posts = fetch_facebook_posts()
            fb_post = (
                posts[0]["summary"]
                if posts
                else "No recent events found on our Facebook page."
            )
            response = concierge_gpt_response(
                f"The guest asked: {req.message}\nLatest Facebook update: {fb_post}"
            )
        else:
            response = concierge_gpt_response(req.message)

    follow_up = concierge_flow.get(intent, {}).get("follow_up")
    if follow_up:
        response += f" {follow_up}"

    return {"response": response}
