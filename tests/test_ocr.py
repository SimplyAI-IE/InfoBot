from pathlib import Path
from backend.apps.concierge.ocr_cache import get_cached_ocr_text

def test_ocr_extraction_from_image():
    image_path = Path("backend/apps/concierge/readImages/174606224_4210921648970816_8591224770352466204_n.jpg")
    text = get_cached_ocr_text(image_path)
    assert isinstance(text, str)
    assert len(text) > 50  # ensure some real content
    assert "soup" in text.lower() or "starter" in text.lower()
