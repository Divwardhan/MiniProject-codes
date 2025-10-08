# ================================================
# STEP 1: READ & SEGMENT PARLIAMENT DEBATE BY SPEAKER
# ================================================

import re
import json
# Path to your uploaded file
file_path = "cleaned_v2.txt"

# Read the text file
with open(file_path, "r", encoding="utf-8") as f:
    raw_text = f.read()

print("✅ File loaded successfully.")
print(f"Total characters: {len(raw_text)}")

# -----------------------------------------------
# Detect and split by speaker names
# Speaker markers typically look like:
# "श्री", "सुश्री", "श्रीमती", "MR.", "SHRI", etc.
# -----------------------------------------------

# Use regex to split speeches by these markers (while keeping the speaker name)
segments = re.split(r"\n(?=(?:श्री|सुश्री|श्रीमती|MR\.|SHRI|MS\.))", raw_text)

# Remove extra whitespace and filter out tiny fragments
speeches = [seg.strip() for seg in segments if len(seg.strip().split()) > 5]

print(f"✅ Extracted {len(speeches)} speeches.")

# Preview a few
for i, s in enumerate(speeches[:3]):
    print(f"\n--- Speech {i+1} ---\n{s[:400]}...\n")


with open("speeches-list2.json","w",encoding="utf-8") as f:
    json.dump(speeches, f, ensure_ascii=False, indent=4)
    

