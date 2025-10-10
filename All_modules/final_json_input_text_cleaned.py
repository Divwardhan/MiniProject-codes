"""
📜 Parliament Debate OCR → Clean JSON Pipeline (Hindi + English, Windows)
"""

from pdf2image import convert_from_path
import pytesseract
import re
import json
import unicodedata

# ======================================
# CONFIG PATHS
# ======================================
poppler_path = r"C:\poppler-25.07.0\poppler-25.07.0\Library\bin"
pdf_path = r"C:\Users\asus\Desktop\mini_project\mini_project.pdf"
ocr_output_path = r"C:\Users\asus\Desktop\mini_project\OCR_raw.txt"
tesseract_path = r"C:\Program Files\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = tesseract_path

# ======================================
# STEP 1: OCR PDF → Raw Text
# ======================================
def run_ocr(pdf_path, output_path):
    print("🔄 Converting PDF to images...")
    pages = convert_from_path(pdf_path, dpi=300, poppler_path=poppler_path)
    all_text = ""

    for i, page in enumerate(pages):
        print(f"🔍 OCR Processing page {i+1}/{len(pages)}...")
        text = pytesseract.image_to_string(page, lang="hin+eng")
        all_text += f"\n\n--- Page {i+1} ---\n\n{text.strip()}"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(all_text)
    print(f"✅ OCR complete! Text saved to:\n{output_path}")



def clean_text(text):
    # Remove page headers
    text = re.sub(r'--- Page \d+ ---', '', text)

    # Remove "Uncorrected/Not for publication" lines
    text = re.sub(r'Uncorrected/Not for publication[^\n]*', '', text, flags=re.IGNORECASE)

    # Remove code-like patterns: 3B/VNK, SCH-TDB/4.45/3K, (Contd. By kls/8m), etc.
    code_pattern = r'(\b[A-Z0-9\-]+(?:/[A-Z0-9\-\.]+)+\b|\(Contd\..*?\))'
    text = re.sub(code_pattern, '', text, flags=re.IGNORECASE)

    # Optional: normalize unicode
    text = unicodedata.normalize("NFKC", text)

    # Remove extra spaces & blank lines
    text = re.sub(r'\n\s*\n', '\n', text)
    text = re.sub(r'[ \t]+', ' ', text)

    return text.strip()



def segment_by_speaker(text, output_json):
    # Regex for Hindi + English speakers
    pattern = re.compile(
        r'(?P<speaker>('
        r'(?:श्री|सुश्री|श्रीमती|डॉ\.?|कुमारी)[^\n:]*\(?.*?\)?'  # Hindi
        r'|'
        r'(?:MR\.|MS\.|MRS\.|DR\.|PROF\.|SHRI|SHRIMATI|SMT\.|KUMARI)[A-Z\s\.]+(?:\([A-Z\s]+\))?'  # English
        r'))\s*[:\n]\s*'
        r'(?P<speech>.*?)(?=(?:\n(?:श्री|सुश्री|श्रीमती|डॉ\.?|कुमारी|MR\.|MS\.|MRS\.|DR\.|PROF\.|SHRI|SHRIMATI|SMT\.|KUMARI))|$)',
        re.DOTALL | re.IGNORECASE
    )

    speeches = []
    for m in pattern.finditer(text):
        speaker = m.group("speaker").strip()
        speech = m.group("speech").strip()
        if speech:
            speeches.append({"speaker": speaker, "speech": speech})

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(speeches, f, ensure_ascii=False, indent=4)

    print(f"✅ Extracted {len(speeches)} speeches → {output_json}")
    return speeches


if __name__ == "__main__":
    # 1️⃣ OCR
    run_ocr(pdf_path, ocr_output_path)

    # 2️⃣ Read OCR text & clean
    with open(ocr_output_path, "r", encoding="utf-8") as f:
        raw_text = f.read()
    cleaned_text = clean_text(raw_text)

    # Save cleaned text (optional)
    cleaned_text_path = "OCR_cleaned.txt"
    with open(cleaned_text_path, "w", encoding="utf-8") as f:
        f.write(cleaned_text)
    print(f"✅ Cleaned text saved → {cleaned_text_path}")

    # 3️⃣ Segment by speaker & save JSON
    speeches = segment_by_speaker(cleaned_text, "speecheeees_cleaned.json")
    print("\n🎉 FULL PIPELINE COMPLETE — Output file: speeches_cleaned.json")
