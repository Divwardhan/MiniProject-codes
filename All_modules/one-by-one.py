import os
import subprocess

# --- Script Paths ---
ocr_script = r"C:\Users\asus\OneDrive\Desktop\NLP\MiniProject\All_modules\1_reading.py"
extract_debate_script = r"C:\Users\asus\OneDrive\Desktop\NLP\MiniProject\All_modules\2_cropping.py"
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

# --- Process session by session ---
for session in sessions:
    session_num = int(session.split("_")[1])
    if not (start_session_num <= session_num <= end_session_num):
        continue

    print(f"\n📘 Starting session: {session}")
    session_path = os.path.join(input_root, session)

    for root, dirs, files in os.walk(session_path):
        dir_name = os.path.basename(root)
        if not dir_name:
            continue

        for file in files:
            if not file.lower().endswith(".pdf") or "fullday" in file.lower():
                continue

            pdf_path = os.path.join(root, file)
            file_stem = os.path.splitext(file)[0]
            base_name = f"{dir_name}-{file_stem}_{session}"

            # Output file paths
            ocr_output = os.path.join(ocr_output_dir, f"{base_name}.txt")
            debate_output = os.path.join(debate_output_dir, f"{base_name}_debate.txt")
            cleaned_output = os.path.join(cleaned_output_dir, f"{base_name}_cleaned.txt")
            speeches_list_output = os.path.join(speeches_list_output_dir, f"{base_name}_speeches.json")
            final_output = os.path.join(final_output_dir, f"{base_name}_final.json")

            print("\n" + "=" * 100)
            print(f"📄 Processing file: {file}")
            print(f"📂 Directory: {dir_name}")
            print(f"📁 Session: {session}")
            print("=" * 100)

            try:
                # --- Step 1: OCR ---
                if not os.path.exists(ocr_output):
                    print("🔤 STEP 1: Performing OCR...")
                    result = subprocess.run(["python", ocr_script, pdf_path, ocr_output])
                    if result.returncode != 0:
                        raise Exception("OCR failed")
                else:
                    print("✅ OCR already done, skipping...")

                # --- Step 2: Debate Extraction ---
                if not os.path.exists(debate_output):
                    print("📝 STEP 2: Extracting debate content...")
                    result = subprocess.run(["python", extract_debate_script, ocr_output, debate_output])
                    if result.returncode != 0:
                        raise Exception("Debate extraction failed")
                else:
                    print("✅ Debate extraction already done, skipping...")

                # --- Step 3: Cleaning ---
                if not os.path.exists(cleaned_output):
                    print("🧹 STEP 3: Cleaning text...")
                    result = subprocess.run(["python", cleaner_script, debate_output, cleaned_output])
                    if result.returncode != 0:
                        raise Exception("Cleaning failed")
                else:
                    print("✅ Cleaning already done, skipping...")

                # --- Step 4: Speaker Segmentation ---
                if not os.path.exists(speeches_list_output):
                    print("👥 STEP 4: Segmenting speeches by speaker...")
                    result = subprocess.run(["python", speaker_wise_script, cleaned_output, speeches_list_output])
                    if result.returncode != 0:
                        raise Exception("Speaker segmentation failed")
                else:
                    print("✅ Speaker segmentation already done, skipping...")

                # --- Step 5: Object Creation ---
                if not os.path.exists(final_output):
                    print("🎯 STEP 5: Creating speech objects...")
                    result = subprocess.run(["python", object_making_script, speeches_list_output, final_output])
                    if result.returncode != 0:
                        raise Exception("Object creation failed")
                else:
                    print("✅ Object creation already done, skipping...")

                print("\n" + "=" * 100)
                print(f"🎉 SUCCESS! Completed pipeline for: {file}")
                print(f"📊 Final output: {final_output}")
                print("=" * 100 + "\n")

            except Exception as e:
                print(f"❌ ERROR: {e} for {file}, skipping to next...\n")
                continue

print("\n" + "🎉" * 40)
print("🎉 ALL ELIGIBLE PDFs PROCESSED SUCCESSFULLY! 🎉")
print("🎉" * 40)
