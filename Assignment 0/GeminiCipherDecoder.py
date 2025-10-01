import string
from collections import Counter

# Standard English letter frequencies (approximate percentages)
# The order is: E, T, A, O, I, N, S, H, R
ENGLISH_FREQUENCIES = {
    'E': 12.70, 'T': 9.06, 'A': 8.17, 'O': 7.51, 'I': 6.97,
    'N': 6.75, 'S': 6.33, 'H': 6.09, 'R': 5.99, 'D': 4.25,
    'L': 4.03, 'C': 2.78, 'U': 2.76, 'M': 2.41, 'W': 2.36,
    'F': 2.23, 'G': 2.02, 'Y': 1.97, 'P': 1.93, 'B': 1.29,
    'V': 0.98, 'K': 0.77, 'J': 0.15, 'X': 0.15, 'Q': 0.10,
    'Z': 0.07
}

def analyze_ciphertext_frequencies(ciphertext):
    """
    Calculates letter frequencies in the ciphertext and compares them
    to standard English frequencies.

    Args:
        ciphertext (str): The cipher text to analyze.

    Returns:
        dict: A dictionary of ciphertext letter counts and percentages.
    """
    # Clean the text: convert to uppercase and keep only letters
    cleaned_text = ''.join(filter(str.isalpha, ciphertext.upper()))
    total_letters = len(cleaned_text)

    if total_letters == 0:
        return "Error: No letters found in the ciphertext."

    # Count the occurrences of each letter
    counts = Counter(cleaned_text)

    # Calculate percentages and prepare for display
    analysis = {}
    for letter in sorted(counts.keys()):
        count = counts[letter]
        percentage = (count / total_letters) * 100
        analysis[letter] = {
            'count': count,
            'percent': round(percentage, 2)
        }

    return analysis

# --- Example Usage (Replace with your actual ciphertext) ---

# Example Ciphertext:
CIPHERTEXT = "QXP KQL YQG UZGP XP Q ZQG JQZ" 
# (This is a short, fabricated example. Real texts should be longer for good frequency analysis.)

# Run the analysis
cipher_analysis = analyze_ciphertext_frequencies(CIPHERTEXT)

# --- Display Results ---

print("--- Ciphertext Frequency Analysis ---")
print(f"Total Letters Analyzed: {len(''.join(filter(str.isalpha, CIPHERTEXT.upper())))}")
print("-" * 50)
print(f"| {'Cipher Letter':<15} | {'Count':<5} | {'Percent':<7} | {'English Guess':<15} |")
print("-" * 50)

# Sort the cipher letters by descending frequency for easier comparison
sorted_cipher_analysis = sorted(cipher_analysis.items(), key=lambda item: item[1]['percent'], reverse=True)

# Sort English frequencies (E, T, A, O, I, N...)
sorted_english = sorted(ENGLISH_FREQUENCIES.items(), key=lambda item: item[1], reverse=True)
english_letters = [item[0] for item in sorted_english]

# Display the results
for i, (cipher_letter, data) in enumerate(sorted_cipher_analysis):
    # Match the i-th most frequent cipher letter to the i-th most frequent English letter
    english_guess = english_letters[i] if i < len(english_letters) else '?'

    print(f"| {cipher_letter:<15} | {data['count']:<5} | {data['percent']:<7.2f}% | {english_guess:<15} |")

print("-" * 50)
print("The 'English Guess' column suggests a possible mapping (e.g., the most frequent cipher letter often maps to 'E').")
print("This is the starting point for manual decoding and key creation.")