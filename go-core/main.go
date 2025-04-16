package main

import (
	"bufio"
	"encoding/hex"
	"fmt"
	"os"
	"strings"
)

func main() {
	// First, check for command-line arguments
	if len(os.Args) > 1 {
		command := os.Args[1]
		
		if command == "generate-mnemonic" {
			mnemonic, err := GenerateMnemonic()
			if err != nil {
				fmt.Fprintf(os.Stderr, "Error: %v\n", err)
				os.Exit(1)
			}
			// Just print the mnemonic without any prefix
			fmt.Println(mnemonic)
			os.Exit(0)
		} else if command == "derive-key" {
			if len(os.Args) < 3 {
				fmt.Println("Usage: derive-key <mnemonic>")
				os.Exit(1)
			}
			
			mnemonic := os.Args[2]
			privKey, address, err := DeriveKey(mnemonic, "m/44'/60'/0'/0/0", Ethereum)
			if err != nil {
				fmt.Println("Error deriving key:", err)
				os.Exit(1)
			}
			fmt.Printf("Ethereum Address: %s\nPrivate Key: %s\n", address, privKey)
			os.Exit(0)
		} else if command == "derive-btc" {
			if len(os.Args) < 3 {
				fmt.Println("Usage: derive-btc <mnemonic> [witness_type]")
				os.Exit(1)
			}
			mnemonic := os.Args[2]
			witnessType := "legacy"
			if len(os.Args) > 3{
				witnessType=os.Args[3]
			}
			privKey, address, err := DeriveKey(mnemonic, "m/44'/0'/0'/0/0", Bitcoin,witnessType)
			if err != nil {
				fmt.Println("Error deriving key:", err)
				os.Exit(1)
			}
			fmt.Printf("Bitcoin Address: %s\nPrivate Key: %s\n", address, privKey)
			os.Exit(0)
		} else if command == "derive-sol" {
			if len(os.Args) < 3 {
				fmt.Println("Usage: derive-sol <mnemonic>")
				os.Exit(1)
			}
			mnemonic := os.Args[2]
			privKey, address, err := DeriveKey(mnemonic, "m/44'/501'/0'/0", Solana)
			if err != nil {
				fmt.Println("Error deriving key:", err)
				os.Exit(1)
			}
			fmt.Printf("Solana Address: %s\nPrivate Key: %s\n", address, privKey)
			os.Exit(0)
		} else if command == "encrypt" {
			if len(os.Args) < 4 {
				fmt.Println("Usage: encrypt <privateKeyHex> <password>")
				os.Exit(1)
			}
			privKey, _ := hex.DecodeString(os.Args[2])
			encrypted, _ := EncryptPrivateKey(privKey, os.Args[3])
			fmt.Println(hex.EncodeToString(encrypted))
			os.Exit(0)
		} else if command == "decrypt" {
			if len(os.Args) < 4 {
				fmt.Println("Usage: decrypt <encryptedKeyHex> <password>")
				os.Exit(1)
			}
			encrypted, _ := hex.DecodeString(os.Args[2])
			decrypted, _ := DecryptPrivateKey(encrypted, os.Args[3])
			fmt.Println(hex.EncodeToString(decrypted))
			os.Exit(0)
		}
		
		// If the command wasn't recognized
		fmt.Fprintf(os.Stderr, "Unknown command: %s\n", command)
		os.Exit(1)
	}

	// If no command-line args, start interactive mode
	scanner := bufio.NewScanner(os.Stdin)

	for {
		fmt.Print("Enter command: ")
		scanner.Scan()
		input := scanner.Text()
		args := strings.Fields(input)

		if len(args) == 0 {
			continue
		}

		command := args[0]

		if command == "exit" {
			fmt.Println("Exiting program.")
			break
		}

		switch command {
		case "generate-mnemonic":
			mnemonic, err := GenerateMnemonic()
			if err != nil {
				fmt.Println("Error generating mnemonic:", err)
				continue
			}
			fmt.Println("Mnemonic:", mnemonic)
		case "derive-key":
			if len(args) < 2 {
				fmt.Println("Usage: derive-key <mnemonic>")
				continue
			}
		
			mnemonic := args[1]
			privKey, address, err := DeriveKey(mnemonic, "m/44'/60'/0'/0/0", Ethereum)
			if err != nil {
				fmt.Println("Error deriving key:", err)
				continue
			}
			fmt.Printf("Ethereum Address: %s\nPrivate Key: %s\n", address, privKey)
		case "derive-btc":
			if len(args) < 2 {
				fmt.Println("Usage: derive-btc <mnemonic>")
				continue
			}
			mnemonic := args[1]
			privKey, address, err := DeriveKey(mnemonic, "m/44'/0'/0'/0/0", Bitcoin)
			if err != nil {
				fmt.Println("Error deriving key:", err)
				continue
			}
			fmt.Printf("Bitcoin Address: %s\nPrivate Key: %s\n", address, privKey)
		case "derive-sol":
			if len(args) < 2 {
				fmt.Println("Usage: derive-sol <mnemonic>")
				continue
			}
			mnemonic := args[1]
			privKey, address, err := DeriveKey(mnemonic, "m/44'/501'/0'/0", Solana)
			if err != nil {
				fmt.Println("Error deriving key:", err)
				continue
			}
			fmt.Printf("Solana Address: %s\nPrivate Key: %s\n", address, privKey)
		case "encrypt":
			if len(args) < 3 {
				fmt.Println("Usage: encrypt <privateKeyHex> <password>")
				continue
			}
			privKey, _ := hex.DecodeString(args[1])
			encrypted, _ := EncryptPrivateKey(privKey, args[2])
			fmt.Println(hex.EncodeToString(encrypted))
		case "decrypt":
			if len(args) < 3 {
				fmt.Println("Usage: decrypt <encryptedKeyHex> <password>")
				continue
			}
			encrypted, _ := hex.DecodeString(args[1])
			decrypted, _ := DecryptPrivateKey(encrypted, args[2])
			fmt.Println(hex.EncodeToString(decrypted))
		default:
			fmt.Println("Unknown command:", command)
		}
	}
}