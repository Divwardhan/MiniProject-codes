import os
import json
import re
import pandas as pd

def extract_date_time(filename):
    """
    Extract date and time from filenames like:
    2008-02-25-11.00amTo12.00Noon_session_213_final.json
    """
    # Match pattern like 2008-02-25-11.00amTo12.00Noon
    match = re.search(r'(\d{4}-\d{2}-\d{2})-(\d{1,2}\.\d{2}\s?(?:am|pm|AM|PM))', filename)
    if match:
        date = match.group(1)
        time = match.group(2).replace(".", ":").upper().replace(" ", "")
        return date, time
    else:
        return None, None


def collect_jsons(root_dir):
    """
    Recursively collect all JSONs, attach date/time from filenames,
    and skip unwanted speakers.
    """
    unwanted_speakers = {
        "mr. chairman", "chairman", "unknown",
        "mr. deputy chairman", "shri up-sabhapati",
        "श्री उपसभापति", "अध्यक्ष", "सभापति"
    }

    all_records = []

    # Walk through all directories
    for dirpath, _, filenames in os.walk(root_dir):
        for fname in filenames:
            if fname.endswith(".json"):
                fpath = os.path.join(dirpath, fname)
                date, time = extract_date_time(fname)
                if not date:
                    continue  # skip files without valid date/time

                try:
                    with open(fpath, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    for entry in data:
                        speaker = str(entry.get("speaker", "")).strip()
                        speech = str(entry.get("speech", "")).strip()

                        # skip empty or unwanted speakers
                        if not speech:
                            continue
                        if any(sp in speaker.lower() for sp in unwanted_speakers):
                            continue

                        all_records.append({
                            "date": date,
                            "time": time,
                            "speaker": speaker,
                            "speech": speech
                        })
                except Exception as e:
                    print(f"❌ Error in {fpath}: {e}")

    df = pd.DataFrame(all_records)
    return df


if __name__ == "__main__":
    input_dir = r"C:\Users\asus\OneDrive\Desktop\NLP\MiniProject\OCR_Outputs\5_speech_objects"
    df = collect_jsons(input_dir)
    print(f"\n✅ Total valid speeches collected: {len(df)}")

    output_file = "compiled_speeches.csv"
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"📁 Saved compiled data to {output_file}")
