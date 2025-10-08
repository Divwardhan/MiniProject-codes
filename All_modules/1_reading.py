from pdf2image import convert_from_path
import pytesseract
from PIL import Image
import os

# Paths
poppler_path = r"C:\Users\asus\AppData\Local\Microsoft\WinGet\Packages\oschwartz10612.Poppler_Microsoft.Winget.Source_8wekyb3d8bbwe\poppler-25.07.0\Library\bin"
pdf_path = r"C:\Users\asus\OneDrive\Desktop\NLP\MiniProject\Fullday.pdf"
output_path = r"C:\Users\asus\OneDrive\Desktop\NLP\MiniProject\Fullday_OCR.txt"

tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
# Configure Tesseract
pytesseract.pytesseract.tesseract_cmd = tesseract_path

try:
    # Convert PDF to images
    print("🔄 Converting PDF to images...")
    pages = convert_from_path(pdf_path, dpi=300, poppler_path=poppler_path)

    all_text = ""
    for i, page in enumerate(pages):
        print(f"🔍 Processing page {i+1}/{len(pages)}...")
        # OCR in Hindi + English
        text = pytesseract.image_to_string(page, lang="hin+eng")
        all_text += f"\n\n--- Page {i+1} ---\n\n{text.strip()}"

    # Save output
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(all_text)

    print(f"✅ OCR complete! Text saved to:\n{output_path}")

except Exception as e:
    print("❌ Error during OCR:", e)