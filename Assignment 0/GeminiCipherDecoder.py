def create_decryption_table(key_mapping):
    """Creates the decryption translation table."""
    return str.maketrans(key_mapping)

def aristocrat_decipher(ciphertext, table):
    """Applies the cipher translation (decryption) to the ciphertext."""
    return ciphertext.upper().translate(table)

# The Full Decryption Key (Ciphertext letter -> Plaintext letter)
DECRYPTION_KEY = {
    'W': 'M', 'U': 'O', 'O': 'V', 'C': 'E', 'I': 'N', 'M': 'T', 'L': 'S',
    'F': 'H', 'Z': 'A', 'V': 'R', 'X': 'I', 'A': 'B', 'D': 'C', 'Y': 'D',
    'J': 'P', 'B': 'L', 'G': 'J', 'N': 'U', 'R': 'Y', 'E': 'G', 'P': 'W',
    'T': 'F',
}

CIPHERTEXT = "WUOCWCIML FZOC IZVVZMXOCL. MFCR MCBB LMUVXCL, ACDZNLC MFCR ZVC IUM GNLM ZAUNM VCZVVZIEXIE CDUIUWXDL ZIY JUBXMXDL. MFCR ZBLU VCZVVZIEC WCZIXIE. ZIY MFCR’VC IUM GNLM ZAUNM VCYXLMVXANMXIE MFC EUUYL. MFCR’VC ZAUNM TXENVXIE UNM PFZM XL EUUY."

# 1. Create the translation table
decryption_table = create_decryption_table(DECRYPTION_KEY)

# 2. Decrypt the message
plaintext = aristocrat_decipher(CIPHERTEXT, decryption_table)

# 3. Print the result
print("--- Decrypted Message ---")
print(plaintext)
print("Look at small words to see if you can swap around letters to have them make sense and edit the DECRYPTION_KEY to make the swap")