from pathlib import Path

from backend.apps.concierge.ocr_cache import bulk_process_directory


def preload_concierge_assets() -> None:
    image_dir = Path(__file__).parent / "readImages"
    bulk_process_directory(image_dir)


# Ensure it's called when you run the file directly
if __name__ == "__main__":
    preload_concierge_assets()
