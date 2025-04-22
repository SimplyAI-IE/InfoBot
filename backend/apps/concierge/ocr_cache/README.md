# 🗂️ OCR Cache

This directory stores the **cached text outputs** generated from OCR-processed images.

---

## 📌 Purpose

- When images are placed in the `readImages/` folder, they are processed by Tesseract OCR.
- The extracted text is saved here to avoid redundant OCR passes on the same files.

---

## ⚠️ Do Not Version Control

This folder should be **excluded from Git**. Cached OCR output is transient and should not be committed.

Ensure `.gitignore` includes:

