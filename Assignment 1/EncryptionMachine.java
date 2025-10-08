package encryptionMachine;

import java.util.Scanner;

public class EncryptionMachine {
	// Class constants
	public static final String ALPHABET = "abcdefghijklmnopqrstuvwxyz";
    public static final int SHIFT = 3;

    public static void main(String[] args) {
    	
    	Scanner input = new Scanner(System.in);	//create new scanner
    	promptEncryption(input);	//call method to prompt user for input
    	input.close();	//close input
    }
    
    /**
     * Prompts user for input on the key and the number of words
     * they want to encrypt. Then calls encryptWord() for the key
     * and for each word they choose to enter
     */
    public static void promptEncryption(Scanner input) {
    	System.out.println("Welcome to the CSCI717 Encryption Machine Construction");
        System.out.println("The program lets you encrypt a message");
        System.out.println("with a key for your recipient to decrypt!");
        System.out.println();	//print new line
        
        // Prompt for the key
        System.out.print("Enter key: ");
        String key = input.next();	//set key to the input
        String encryptedKey = encryptWord(key);	//call encryptWord on the entered key
        //output the encrypted key
        System.out.println("\"" + key + "\" has been encrypted to: " + encryptedKey);
        System.out.println();	//print new line
        
        // Prompt for the number of words in the message
        System.out.print("How many words is your message?: ");
        int numWords = input.nextInt();	//set numWords to the input
        System.out.println();	//print new line
        
        // Encrypt each word
        for (int i = 0; i < numWords; i++) {	//prompt for numWords words to encrypt
            System.out.print("Next word: ");
            String word = input.next();	//set word to the input
            String encryptedWord = encryptWord(word);	//call encryptWord on the entered word
            //output the encrypted word
            System.out.println("\"" + word + "\" has been encrypted to: " + encryptedWord);
            System.out.println();	//print new line
        }
        
        System.out.println("Message fully encrypted. Happy secret messaging!");
    }

    /**
     * Encrypts an input letter by shifting it based on the SHIFT class constant.
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

