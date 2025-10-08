package encryptionMachine;

public class EncryptionMachine {
	// Class constants
	public static final String ALPHABET = "abcdefghijklmnopqrstuvwxyz";
    public static final int SHIFT = 3;

    public static void main(String[] args) {
    	System.out.println("Encrypted 'play' → " + encryptWord("play"));
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
    
    /**
     * Encrypts an entire word by encrypting each letter individually
     * using the encryptLetter() method.
     */
    public static String encryptWord(String inputWord) {
        StringBuilder outputWord = new StringBuilder();	//create new string builder

        for (int i = 0; i < inputWord.length(); i++) {	//loop through each character in input word
            char inputLetter = inputWord.charAt(i);	//get the character at the loop index
            char shiftedLetter = encryptLetter(inputLetter);	//shift character with encryptLetter()
            outputWord.append(shiftedLetter);	//append shifted character to string builder
        }

        return outputWord.toString();	//return new word made up of shifted characters
    }
}

