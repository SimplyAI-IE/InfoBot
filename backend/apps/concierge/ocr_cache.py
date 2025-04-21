from pathlib import Path
from PIL import Image
import pytesseract
from pathlib import Path
from typing import Any

OCR_CACHE_DIR = Path(__file__).resolve().parent / "ocr_cache"
OCR_CACHE_DIR.mkdir(parents=True, exist_ok=True)

def bulk_process_directory(image_dir: Path) -> None:
    for image_path in sorted(image_dir.glob("*.jpg")):
        _ = get_cached_ocr_text(image_path)


def get_cached_ocr_text(image_path: Path) -> str:
    txt_path = OCR_CACHE_DIR / (image_path.stem + ".txt")

    if txt_path.exists():
        return txt_path.read_text(encoding="utf-8")

    image = Image.open(image_path)
    raw_text = pytesseract.image_to_string(image)

    txt_path.write_text(raw_text, encoding="utf-8")
    return raw_text
