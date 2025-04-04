package main

import (
	"crypto/aes"
	"crypto/cipher"
	"crypto/rand"
	"fmt"
	"golang.org/x/crypto/scrypt"
)

const (
	// Scrypt parameters (N, r, p). Adjust for your security needs.
	scryptN      = 32768
	scryptR      = 8
	scryptP      = 1
	scryptKeyLen = 32 // AES-256 requires 32-byte keys
	saltSize     = 32 // 32 bytes for salt
)

// EncryptPrivateKey encrypts a private key using AES-GCM and Scrypt for key derivation.
func EncryptPrivateKey(privkey []byte, password string) ([]byte, error) {
	// Generate a random salt for Scrypt
	salt := make([]byte, saltSize)
	// Use crypto/rand to generate a secure random salt
	if _, err := rand.Read(salt); err != nil {
		return nil, fmt.Errorf("failed to generate salt: %v", err)
	}

	// Derive a key from the password using Scrypt
	key, err := scrypt.Key([]byte(password), salt, scryptN, scryptR, scryptP, scryptKeyLen)
	if err != nil {
		return nil, fmt.Errorf("scrypt key derivation failed: %v", err)
	}

	// Create a new AES-GCM cipher block
	block, err := aes.NewCipher(key)
	if err != nil {
		return nil, fmt.Errorf("AES cipher creation failed: %v", err)
	}
	// Create GCM mode
	gcm, err := cipher.NewGCM(block)
	if err != nil {
		return nil, fmt.Errorf("GCM mode creation failed: %v", err)
	}

	// Generate a random nonce for GCM
	nonce := make([]byte, gcm.NonceSize())
	if _, err := rand.Read(nonce); err != nil {
		return nil, fmt.Errorf("nonce generation failed: %v", err)
	}

	// Encrypt the private key using AES-GCM
	ciphertext := gcm.Seal(nil, nonce, privkey, nil)

	// Combine salt, nonce and ciphertext into one byte slice
	result := append(salt, nonce...)
	result = append(result, ciphertext...)

	return result, nil
}

// DecryptPrivateKey decrypts an encrypted private key.
func DecryptPrivateKey(encryptedData []byte, password string) ([]byte, error) {
	// Calculate expected minimum length
	if len(encryptedData) < saltSize+12 { // 12 is the standard GCM nonce size
		return nil, fmt.Errorf("invalid encrypted data: too short")
	}
	
	// Extract salt, nonce, and ciphertext
	salt := encryptedData[:saltSize]
	nonceSize := 12 // GCM's standard nonce size
	nonce := encryptedData[saltSize : saltSize+nonceSize]
	ciphertext := encryptedData[saltSize+nonceSize:]

	// Derive the key using Scrypt
	key, err := scrypt.Key(
		[]byte(password), salt, scryptN, scryptR, scryptP, scryptKeyLen,
	)
	if err != nil {
		return nil, fmt.Errorf("scrypt key derivation failed: %v", err)
	}
	
	// Create AES cipher block
	block, err := aes.NewCipher(key)
	if err != nil {
		return nil, fmt.Errorf("AES cipher creation failed: %v", err)
	}
	
	// Create GCM mode
	gcm, err := cipher.NewGCM(block)
	if err != nil {
		return nil, fmt.Errorf("GCM mode creation failed: %v", err)
	}
	
	// Decrypt data
	decrypted, err := gcm.Open(nil, nonce, ciphertext, nil)
	if err != nil {
		return nil, fmt.Errorf("decryption failed (possibly wrong password): %v", err)
	}

	return decrypted, nil
}