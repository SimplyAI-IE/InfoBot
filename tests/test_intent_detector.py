from infobot.intents.intent_detector import parse_intent_response


def test_callback_requested():
    response = """
    {
        "callback_request": true,
        "name": "Alice",
        "phone": "+441234567890"
    }
    """
    parsed = parse_intent_response(response)
    assert parsed["callback_request"] is True
    assert parsed["name"] == "Alice"
    assert parsed["phone"] == "+441234567890"


def test_callback_not_requested():
    response = """
    {
        "callback_request": false
    }
    """
    parsed = parse_intent_response(response)
    assert parsed["callback_request"] is False
    assert parsed["name"] is None
    assert parsed["phone"] is None


def test_malformed_json():
    response = """
    callback_request: true
    """
    parsed = parse_intent_response(response)
    assert parsed["callback_request"] is False
    assert parsed["name"] is None
    assert parsed["phone"] is None
