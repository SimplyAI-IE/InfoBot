from pathlib import Path
from backend.apps.concierge.ocr_cache import bulk_process_directory

def preload_concierge_assets():
    image_dir = Path(__file__).parent / "readImages"
    bulk_process_directory(image_dir)