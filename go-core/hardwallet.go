package main

import (
	"crypto/ecdsa"
	"crypto/ed25519"
	"encoding/hex"
	"fmt"
	"strconv"
	"strings"

	"github.com/btcsuite/btcd/chaincfg"
	"github.com/btcsuite/btcutil"
	"github.com/btcsuite/btcutil/base58"
	"github.com/btcsuite/btcutil/hdkeychain"
	"github.com/ethereum/go-ethereum/crypto"
	"github.com/tyler-smith/go-bip39"
	"golang.org/x/crypto/sha3"
)

// ChainType represents different blockchain types
type ChainType int

const (
	Bitcoin ChainType = iota // Bitcoin blockchain type
	Ethereum                 // Ethereum blockchain type
	Solana                   // Solana blockchain type
)

// DeriveKey derives a private key and its corresponding address for different blockchain types
func DeriveKey(mnemonic, path string, chainType ChainType, witnessType ...string) (string, string, error) {
    // Validate mnemonic
    if !bip39.IsMnemonicValid(mnemonic) {
        return "", "", fmt.Errorf("invalid mnemonic phrase")
    }

    // Generate seed from mnemonic (consider adding a passphrase for additional security)
    seed := bip39.NewSeed(mnemonic, "")

    // Switch case to determine which blockchain key derivation function to call
    switch chainType {
    case Bitcoin:
        // If witnessType is provided, pass it to deriveBitcoinKey
        if len(witnessType) > 0 {
            return deriveBitcoinKeyWithFormat(seed, path, witnessType[0])
        }
        return deriveBitcoinKey(seed, path) // Original function for backward compatibility
    case Ethereum:
        return deriveEthereumKey(seed, path)
    case Solana:
        return deriveSolanaKey(seed, path)
    default:
        return "", "", fmt.Errorf("unsupported chain type")
    }
}
// deriveBitcoinKeyWithFormat derives a Bitcoin private key and address with specified format
func deriveBitcoinKeyWithFormat(seed []byte, path string, witnessType string) (string, string, error) {
    // Generate master key from seed
    masterKey, err := hdkeychain.NewMaster(seed, &chaincfg.MainNetParams)
    if err != nil {
        return "", "", fmt.Errorf("failed to create master key: %w", err)
    }

    // Derive key from the given derivation path
    derivedKey, err := DeriveKeyFromPath(masterKey, path)
    if err != nil {
        return "", "", fmt.Errorf("failed to derive key: %w", err)
    }

    // Extract private key
    privateKey, err := derivedKey.ECPrivKey()
    if err != nil {
        return "", "", fmt.Errorf("failed to extract private key: %w", err)
    }
    privKeyHex := hex.EncodeToString(privateKey.Serialize())

    // Extract public key
    pubKey, err := derivedKey.ECPubKey()
    if err != nil {
        return "", "", fmt.Errorf("failed to extract public key: %w", err)
    }

    // Generate Bitcoin address based on witnessType
    var address string
    switch strings.ToLower(witnessType) {
    case "legacy":
        // Legacy address (P2PKH)
        pubKeyHash := btcutil.Hash160(pubKey.SerializeCompressed())
        legacyAddress, err := btcutil.NewAddressPubKeyHash(pubKeyHash, &chaincfg.MainNetParams)
        if err != nil {
            return "", "", fmt.Errorf("failed to create legacy Bitcoin address: %w", err)
        }
        address = legacyAddress.EncodeAddress()
    case "segwit":
        // SegWit address (P2SH-wrapped)
        witnessProgram := btcutil.Hash160(pubKey.SerializeCompressed())
        witnessProgramHash := btcutil.Hash160(append([]byte{0x00, 0x14}, witnessProgram...))
        segwitAddress, err := btcutil.NewAddressScriptHashFromHash(witnessProgramHash, &chaincfg.MainNetParams)
        if err != nil {
            return "", "", fmt.Errorf("failed to create segwit Bitcoin address: %w", err)
        }
        address = segwitAddress.EncodeAddress()
    case "bech32":
        // Native SegWit address (Bech32/P2WPKH)
        witnessProg := btcutil.Hash160(pubKey.SerializeCompressed())
        bech32Address, err := btcutil.NewAddressWitnessPubKeyHash(witnessProg, &chaincfg.MainNetParams)
        if err != nil {
            return "", "", fmt.Errorf("failed to create bech32 Bitcoin address: %w", err)
        }
        address = bech32Address.EncodeAddress()
    default:
        // Default to legacy if unknown format specified
        pubKeyHash := btcutil.Hash160(pubKey.SerializeCompressed())
        legacyAddress, err := btcutil.NewAddressPubKeyHash(pubKeyHash, &chaincfg.MainNetParams)
        if err != nil {
            return "", "", fmt.Errorf("failed to create Bitcoin address: %w", err)
        }
        address = legacyAddress.EncodeAddress()
    }

    return privKeyHex, address, nil
}
// deriveBitcoinKey derives a Bitcoin private key and address from the seed and derivation path
func deriveBitcoinKey(seed []byte, path string) (string, string, error) {
	// Generate master key from seed
	masterKey, err := hdkeychain.NewMaster(seed, &chaincfg.MainNetParams)
	if err != nil {
		return "", "", fmt.Errorf("failed to create master key: %w", err) // Return error if key generation fails
	}

	// Derive key from the given derivation path
	derivedKey, err := DeriveKeyFromPath(masterKey, path)
	if err != nil {
		return "", "", fmt.Errorf("failed to derive key: %w", err) // Return error if derivation fails
	}

	// Extract private key
	privateKey, err := derivedKey.ECPrivKey()
	if err != nil {
		return "", "", fmt.Errorf("failed to extract private key: %w", err) // Return error if private key extraction fails
	}
	privKeyHex := hex.EncodeToString(privateKey.Serialize()) // Convert private key to hexadecimal format

	// Extract public key
	pubKey, err := derivedKey.ECPubKey()
	if err != nil {
		return "", "", fmt.Errorf("failed to extract public key: %w", err) // Return error if public key extraction fails
	}

	// Generate Bitcoin address
	pubKeyHash := btcutil.Hash160(pubKey.SerializeCompressed()) // Compute hash of the compressed public key
	address, err := btcutil.NewAddressPubKeyHash(pubKeyHash, &chaincfg.MainNetParams)
	if err != nil {
		return "", "", fmt.Errorf("failed to create Bitcoin address: %w", err) // Return error if address creation fails
	}

	return privKeyHex, address.EncodeAddress(), nil // Return private key and Bitcoin address
}

// deriveEthereumKey derives an Ethereum private key and address from the seed and derivation path
func deriveEthereumKey(seed []byte, path string) (string, string, error) {
	// Generate master key from seed
	masterKey, err := hdkeychain.NewMaster(seed, &chaincfg.MainNetParams)
	if err != nil {
		return "", "", fmt.Errorf("failed to create master key: %w", err) // Return error if key generation fails
	}

	// Derive key from the given derivation path
	derivedKey, err := DeriveKeyFromPath(masterKey, path)
	if err != nil {
		return "", "", fmt.Errorf("failed to derive key: %w", err) // Return error if derivation fails
	}

	// Extract private key
	privateKey, err := derivedKey.ECPrivKey()
	if err != nil {
		return "", "", fmt.Errorf("failed to extract private key: %w", err) // Return error if private key extraction fails
	}
	privKeyBytes := privateKey.Serialize()
	privKeyHex := hex.EncodeToString(privKeyBytes) // Convert private key to hexadecimal format

	// Convert to Ethereum private key
	ethPrivKey, err := crypto.ToECDSA(privKeyBytes)
	if err != nil {
		return "", "", fmt.Errorf("failed to convert to Ethereum private key: %w", err)
	}

	// Generate Ethereum address from public key
	publicKey := ethPrivKey.Public().(*ecdsa.PublicKey)
	address := crypto.PubkeyToAddress(*publicKey)

	return privKeyHex, address.Hex(), nil // Return private key and Ethereum address
}

// DeriveKeyFromPath derives a child key from a master key using a BIP32 derivation path
func DeriveKeyFromPath(masterKey *hdkeychain.ExtendedKey, path string) (*hdkeychain.ExtendedKey, error) {
	components := strings.Split(path, "/")
	key := masterKey

	for _, component := range components {
		if component == "m" || component == "" {
			continue
		}

		// Handle hardened derivation
		var childNum uint32
		if strings.HasSuffix(component, "'") || strings.HasSuffix(component, "h") {
			// Support both ' and h as hardened indicators
			index, err := strconv.Atoi(strings.TrimRight(component, "'h"))
			if err != nil {
				return nil, fmt.Errorf("invalid path component: %s", component)
			}
			childNum = uint32(index) + hdkeychain.HardenedKeyStart
		} else {
			index, err := strconv.Atoi(component)
			if err != nil {
				return nil, fmt.Errorf("invalid path component: %s", component)
			}
			childNum = uint32(index)
		}

		var err error
		key, err = key.Child(childNum)
		if err != nil {
			return nil, fmt.Errorf("failed to derive child key at component %s: %w", component, err)
		}
	}
	return key, nil
}

// deriveSolanaKey derives a Solana private key and address from the seed and derivation path
func deriveSolanaKey(seed []byte, path string) (string, string, error) {
	// Generate master key from seed
	masterKey, err := hdkeychain.NewMaster(seed, &chaincfg.MainNetParams)
	if err != nil {
		return "", "", fmt.Errorf("failed to create master key: %w", err)
	}

	// Derive key from the given derivation path
	derivedKey, err := DeriveKeyFromPath(masterKey, path)
	if err != nil {
		return "", "", fmt.Errorf("failed to derive key: %w", err)
	}

	// Extract private key
	privateKey, err := derivedKey.ECPrivKey()
	if err != nil {
		return "", "", fmt.Errorf("failed to extract private key: %w", err)
	}
	privKeyBytes := privateKey.Serialize()
	privKeyHex := hex.EncodeToString(privKeyBytes)

	// For Solana, we need to convert the secp256k1 private key to ed25519
	// Note: This is a simplified approach - in production, use a proper Solana SDK
	// We're using the private key to seed an ed25519 key
	hash := sha3.Sum512(privKeyBytes)
	var edPrivateKey ed25519.PrivateKey = make([]byte, ed25519.PrivateKeySize)
	copy(edPrivateKey, hash[:32])
	
	// Generate the public key
	publicKey := ed25519.PublicKey(edPrivateKey.Public().(ed25519.PublicKey))
	
	// Solana addresses are the base58 encoding of the public key
	solanaAddress := base58.Encode(publicKey)

	return privKeyHex, solanaAddress, nil
}