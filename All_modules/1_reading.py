import sys
import os
from pdf2image import convert_from_path
import pytesseract
from PIL import Image

# ✅ Usage:
# python ocr_script.py "input.pdf" "output.txt"

# --- Configuration ---
poppler_path = r"C:\Users\asus\AppData\Local\Microsoft\WinGet\Packages\oschwartz10612.Poppler_Microsoft.Winget.Source_8wekyb3d8bbwe\poppler-25.07.0\Library\bin"
tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = tesseract_path

def perform_ocr(input_pdf, output_txt):
    try:
        # Check input file
        if not os.path.exists(input_pdf):
            print(f"❌ Error: Input file not found: {input_pdf}")
            return
        
        # Convert PDF to images
        print("🔄 Converting PDF to images...")
        pages = convert_from_path(input_pdf, dpi=300, poppler_path=poppler_path)

        all_text = ""
        for i, page in enumerate(pages):
            print(f"🔍 Processing page {i+1}/{len(pages)}...")
            text = pytesseract.image_to_string(page, lang="hin+eng")
            all_text += f"\n\n--- Page {i+1} ---\n\n{text.strip()}"

        # Save output
        with open(output_txt, "w", encoding="utf-8") as f:
            f.write(all_text)

        print(f"✅ OCR complete! Text saved to:\n{output_txt}")

    except Exception as e:
        print("❌ Error during OCR:", e)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("⚠️ Usage: python ocr_script.py <input_pdf_path> <output_txt_path>")
        sys.exit(1)
    
    input_pdf = sys.argv[1]
    output_txt = sys.argv[2]
    
    perform_ocr(input_pdf, output_txt)
