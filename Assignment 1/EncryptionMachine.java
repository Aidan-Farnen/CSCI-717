package encryptionMachine;

public class EncryptionMachine {
	
	public static final String ALPHABET = "abcdefghijklmnopqrstuvwxyz";
    public static final int SHIFT = 3;

    public static void main(String[] args) {
    	System.out.println("Encrypted 'a' → " + encryptLetter('a'));
    	System.out.println("Encrypted 'y' → " + encryptLetter('y'));
    }

    /**
     * Encrypts the fixed letter 'a' with a fixed shift of 3 using Caesar cipher logic.
     * Wraps around if necessary.
     */
    public static char encryptLetter(char letterInput) {

        int index = ALPHABET.indexOf(letterInput);	//get index of character input to method
        int shiftedIndex = (index + SHIFT) % ALPHABET.length();	//get the index of letter after shifting
        return ALPHABET.charAt(shiftedIndex);	//return character after shifting
    }
}

