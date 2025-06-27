import re

def preprocess_transcript(text):
    import re
    # Remove filler words and hesitations
    text = re.sub(r'\b(ehm|uh|um|ah)\b', '', text, flags=re.IGNORECASE)
    # Clean up multiple dots
    text = re.sub(r'\.{2,}', '.', text)
    # Remove orphaned commas after filler word removal
    text = re.sub(r',\s*,', ',', text)
    text = re.sub(r'\s*,\s*([.!?])', r'\1', text)  # Remove commas before punctuation
    text = re.sub(r'^\s*,\s*', '', text)  # Remove leading commas
    text = re.sub(r'\s*,\s*$', '', text)  # Remove trailing commas
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def preprocess_transcript_fixed(text):
    import re
    # Remove filler words and hesitations
    text = re.sub(r'\b(ehm|uh|um|ah)\b', '', text, flags=re.IGNORECASE)
    # Clean up multiple dots
    text = re.sub(r'\.{2,}', '.', text)
    # Remove commas that are left hanging after filler word removal
    text = re.sub(r',\s*,', ',', text)  # Multiple commas
    text = re.sub(r'\s*,\s*([.!?])', r'\1', text)  # Commas before punctuation
    text = re.sub(r'^\s*,\s*', '', text)  # Leading commas
    text = re.sub(r'\s*,\s*$', '', text)  # Trailing commas
    # Remove commas that appear after spaces where filler words were removed
    text = re.sub(r'(\w+),\s+(\w+)', r'\1 \2', text)  # Remove commas between words
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

raw_transcript = """
ehm... il paziente, uh, presenta dolori al petto... e, uh, difficoltà respiratorie.
La diagnosi... ehm... indica una possibile infezione polmonare.
"""

print("Original text:")
print(repr(raw_transcript))

print("\nWith current preprocessing:")
cleaned = preprocess_transcript(raw_transcript)
print(repr(cleaned))

print("\nWith improved preprocessing:")
cleaned_fixed = preprocess_transcript_fixed(raw_transcript)
print(repr(cleaned_fixed))

print("\nChecking target string:")
target = 'il paziente presenta dolori al petto'
print(f"Target: '{target}'")
print(f"Found in current: {target in cleaned}")
print(f"Found in fixed: {target in cleaned_fixed}")
