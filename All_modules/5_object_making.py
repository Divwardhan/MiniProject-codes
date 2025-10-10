# ==========================================================
# FIXED: Accurate Speaker Extraction with Colon Handling
# ==========================================================

# ✅ Usage:
# python 5_object_making.py "input.json" "output.json"

import sys
import os
import re
import unicodedata
import json

DEV = r"\u0900-\u097F"


def fix_hindi_spacing_v2(text):
    """
    Correct spacing issues in Hindi text while keeping normal spaces intact.
    """
    # Remove multiple dots / ellipses
    text = re.sub(r"\.{2,}", ".", text)

    # Split into tokens by space
    tokens = text.split()
    fixed_tokens = []
    buffer = []

    for tok in tokens:
        # If token is single Hindi letter, it's likely OCR split
        if re.fullmatch(rf"[{DEV}]", tok):
            buffer.append(tok)
        else:
            if buffer:
                fixed_tokens.append("".join(buffer))
                buffer = []
            fixed_tokens.append(tok)
    if buffer:
        fixed_tokens.append("".join(buffer))

    text = " ".join(fixed_tokens)

    # Fix Hindi + English boundaries
    text = re.sub(rf"([{DEV}])([A-Za-z0-9])", r"\1 \2", text)
    text = re.sub(rf"([A-Za-z0-9])([{DEV}])", r"\1 \2", text)

    # Fix spaces before punctuation
    text = re.sub(rf"\s+([.,।?!])", r"\1", text)
    # Ensure space after punctuation if missing
    text = re.sub(r"([।?!,\.])([^\s])", r"\1 \2", text)

    # Normalize multiple spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text


def extract_speaker_clean_v2(text):
    """
    Extract speaker and clean speech text with proper colon handling.
    """
    
    # Replace all | with I
    text = text.replace("|", "I")
    
    # Normalize Unicode and remove leading dots/spaces
    text = unicodedata.normalize("NFKC", text).strip()
    text = re.sub(r"^\.+", "", text)

    speaker = "Unknown"
    speech_text = text

    # STRATEGY 1: Check for colon separator first (most reliable)
    if ":" in text:
        parts = text.split(":", 1)
        potential_speaker = parts[0].strip()
        
        # Validate if it looks like a speaker name (not too long, has name-like pattern)
        if len(potential_speaker) < 100 and (
            re.search(r"[A-Z]{2,}", potential_speaker) or  # All-caps words (MR., SHRI, etc.)
            re.search(rf"[{DEV}]", potential_speaker)  # Contains Hindi characters
        ):
            speaker = potential_speaker
            speech_text = parts[1].strip()
    
    # STRATEGY 2: If no colon, try pattern matching
    else:
        # Enhanced speaker regex covering more cases
        speaker_patterns = [
            # Hindi titles
            rf"^(श्री|सुश्री|श्रीमती|डॉ\.?|कुमारी)\s+([{DEV}\s]+?)(?=\s*:|\s*$)",
            # English titles with names (including ALL CAPS)
            r"^(MR\.|MS\.|MRS\.|DR\.|PROF\.|SHRI|SHRIMATI|SMT\.|KUMARI)\s+([A-Z][A-Za-z\s\.]+?)(?=\s*:|\s*$)",
            # Just names in caps (like "SHRIMATI JAYA BACHCHAN")
            r"^([A-Z][A-Z\s\.]+?)(?=\s*:|\s*$)",
        ]
        
        for pattern in speaker_patterns:
            match = re.match(pattern, text, flags=re.IGNORECASE)
            if match:
                speaker = match.group(0).strip()
                speech_text = text[len(speaker):].strip()
                # Remove leading colon if present
                speech_text = re.sub(r"^:\s*", "", speech_text)
                break

    # --- Clean the speech text ---
    # Remove ellipses or long dot chains
    speech_text = re.sub(r"\.{2,}", " ", speech_text)

    # Remove procedural noise
    procedural_patterns = [
        r"honou?rable\s+speaker", r"madam\s+speaker", r"mr\.?\s+deputy\s+chairman",
        r"mr\.?\s+chairman", r"\(applause\)", r"\(laughter\)", r"thank\s+you", r"\(order\)",
        r"hear\s+hear", r"\(expunged\)", r"\(interruptions\)", r"\(व्यवधान\)"
    ]
    for p in procedural_patterns:
        speech_text = re.sub(p, " ", speech_text, flags=re.IGNORECASE)

    # Keep only Hindi/English letters + punctuation
    speech_text = re.sub(rf"[^A-Za-z{DEV}\s.,?!।]", " ", speech_text)
    
    # Fix Hindi spacing
    speech_text = fix_hindi_spacing_v2(speech_text)
    
    # Normalize spaces
    speech_text = re.sub(r"\s+", " ", speech_text).strip()

    return {"speaker": speaker, "speech": speech_text}


def process_speeches(input_path, output_path):
    try:
        # Check input file
        if not os.path.exists(input_path):
            print(f"❌ Error: Input file not found: {input_path}")
            return
        
        print(f"🔄 Reading speeches from: {input_path}")
        with open(input_path, "r", encoding="utf-8") as f:
            speeches = json.load(f)
        
        print(f"✅ Loaded {len(speeches)} speeches.")
        
        # --- Apply to all speeches ---
        print("🔍 Extracting speaker information and cleaning speeches...")
        speech_objects = []
        for s in speeches:
            if len(s.strip()) > 10:
                obj = extract_speaker_clean_v2(s)
                # Only add if we got meaningful content
                if obj["speech"]:
                    speech_objects.append(obj)

        print(f"✅ Extracted {len(speech_objects)} speech objects.")
        print("\n" + "="*70)
        print("📝 SAMPLE OUTPUT:")
        print("="*70)

        for i, obj in enumerate(speech_objects[:8], 1):
            print(f"\n{i}. 🎙️ Speaker: {obj['speaker']}")
            print(f"   🗣️ Speech: {obj['speech'][:200]}...")
            print("-" * 70)

        # Save to file
        print(f"\n💾 Saving speech objects to: {output_path}")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(speech_objects, f, ensure_ascii=False, indent=4)

        print(f"✅ Done! Speech objects saved to:\n{output_path}")

    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in input file: {e}")
    except Exception as e:
        print(f"❌ Error during speech processing: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("⚠️ Usage: python 5_object_making.py <input_json_path> <output_json_path>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    process_speeches(input_file, output_file)