package encryptionMachine;

public class EncryptionMachine {

    public static void main(String[] args) {
        char plainLetter = 'y';  // arbitrary single letter
        char cipherLetter = encryptFixedLetter();	// call method
        System.out.println("Encrypted '" + plainLetter + "' → '" + cipherLetter + "'");	//output
    }

    /**
     * Encrypts the fixed letter 'a' with a fixed shift of 3 using Caesar cipher logic.
     * Wraps around if necessary.
     */
    public static char encryptFixedLetter() {
        final String ALPHABET = "abcdefghijklmnopqrstuvwxyz";
        final int SHIFT = 3;

        char plain = 'y'; // arbitrary single letter
        int index = ALPHABET.indexOf(plain);	//get index of arbitrary letter
        int shiftedIndex = (index + SHIFT) % ALPHABET.length();	//get the index of letter after shifting
        return ALPHABET.charAt(shiftedIndex);	//return character after shifting
    }
}

