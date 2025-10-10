import os
import subprocess

# --- Script Paths ---
ocr_script = r"C:\Users\asus\OneDrive\Desktop\NLP\MiniProject\All_modules\1_reading.py"
extract_debate_script = r"C:\Users\asus\OneDrive\Desktop\NLP\MiniProject\All_modules\2_extract_debate.py"
cleaner_script = r"C:\Users\asus\OneDrive\Desktop\NLP\MiniProject\All_modules\3_cleaner.py"
speaker_wise_script = r"C:\Users\asus\OneDrive\Desktop\NLP\MiniProject\All_modules\4_speaker_wise.py"
object_making_script = r"C:\Users\asus\OneDrive\Desktop\NLP\MiniProject\All_modules\5_object_making.py"

# --- Input/Output Paths ---
input_root = r"C:\Users\asus\OneDrive\Desktop\DataScrapping\downloads"
output_root = r"C:\Users\asus\OneDrive\Desktop\NLP\MiniProject\OCR_Outputs"

# --- Create intermediate directories ---
ocr_output_dir = os.path.join(output_root, "1_ocr")
debate_output_dir = os.path.join(output_root, "2_debate_extracted")
cleaned_output_dir = os.path.join(output_root, "3_cleaned")
speeches_list_output_dir = os.path.join(output_root, "4_speeches_list")
final_output_dir = os.path.join(output_root, "5_speech_objects")

for dir_path in [
    ocr_output_dir, debate_output_dir, cleaned_output_dir,
    speeches_list_output_dir, final_output_dir
]:
    os.makedirs(dir_path, exist_ok=True)

# --- Choose session range ---
start_session_num = int(input("🔢 Enter the starting session number (e.g., 210): "))
end_session_num = int(input("🔢 Enter the ending session number (e.g., 230): "))

# --- Sort sessions numerically ---
sessions = sorted(
    [d for d in os.listdir(input_root) if d.startswith("session_")],
    key=lambda x: int(x.split("_")[1])
)

total_sessions = len([s for s in sessions if start_session_num <= int(s.split("_")[1]) <= end_session_num])
current_session_index = 0

# --- Walk through sessions ---
for session in sessions:
    session_num = int(session.split("_")[1])

    # Skip sessions outside the range
    if session_num < start_session_num or session_num > end_session_num:
        continue

    current_session_index += 1
    print(f"\n📘 Processing session {session_num} ({current_session_index}/{total_sessions})")

    session_path = os.path.join(input_root, session)

    # Walk through all subfolders under this session
    for root, dirs, files in os.walk(session_path):
        dir_name = os.path.basename(root)
        if not dir_name:
            continue

        for file in files:
            if file.lower().endswith(".pdf") and "fullday" not in file.lower():
                pdf_path = os.path.join(root, file)

                # Generate base filename
                file_stem = os.path.splitext(file)[0]
                base_name = f"{dir_name}-{file_stem}_{session}"

                # Define all intermediate file paths
                ocr_output = os.path.join(ocr_output_dir, f"{base_name}.txt")
                debate_output = os.path.join(debate_output_dir, f"{base_name}_debate.txt")
                cleaned_output = os.path.join(cleaned_output_dir, f"{base_name}_cleaned.txt")
                speeches_list_output = os.path.join(speeches_list_output_dir, f"{base_name}_speeches.json")
                final_output = os.path.join(final_output_dir, f"{base_name}_final.json")

                print("=" * 90)
                print(f"📄 Processing file: {file}")
                print(f"📁 Session: {session}")
                print(f"📂 Directory: {dir_name}")
                print("=" * 90)

                # --- Step 1: OCR ---
                print("\n🔤 STEP 1: Performing OCR...")
                result = subprocess.run(["python", ocr_script, pdf_path, ocr_output])
                if result.returncode != 0:
                    print(f"❌ OCR failed for {pdf_path}, skipping...\n")
                    continue

                # --- Step 2: Extract Debate ---
                print("\n📝 STEP 2: Extracting debate content...")
                result = subprocess.run(["python", extract_debate_script, ocr_output, debate_output])
                if result.returncode != 0:
                    print(f"❌ Debate extraction failed for {ocr_output}, skipping...\n")
                    continue

                # --- Step 3: Clean Text ---
                print("\n🧹 STEP 3: Cleaning text...")
                result = subprocess.run(["python", cleaner_script, debate_output, cleaned_output])
                if result.returncode != 0:
                    print(f"❌ Cleaning failed for {debate_output}, skipping...\n")
                    continue

                # --- Step 4: Segment by Speaker ---
                print("\n👥 STEP 4: Segmenting speeches by speaker...")
                result = subprocess.run(["python", speaker_wise_script, cleaned_output, speeches_list_output])
                if result.returncode != 0:
                    print(f"❌ Speaker segmentation failed for {cleaned_output}, skipping...\n")
                    continue

                # --- Step 5: Create Speech Objects ---
                print("\n🎯 STEP 5: Creating speech objects...")
                result = subprocess.run(["python", object_making_script, speeches_list_output, final_output])
                if result.returncode != 0:
                    print(f"❌ Object creation failed for {speeches_list_output}, skipping...\n")
                    continue

                print("\n" + "=" * 90)
                print(f"✅ SUCCESS! Pipeline completed for: {file}")
                print(f"📊 Final output saved to: {final_output}")
                print("=" * 90 + "\n")

print("\n" + "🎉" * 40)
print("🎉 ALL ELIGIBLE PDFs PROCESSED SUCCESSFULLY! 🎉")
print("🎉" * 40)

print("\n📁 Output directories:")
print(f"   1️⃣ OCR outputs: {ocr_output_dir}")
print(f"   2️⃣ Debate extracts: {debate_output_dir}")
print(f"   3️⃣ Cleaned texts: {cleaned_output_dir}")
print(f"   4️⃣ Speech lists: {speeches_list_output_dir}")
print(f"   5️⃣ Final speech objects: {final_output_dir}")
