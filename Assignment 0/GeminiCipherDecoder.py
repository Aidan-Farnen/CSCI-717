import string

def create_decryption_table(key_mapping):
    """
    Creates the decryption translation table from the key mapping.

    Args:
        key_mapping (dict): A dictionary where keys are CIPHERTEXT letters
                            and values are their PLAINTEXT substitutions.

    Returns:
        str.maketrans table: The translation table for decryption.
    """
    # The key is already in the required format: Ciphertext -> Plaintext
    return str.maketrans(key_mapping)

def aristocrat_decipher(ciphertext, table):
    """
    Applies the cipher translation (decryption) to the ciphertext.
    """
    # Text is usually uppercase for these ciphers
    return ciphertext.upper().translate(table)

# --- USER INPUT SECTION ---

# 1. Paste your ciphertext here (all caps, no spaces if possible, or keep spaces)
CIPHERTEXT = "QXP KQL YQG UZGP XP Q ZQG JQZ" # Example: THIS IS NOT A REAL KEY

# 2. Define the DECRYPTION key (Ciphertext letter -> Plaintext letter)
# YOU MUST FIGURE OUT/PROVIDE THIS KEY for the code to work.
# 'Q' maps to 'T', 'X' maps to 'H', etc.
DECRYPTION_KEY = {
    'Q': 'T', 'X': 'H', 'P': 'I', 'K': 'S', 'L': 'F',
    'Y': 'A', 'G': 'R', 'U': 'E', 'Z': 'N', 'J': 'M',
    # Continue mapping all 26 letters...
}

# --- DECRYPTION ---

# 1. Create the translation table
decryption_table = create_decryption_table(DECRYPTION_KEY)

# 2. Decrypt the message
plaintext = aristocrat_decipher(CIPHERTEXT, decryption_table)

# 3. Print the result
print(f"Ciphertext: {CIPHERTEXT}")
print(f"Decryption Key: {DECRYPTION_KEY}")
print(f"Plaintext:  {plaintext}")