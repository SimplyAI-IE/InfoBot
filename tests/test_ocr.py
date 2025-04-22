from pathlib import Path
from apps.concierge.ocr_cache import get_cached_ocr_text
import pytest


def test_ocr_extraction_from_image():
    image_path = Path("tests/test_assets/test_image.png")
    if not image_path.exists():
        pytest.skip("OCR test skipped: test image not found.")

    text = get_cached_ocr_text(image_path)
    assert "selection of cereals" in text.lower()
