
from fastapi import APIRouter, Request
from pydantic import BaseModel
import yaml
from langdetect import detect

router = APIRouter()

with open("backend/apps/concierge/concierge_knowledge.yaml", "r") as f:
    knowledge = yaml.safe_load(f)

class ConciergeQuery(BaseModel):
    message: str

@router.post("/concierge")
async def concierge_response(req: ConciergeQuery):
    msg = req.message.strip().lower()
    lang = detect(msg)

    if "check" in msg or "check-in" in msg or "check out" in msg:
        return {
            "response": (
                f"Check-in is from **{knowledge['hotel']['checkin']}**, and checkout is by **{knowledge['hotel']['checkout']}**."
            )
        }
    elif "wifi" in msg:
        wifi_info = knowledge['hotel']['wifi']
        return {
           "response": f"The Wi-Fi details are:\\n\\n{wifi_info}"

        }
    elif "facebook" in msg:
        return {
            "response": f"You can view the hotel's Facebook page here: [Facebook]({knowledge['hotel']['facebook']})"
        }
    elif "website" in msg:
        return {
            "response": f"The official website is [whitesands.ie]({knowledge['hotel']['website']})"
        }
    elif "dine" in msg or "restaurant" in msg or "eat" in msg:
        options = "\n".join(f"- {place}" for place in knowledge["area"]["ballyheigue"]["dining"])
        return {
            "response": f"Recommended places to eat near Ballyheigue:\n\n{options}"
        }
    elif "do" in msg or "see" in msg or "activity" in msg:
        activities = "\n".join(f"- {thing}" for thing in knowledge["area"]["ballyheigue"]["activities"])
        return {
            "response": f"Things to do in Ballyheigue:\n\n{activities}"
        }
    else:
        return {
            "response": "I'm here to help with hotel info, check-in times, Wi-Fi, local attractions, or dining. Ask me anything related to White Sands Hotel or Ballyheigue!"
        }
