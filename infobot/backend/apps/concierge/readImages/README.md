# readImages

This folder stores uploaded or manually added images (JPG, PNG, etc.) intended for OCR processing.

## Expected Use

- Restaurant menus
- Timetables
- Visual information shared via social or staff

⚠️ Not all images here are guaranteed to be menu content.

## Behavior

On app startup:
- All `.jpg` files are OCR-processed (if not already cached)
- Text is saved in `ocr_cache/`
