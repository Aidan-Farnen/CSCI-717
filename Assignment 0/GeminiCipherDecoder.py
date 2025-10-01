import string

def create_aristocrat_key(key_mapping):
    """
    Creates the encryption and decryption translation tables.

    Args:
        key_mapping (dict): A dictionary where keys are plaintext letters
                            and values are their ciphertext substitutions.

    Returns:
        tuple: (encryption_table, decryption_table)
    """
    # Create the reverse mapping for decryption
    rev_mapping = {v: k for k, v in key_mapping.items()}

    # Create translation tables
    enc_table = str.maketrans(key_mapping)
    dec_table = str.maketrans(rev_mapping)

    return enc_table, dec_table

def aristocrat_cipher(text, table):
    """
    Applies the cipher translation to the text.
    """
    # Convert text to uppercase before applying the translation
    return text.upper().translate(table)

# --- Example Usage ---

# Define a substitution key (Plaintext -> Ciphertext)
# This key is the 'code' for the cipher.
# A common characteristic of Aristocrats is that no letter maps to itself.
KEY = {
    'A': 'M', 'B': 'N', 'C': 'O', 'D': 'P', 'E': 'Q',
    'F': 'R', 'G': 'S', 'H': 'T', 'I': 'U', 'J': 'V',
    'K': 'W', 'L': 'X', 'M': 'Y', 'N': 'Z', 'O': 'A',
    'P': 'B', 'Q': 'C', 'R': 'D', 'S': 'E', 'T': 'F',
    'U': 'G', 'V': 'H', 'W': 'I', 'X': 'J', 'Y': 'K',
    'Z': 'L'
}

plaintext = "THIS IS A SECRET MESSAGE FOR YOU"

# 1. Create the translation tables
encrypt_table, decrypt_table = create_aristocrat_key(KEY)

# 2. Encrypt the message
ciphertext = aristocrat_cipher(plaintext, encrypt_table)
print(f"Plaintext:  {plaintext}")
print(f"Ciphertext: {ciphertext}")

print("-" * 20)

# 3. Decrypt the message
decrypted_text = aristocrat_cipher(ciphertext, decrypt_table)
print(f"Decrypted:  {decrypted_text}")