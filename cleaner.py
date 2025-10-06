# cleaner_v2.py
# Safe cleaning for parliamentary transcript-like text.
# - Preserves line breaks (keeps same number of lines).
# - Removes slash/dash technical markers, page-number-only lines, and interrupt-noise like ...(Interruptions)...
# - Keeps English names / normal uppercase names intact.

import re
from pathlib import Path

# ---- CONFIG: change these paths if needed ----
INPUT_PATH = Path("cleaned_parliament_2016_8_3_11-12.txt")
OUTPUT_PATH = Path("cleaned_parliament_2016_8_3_11-12.cleaned_v2.txt")
# ---------------------------------------------

# compile regexes once
RE_PAREN_WITH_SLASH = re.compile(r'\([^)]*\/[^)]*\)', flags=re.UNICODE)   # remove ( ... / ... )
RE_HYPHEN_SLASH_FRAGMENT = re.compile(
    r'-\s*(?:[A-Za-z0-9]+(?:\s*[-/]\s*[A-Za-z0-9\.]+)+(?:\s*[-/]\s*[A-Za-z0-9\.]+)*)',
    flags=re.UNICODE)   # remove -.../... fragments
# remove any substring (up to a reasonable length) that contains at least one slash
RE_ANY_CONTAIN_SLASH = re.compile(r'[A-Za-z0-9\-\./\s]{0,120}\/[A-Za-z0-9\-\./\s]{0,120}', flags=re.UNICODE)

# remove dotted noise patterns like ...(Interruptions)... or ...(व्यवधान)...
RE_DOTTED_NOISE = re.compile(r'\.{2,}\s*\(?\s*(Interruptions|व्यवधान)\s*\)?\s*\.{0,}', flags=re.IGNORECASE | re.UNICODE)
# small parenthetical acronyms/noise to strip if they appear alone in parenthesis
RE_SMALL_PARENS_NOISE = re.compile(
    r'\(\s*(?:AIA|AIM|HK/C|HK-SC|HK/SC|KSK/D|Contd\.?|Contd|Contd by|Ends\.)\s*\)',
    flags=re.IGNORECASE | re.UNICODE)

# collapse many dots to an ellipsis (choice: change '...' to ' ' if you prefer removal)
RE_MANY_DOTS = re.compile(r'\.{3,}', flags=re.UNICODE)

# detect page-number-only lines (keep a blank line in output to preserve line count)
RE_PAGE_NUMBER = re.compile(r'^\s*\*?\d+\s*$')

# helper: collapse repeated identical word sequences like "and and" -> "and"
RE_DUP_WORDS = re.compile(r'\b(\w+)(?:\s+\1\b)+', flags=re.IGNORECASE)

# optional: remove leftover long tokens that are mostly punctuation (conservative)
RE_LONG_GARBAGE = re.compile(r'[^\w\s]{6,}', flags=re.UNICODE)


def clean_line_preserve_breaks(line: str) -> str:
    """
    Clean a single line and return the cleaned text (without newline).
    If function returns empty string, caller will write a blank line to preserve line count.
    """
    s = line  # do not strip newline here (caller supplies line content without trailing newline)
    # 1) quick removal of parenthetical sequences that contain slashes
    s = RE_PAREN_WITH_SLASH.sub('', s)

    # 2) fragments that start with hyphen and include slashes/dashes
    s = RE_HYPHEN_SLASH_FRAGMENT.sub('', s)

    # 3) robust: remove any contiguous substring that contains a '/' (covers spaced variants)
    s = RE_ANY_CONTAIN_SLASH.sub('', s)

    # 4) remove the noisy dotted parenthetical patterns like ...(Interruptions)...
    s = RE_DOTTED_NOISE.sub('', s)

    # 5) remove some short parenthetical acronyms/noise we commonly see
    s = RE_SMALL_PARENS_NOISE.sub('', s)

    # 6) collapse extremely long runs of dots into a single ellipsis (keeps readability)
    s = RE_MANY_DOTS.sub('...', s)

    # 7) collapse duplicate adjacent words (e.g. "and and")
    s = RE_DUP_WORDS.sub(r'\1', s)

    # 8) remove long punctuation-only garbage (conservative: only sequences of punctuation)
    #     keep words/letters; this targets lines like "----- ) ## // ///" etc.
    def _long_garbage_repl(m):
        token = m.group(0)
        # measure proportion of letters (incl. Devanagari) vs punctuation
        letters = re.findall(r'[A-Za-z\u0900-\u097F\u00C0-\u024F0-9]', token)
        if len(letters) / max(1, len(token)) < 0.25:
            return ''
        return token  # otherwise keep
    s = RE_LONG_GARBAGE.sub(_long_garbage_repl, s)

    # 9) tidy whitespace (but do not remove newline; caller handles it)
    s = re.sub(r'[ \t]{2,}', ' ', s).strip()

    return s


def clean_file(input_path: Path, output_path: Path):
    with input_path.open('r', encoding='utf-8') as inf:
        lines = inf.readlines()  # preserves line count and newline characters

    out_lines = []
    for raw in lines:
        # raw includes trailing '\n' except possibly last line; remove it for processing but remember newline
        has_nl = raw.endswith('\n')
        line_body = raw[:-1] if has_nl else raw

        # preserve exact number of lines: if a page-number-only line, output a blank line (i.e. '\n')
        if RE_PAGE_NUMBER.match(line_body):
            out_lines.append('\n')
            continue

        cleaned = clean_line_preserve_breaks(line_body)

        # if cleaned is empty, write a blank line so line count stays same
        if cleaned == '':
            out_lines.append('\n')
        else:
            out_lines.append(cleaned + ('\n' if has_nl else ''))

    # write output
    with output_path.open('w', encoding='utf-8') as outf:
        outf.writelines(out_lines)

    print("✅ Done. Cleaned file saved to:", output_path)


if __name__ == "__main__":
    # run
    clean_file(INPUT_PATH, OUTPUT_PATH)
