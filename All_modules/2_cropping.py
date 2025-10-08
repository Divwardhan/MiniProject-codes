import re

def extract_debate(file_path, output_path):
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Find the first interruption
    interruption_match = re.search(r"\(Interruptions\)|\(व्यवधान\)", text)
    
    if interruption_match:
        first_interrupt_pos = interruption_match.start()

        # Trace backward to find the last "(Ends)" or "समाप्त" before this
        pre_text = text[:first_interrupt_pos]
        last_end_match = list(re.finditer(r"\(Ends\)|समाप्त", pre_text))
        if last_end_match:
            start_pos = last_end_match[-1].end()
        else:
            start_pos = 0  # fallback to start if no end marker found

        # Extract debate text
        debate_text = text[start_pos:].strip()
    else:
        # fallback: entire text if no interruptions
        debate_text = text.strip()

    # Optional: remove page headers
    debate_text = re.sub(r"--- Page.*---", "", debate_text)
    debate_text = re.sub(r"Uncorrected.*\n", "", debate_text)

    # Remove interruption markers from debate
    debate_text = re.sub(r"\(Interruptions\)|\(व्यवधान\)", "", debate_text)

    # Remove extra blank lines
    debate_text = re.sub(r"\n\s*\n", "\n\n", debate_text)

    # Save cleaned debate
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(debate_text.strip())

    print(f"Debate extracted to {output_path}")

# Example usage
if __name__ == "__main__":
    extract_debate(r"..\Fullday_OCR.txt", r"cleaned.txt")
