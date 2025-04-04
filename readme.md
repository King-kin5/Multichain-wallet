# Multichain Wallet CLI







A command-line interface wallet manager supporting multiple blockchains (Ethereum, Bitcoin, and Solana). Built with Python and Go for secure key derivation and management.

## Features

- 🔐 BIP39 mnemonic generation and wallet derivation
- 💼 Multi-chain support:
  - Ethereum (fully implemented)
  - Bitcoin (key derivation ready)
  - Solana (key derivation ready)
- 🔒 Secure key encryption/decryption
- 💸 Transaction management (Ethereum)
- 🔍 Balance checking and transaction status
- 🌐 Custom RPC endpoint configuration

## Installation

1. Clone the repository:
```sh
git clone https://github.com/yourusername/multichain-wallet.git
cd multichain-wallet
```

2. Install Python dependencies:
```sh
pip install -r requirements.txt
```

3. Build the Go core:
```sh
cd go-core
go build -o core.exe
```

## Usage

Start the CLI:
```sh
python cli.py
```

### Available Commands

- `generate` - Create new BIP-39 mnemonic phrase
- `eth` - Enter Ethereum wallet mode
- `help` - Show available commands

### Ethereum Mode Commands

- `wallet` - Show current wallet info
- `balance <addr>` - Check ETH balance
- `create <mnemonic>` - Create a new wallet
- `encrypt` - Encrypt the current wallet
- `decrypt` - Decrypt an encrypted wallet
- `send <to> <amount>` - Send ETH
- `tx <hash>` - Check transaction status
- `connect <url>` - Connect to different Ethereum node

## Project Structure

```
multichain-wallet/
├── cli.py              # Main CLI interface
├── chains/             # Blockchain implementations
│   ├── Ethereum.py    # Ethereum chain logic
│   └── util.py        # Shared utilities
├── go-core/           # Go-based cryptographic core
│   ├── bip39.go      # Mnemonic operations
│   ├── crypto.go     # Encryption utilities
│   └── hardwallet.go # Key derivation logic
├── py_types/         # Python type definitions
│   ├── token.py     # Token data structures
│   ├── transaction.py # Transaction types
│   └── wallet.py    # Wallet data structures
└── utils/           # Additional utilities
    └── ethereum_mode.py # Ethereum mode handler
```

## Future Development

- [ ] Complete Bitcoin mode implementation
- [ ] Complete Solana mode implementation
- [ ] Add token management
- [ ] Implement hardware wallet support
- [ ] Add support for additional chains

## Security Notes

- Private keys are always encrypted when stored
- Encryption passwords should be stored securely
- Use trusted RPC endpoints for network connections

