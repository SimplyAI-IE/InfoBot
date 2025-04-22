from pathlib import Path
from PIL import Image
import pytesseract


OCR_CACHE_DIR = Path(__file__).parent / "ocr_cache"


def bulk_process_directory(input_dir: Path) -> None:
    from .ocr_engine import ocr_image  # Assuming this exists

    OCR_CACHE_DIR.mkdir(exist_ok=True)

    for image_path in input_dir.glob("*.*"):
        try:
            text = ocr_image(image_path)
            cache_path = OCR_CACHE_DIR / f"{image_path.stem}.txt"
            cache_path.write_text(text, encoding="utf-8")
        except Exception as e:
            print(f"Failed to OCR {image_path.name}: {e}")


OCR_CACHE_DIR = Path(__file__).resolve().parent / "ocr_cache"
OCR_CACHE_DIR.mkdir(parents=True, exist_ok=True)


def get_cached_ocr_text(image_path: Path) -> str:
    txt_path = OCR_CACHE_DIR / (image_path.stem + ".txt")

    if txt_path.exists():
        return txt_path.read_text(encoding="utf-8")

    image = Image.open(image_path)
    raw_text = pytesseract.image_to_string(image)

    txt_path.write_text(raw_text, encoding="utf-8")
    return raw_text
