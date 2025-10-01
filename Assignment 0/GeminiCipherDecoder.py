import string
from collections import Counter

# --- Configuration Section ---

# 1. Paste your CIPHERTEXT here
CIPHERTEXT = """
WUOCWCIML FZOC IZVVZMXOCL. MFCR MCBB LMUVXCL,
ACDZNLC MFCR ZVC IUM GNLM ZAUNM VCZVVZIEXIE
CDUIUWXDL ZIY JUBXMXDL. MFCR ZBLU VCZVVZIEC WCZIXIE.
ZIY MFCR’VC IUM GNLM ZAUNM VCYXLMVXANMXIE MFC EUUYL.
MFCR’VC ZAUNM TXENVXIE UNM PFZM XL EUUY.
"""

# Standard English letter frequencies (approximate order from E to Z)
# This is used to map the most frequent cipher letters to the most frequent plaintext letters.
ENGLISH_FREQUENCY_ORDER = "ETAOINSHRDLCUMWFGYPBVKJXQZ"

# =========================================================

def analyze_and_match(ciphertext, english_order):
    """
    Calculates letter frequencies, creates a best-guess key, and decrypts.
    """
    # 1. Clean the text (uppercase, keep only letters for analysis)
    cleaned_text = ''.join(filter(str.isalpha, ciphertext.upper()))
    total_letters = len(cleaned_text)

    if total_letters == 0:
        return None, "Error: No letters found in the ciphertext.", {}

    # 2. Count the occurrences of each letter
    counts = Counter(cleaned_text)
    
    # Sort ciphertext letters by descending frequency
    # We use list(set(string.ascii_uppercase)) to ensure all 26 letters are present, 
    # even if they have a count of 0, for a full key generation.
    cipher_letters_sorted = sorted(
        counts.keys(), 
        key=lambda k: counts[k], 
        reverse=True
    )
    
    # 3. Create the Best-Guess Decryption Key (Cipher -> Plain)
    decryption_key = {}
    
    # We use the length of the English order to ensure we only map the letters needed.
    for i in range(min(len(cipher_letters_sorted), len(english_order))):
        cipher_char = cipher_letters_sorted[i]
        plain_char = english_order[i]
        decryption_key[cipher_char] = plain_char

    # 4. Generate the Decryption Table
    # The key needs to be completed for the translation to work, 
    # but we only use the derived key above for the actual guess.
    full_decryption_key = {
        **{c: p for c, p in decryption_key.items()},
        # Ensure all other characters (punctuation, spaces) are also mapped to themselves
        **{char: char for char in set(ciphertext) if char not in decryption_key}
    }
    
    decryption_table = str.maketrans(full_decryption_key)

    # 5. Decrypt the message
    plaintext_guess = ciphertext.upper().translate(decryption_table)

    # 6. Prepare the analysis display
    analysis = []
    for i, cipher_char in enumerate(cipher_letters_sorted):
        count = counts[cipher_char]
        percentage = (count / total_letters) * 100
        plain_char = decryption_key.get(cipher_char, '?')
        
        analysis.append({
            'cipher': cipher_char,
            'count': count,
            'percent': f"{percentage:.2f}%",
            'guess': plain_char
        })

    return plaintext_guess, cleaned_text, analysis, decryption_key

# --- Execute Analysis ---
print("Running Frequency Analysis and Initial Decryption Guess...")

decrypted_guess, full_text, analysis_data, key_guess = analyze_and_match(CIPHERTEXT, ENGLISH_FREQUENCY_ORDER)

# --- Display Results ---

# Display the frequency table
print("\n" + "=" * 60)
print("             STATISTICAL FREQUENCY ANALYSIS TABLE")
print(f"Total Letters Analyzed: {len(full_text)}")
print("=" * 60)
print(f"| {'Cipher Letter':<15} | {'Count':<5} | {'Percent':<7} | {'Initial Guess':<15} |")
print("-" * 60)

for data in analysis_data:
    print(f"| {data['cipher']:<15} | {data['count']:<5} | {data['percent']:<7} | {data['guess']:<15} |")

print("=" * 60)

# Display the key used
print("\n--- Best-Guess Decryption Key (Cipher -> Plain) ---")
print(key_guess)
print("-" * 60)

# Display the decryption guess
print("\n--- Initial Decryption Attempt ---")
print("NOTE: This is a statistical guess and requires manual refinement!")
print("-" * 60)
print(decrypted_guess)