# ================================================
# STEP 1: READ & SEGMENT PARLIAMENT DEBATE BY SPEAKER
# ================================================

# ✅ Usage:
# python 4_speaker_wise.py "input.txt" "output.json"

import sys
import os
import re
import json

def segment_speeches(file_path, output_path):
    try:
        # Check input file
        if not os.path.exists(file_path):
            print(f"❌ Error: Input file not found: {file_path}")
            return
        
        print(f"🔄 Reading file: {file_path}")
        # Read the text file
        with open(file_path, "r", encoding="utf-8") as f:
            raw_text = f.read()

        print("✅ File loaded successfully.")
        print(f"📊 Total characters: {len(raw_text)}")

        # -----------------------------------------------
        # Detect and split by speaker names
        # Speaker markers typically look like:
        # "श्री", "सुश्री", "श्रीमती", "MR.", "SHRI", etc.
        # -----------------------------------------------
        print("🔍 Segmenting speeches by speaker markers...")
        
        # Use regex to split speeches by these markers (while keeping the speaker name)
        segments = re.split(r"\n(?=(?:श्री|सुश्री|श्रीमती|MR\.|SHRI|MS\.))", raw_text)

        # Remove extra whitespace and filter out tiny fragments
        speeches = [seg.strip() for seg in segments if len(seg.strip().split()) > 5]

        print(f"✅ Extracted {len(speeches)} speeches.")

        # Preview a few
        print("\n📝 Preview of first 3 speeches:")
        for i, s in enumerate(speeches[:3]):
            print(f"\n--- Speech {i+1} ---")
            print(f"{s[:400]}...")
            print()

        # Save to JSON
        print(f"💾 Saving speeches to: {output_path}")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(speeches, f, ensure_ascii=False, indent=4)
        
        print(f"✅ Done! Speeches saved to:\n{output_path}")

    except Exception as e:
        print(f"❌ Error during speech segmentation: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("⚠️ Usage: python 4_speaker_wise.py <input_txt_path> <output_json_path>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    segment_speeches(input_file, output_file)