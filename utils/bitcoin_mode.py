import getpass
from chains.Bitcoin import BitcoinClient
from chains.util import derive_key, generate_mnemonic
from bitcoinlib.wallets import wallet_create_or_open

class BitcoinMode:
    def __init__(self):
        self.btc_client = None
        self.current_wallet = None
        self.wallet_format = 'legacy'  # Default to legacy format for consistent address generation

    def initialize_bitcoin(self, network="bitcoin"):
        """Initialize Bitcoin client with default or specified network"""
        try:
            self.btc_client = BitcoinClient(network=network)
            print(f"\n✅ Connected to Bitcoin network: {network}")
            return True
        except Exception as e:
            print(f"\n⚠️ Failed to connect to Bitcoin network: {str(e)}")
            return False

    def print_btc_help(self):
        print("\nBitcoin commands:")
        print("  wallet        - Show current wallet info")
        print("  balance <addr> - Check BTC balance (uses current wallet if no address provided)")
        print("  create <mnemonic> - Create a new wallet (generates mnemonic if none provided)")
        print("  encrypt       - Encrypt the current wallet")
        print("  decrypt       - Decrypt an encrypted wallet")
        print("  send <to> <amount> <fee> - Send BTC to an address (fee in satoshis is optional)")
        print("  network <name> - Switch to a different network (bitcoin, testnet)")
        print("  format <type> - Switch address format (legacy, segwit, bech32)")
        print("  tx <hash>     - Check transaction status")
        print("  back          - Return to main menu")
        print("  help          - Show this help message\n")

    def get_mnemonic_from_user(self, args, last_mnemonic):
        """Helper to extract mnemonic from args or prompt user"""
        if args and isinstance(args, list) and args[0].strip():
            return args[0].strip()
        elif args and isinstance(args, str) and args.strip():
            return args.strip()
        
        if last_mnemonic:
            print(f"\n🔍 Last generated mnemonic available. Use it? (y/n)")
            if input("> ").strip().lower() == 'y':
                return last_mnemonic
        
        print("\nEnter mnemonic phrase:")
        return input("> ").strip()

    def start(self, last_mnemonic=None):
        """Handle Bitcoin-specific commands"""
        # Initialize Bitcoin client if not already done
        if not self.btc_client:
            if not self.initialize_bitcoin():
                return
        
        print("\n🔹 Bitcoin Mode 🔹")
        print("Type 'help' for available Bitcoin commands\n")
        
        while True:
            try:
                command = input("btc> ").strip().lower()
                
                if not command:
                    continue
                    
                parts = command.split(maxsplit=2)
                command = parts[0].lower()
                args = parts[1:] if len(parts) > 1 else []
                
                if command == "back":
                    print("\n↩️ Returning to main menu\n")
                    break
                    
                elif command == "help":
                    self.print_btc_help()
                
                elif command == "wallet":
                    if self.current_wallet:
                        print("\n" + "="*60)
                        print(" " * 20 + "👛 WALLET INFO 👛")
                        print("="*60)
                        
                        # Wallet Status
                        status = "🔓 DECRYPTED" if "private_key" in self.current_wallet else "🔒 ENCRYPTED"
                        print(f"\nStatus: {status}")
                        
                        # Address with format indicator
                        address = self.current_wallet.get('address', 'N/A')
                        format_emoji = {
                            'legacy': '1️⃣',
                            'segwit': '3️⃣',
                            'bech32': '🆕'
                        }.get(self.wallet_format, '❓')
                        print(f"\nAddress ({format_emoji} {self.wallet_format.upper()}):")
                        print(f"└─ {address}")
                        
                        # Key Information
                        if "private_key" in self.current_wallet:
                            print("\nPrivate Key:")
                            print(f"└─ {self.current_wallet['private_key']}")
                        elif "encrypted_key" in self.current_wallet:
                            print("\nEncrypted Key:")
                            print(f"└─ {self.current_wallet['encrypted_key']}")
                        
                        # Network Information
                        network = self.btc_client.network if self.btc_client else "Not Connected"
                        print(f"\nNetwork: {network.upper()}")
                        
                        # Format Information
                        print("\nAddress Format Details:")
                        format_info = {
                            'legacy': 'Original format (P2PKH) - Starts with "1"',
                            'segwit': 'SegWit format (P2SH) - Starts with "3"',
                            'bech32': 'Native SegWit (P2WPKH) - Starts with "bc1"'
                        }.get(self.wallet_format, 'Unknown format')
                        print(f"└─ {format_info}")
                        
                        print("\n" + "="*60 + "\n")
                    else:
                        print("\n" + "="*60)
                        print(" " * 20 + "⚠️ NO WALLET LOADED ⚠️")
                        print("="*60)
                        print("\nTo create a new wallet, use the 'create' command")
                        print("To load an existing wallet, use the 'decrypt' command\n")
                
                elif command == "format":
                    if not args:
                        print(f"\n🔹 Current address format: {self.wallet_format}")
                        print("\nAvailable formats:")
                        print("  legacy  - Original format (starts with '1')")
                        print("  segwit  - SegWit format (starts with '3')")
                        print("  bech32  - Native SegWit (starts with 'bc1')")
                        print("\n⚠️ Usage: format <type> (legacy, segwit, bech32)\n")
                        continue
                    
                    format_type = args[0].lower()
                    if format_type not in ["legacy", "segwit", "bech32"]:
                        print("\n⚠️ Invalid format. Available formats: legacy, segwit, bech32\n")
                        continue
                    
                    if format_type == self.wallet_format:
                        print(f"\nℹ️ Wallet is already using {format_type} format\n")
                        continue
                    
                    old_format = self.wallet_format
                    self.wallet_format = format_type
                    print(f"\n✅ Changed address format from {old_format} to {format_type}")
                    
                    # If we have a wallet loaded with private key, update the address
                    if self.current_wallet and "private_key" in self.current_wallet:
                        try:
                            # Regenerate address with new format
                            private_key = self.current_wallet["private_key"]
                            witness_type = self._get_witness_type()
                            
                            wallet_name = f"temp_wallet_{self.wallet_format}"
                            temp_wallet = wallet_create_or_open(
                                wallet_name,
                                keys=private_key,
                                witness_type=witness_type
                            )
                            new_address = temp_wallet.get_key().address
                            
                            self.current_wallet["address"] = new_address
                            print(f"Updated wallet address to: {new_address}")
                            print(f"Note: This is the same wallet, just in a different format\n")
                        except Exception as e:
                            print(f"\n⚠️ Error updating address format: {str(e)}")
                            # Revert format change on error
                            self.wallet_format = old_format
                    else:
                        print(f"\nℹ️ No wallet loaded with private key. New format will be used for future wallets.\n")
                
                elif command == "create":
                    mnemonic = args[0] if args else generate_mnemonic()
                    if not args:
                        print(f"\n🆕 Generated Mnemonic: {mnemonic}")
                    
                    try:
                        # Pass the wallet format to create_wallet method
                        witness_type = self._get_witness_type()
                        self.current_wallet = BitcoinClient.create_wallet(
                            mnemonic, 
                            witness_type=witness_type
                        )
                        print(f"\n✅ Created new wallet:")
                        print(f"Address: {self.current_wallet['address']}")
                        print(f"Private Key: {self.current_wallet['private_key']}")
                        print(f"Format: {self.wallet_format}\n")
                    except Exception as e:
                        print(f"\n⚠️ Error creating wallet: {str(e)}")
                
                elif command == "balance":
                    address = args[0] if args else (self.current_wallet.get('address') if self.current_wallet else None)
                    
                    if not address:
                        print("\n⚠️ No address provided or wallet loaded\n")
                        continue
                    
                    try:
                        balance = self.btc_client.get_balance(address)
                        print(f"\n💰 BTC Balance for {address}: {balance} BTC\n")
                    except Exception as e:
                        print(f"\n⚠️ Error checking balance: {str(e)}")
                
                elif command == "encrypt":
                    if not self.current_wallet or "private_key" not in self.current_wallet:
                        print("\n⚠️ No wallet with private key loaded\n")
                        continue
                    
                    password = None
                    # Check if password is provided in command
                    if args:
                        password = args[0]
                    else:
                        # Prompt for password if not provided
                        password = getpass.getpass("\nEnter password for encryption (leave empty to generate): ")
                        # If empty, set to None so a password will be generated
                        if not password:
                            password = None
                        
                    try:
                        private_key = self.current_wallet["private_key"]
                        encrypted_data = self.btc_client.encrypt_wallet(private_key, password)
                        
                        # Update current wallet - keep address and format, only encrypt private key
                        self.current_wallet = {
                            "address": self.current_wallet["address"],
                            "encrypted_key": encrypted_data["encrypted_key"],
                            "format": self.wallet_format
                        }
                        
                        print(f"\n🔒 Private key encrypted successfully!")
                        print(f"Password: {encrypted_data['password_reference']}")
                        print("IMPORTANT: Save this password securely!\n")
                    except Exception as e:
                        print(f"\n⚠️ Error encrypting private key: {str(e)}")
                
                elif command == "decrypt":
                    encrypted_key = None
                    
                    # Check if an encrypted key is provided in the command
                    if args:
                        encrypted_key = args[0]
                    # Otherwise use the current wallet's encrypted key if available
                    elif self.current_wallet and "encrypted_key" in self.current_wallet:
                        encrypted_key = self.current_wallet.get("encrypted_key")
                    
                    if not encrypted_key:
                        print("\n⚠️ No encrypted private key loaded. Please provide encrypted key\n")
                        continue
                    
                    password = getpass.getpass("\nEnter decryption password: ")
                    
                    try:
                        private_key = self.btc_client.decrypt_wallet(encrypted_key, password)
                        
                        # Update current wallet - keep address and format, only decrypt private key
                        self.current_wallet = {
                            "address": self.current_wallet["address"],
                            "private_key": private_key,
                            "format": self.wallet_format
                        }
                        
                        print(f"\n🔓 Private key decrypted successfully!")
                        print(f"Address: {self.current_wallet['address']}")
                        print(f"Private Key: {private_key}")
                        print(f"Format: {self.wallet_format}\n")
                    except Exception as e:
                        print(f"\n⚠️ Error decrypting private key: {str(e)}")
                
                elif command == "send":
                    if len(args) < 2:
                        print("\n⚠️ Usage: send <to_address> <amount> [fee]\n")
                        continue
                    
                    if not self.current_wallet:
                        print("\n⚠️ No wallet loaded\n")
                        continue
                    
                    to_address = args[0]
                    amount = float(args[1])
                    fee = int(args[2]) if len(args) > 2 else 500  # Default fee in satoshis
                    
                    if "private_key" in self.current_wallet:
                        # Need to encrypt first
                        print("\n⚠️ Private key must be encrypted for security.")
                        print("Encrypting wallet first...\n")
                        
                        try:
                            private_key = self.current_wallet["private_key"]
                            # Generate a secure password for this transaction
                            password = getpass.getpass("Enter a password for transaction encryption (leave empty to generate): ")
                            if not password:
                                password = None
                                
                            encrypted_data = self.btc_client.encrypt_wallet(private_key, password)
                            encrypted_key = encrypted_data["encrypted_key"]
                            password = encrypted_data["password_reference"]
                            
                            print(f"Password: {password}")
                            print("IMPORTANT: Save this password securely!\n")
                            
                        except Exception as e:
                            print(f"\n⚠️ Error encrypting wallet: {str(e)}")
                            continue
                    else:
                        encrypted_key = self.current_wallet.get("encrypted_key")
                        if not encrypted_key:
                            print("\n⚠️ Wallet has no encrypted key\n")
                            continue
                        
                        password = getpass.getpass("\nEnter wallet password: ")
                    
                    try:
                        tx_hash = self.btc_client.send_transaction(
                            encrypted_key, 
                            password, 
                            to_address, 
                            amount,
                            fee=fee
                        )
                        
                        print(f"\n✅ Transaction sent successfully!")
                        print(f"Transaction Hash: {tx_hash}")
                        print(f"Sending {amount} BTC to {to_address}\n")
                    except Exception as e:
                        print(f"\n⚠️ Error sending transaction: {str(e)}")
                
                elif command == "network":
                    if not args:
                        print(f"\n🔹 Current network: {self.btc_client.network}")
                        print("\n⚠️ Usage: network <name> (bitcoin, testnet)\n")
                        continue
                    
                    network = args[0].lower()
                    if network not in ["bitcoin", "testnet"]:
                        print("\n⚠️ Invalid network. Available networks: bitcoin, testnet\n")
                        continue
                    
                    try:
                        self.btc_client = BitcoinClient(network=network)
                        print(f"\n✅ Switched to Bitcoin network: {network}\n")
                        # Clear current wallet as it might not be valid on the new network
                        self.current_wallet = None
                    except Exception as e:
                        print(f"\n⚠️ Error connecting to network: {str(e)}")

                elif command == "tx":
                    if not args:
                        print("\n⚠️ Usage: tx <hash>\n")
                        continue
                    tx_hash = args[0]
                    try:
                        # Add this method to BitcoinClient
                        tx_info = self.btc_client.get_transaction_info(tx_hash)
                        print(f"\n🔍 Transaction Status:")
                        for key, value in tx_info.items():
                           print(f"{key}: {value}")
                           print()
                    except Exception as e:
                       print(f"\n⚠️ Error checking transaction: {str(e)}")

                else:
                    print(f"\n❌ Unknown Bitcoin command: {command}")
                    self.print_btc_help()
                    
            except KeyboardInterrupt:
                print("\n\n↩️ Returning to main menu\n")
                break
            except Exception as e:
                print(f"\n⚠️ Error: {str(e)}\n")
        
        return self.current_wallet
        
    def _get_witness_type(self):
        """Helper method to convert wallet format to witness type"""
        if self.wallet_format == "legacy":
            return "legacy"
        elif self.wallet_format == "segwit":
            return "segwit"
        elif self.wallet_format == "bech32":
            return "segwit"  # bech32 is also SegWit, but with a different encoding
        return "legacy"  # Default


"""
BITCOIN ADDRESS FORMAT DIFFERENCES
=================================

1. LEGACY (P2PKH)
   - Starts with "1" (e.g., 17bE4C9PioaZEFDWzvfhnCGisWCuGP5YC6)
   - Original Bitcoin address format (Pay-to-Public-Key-Hash)
   - Higher transaction fees due to larger transaction size
   - Most widely compatible with all wallets and exchanges
   - Uses Base58Check encoding

2. SEGWIT (P2SH-wrapped)
   - Starts with "3" (e.g., 3FZbgi29cpjq2GjdwV8eyHuJJnkLtktZc5)
   - Implements Segregated Witness inside a backward-compatible P2SH address
   - 30-40% cheaper transaction fees than legacy
   - Compatible with most modern wallets
   - Still uses Base58Check encoding

3. BECH32 (Native SegWit/P2WPKH)
   - Starts with "bc1" for mainnet (e.g., bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq)
   - Starts with "tb1" for testnet (e.g., tb1qm4t690ml6ae5ulnu9cne8jul7xx86tjdhhtxl7)
   - Native implementation of Segregated Witness (no backward-compatible wrapper)
   - Lowest transaction fees (up to 40% cheaper than legacy)
   - Better error detection due to improved encoding
   - May not be supported by older wallets or exchanges
   - Uses Bech32 encoding (more efficient than Base58Check)

KEY DIFFERENCES:
- Cost: Bech32 is cheapest, SegWit is middle, Legacy is most expensive
- Compatibility: Legacy has widest support, Bech32 has least compatibility with older systems
- Error Detection: Bech32 has better error detection than other formats
- Transaction Size: Bech32 transactions are smallest, Legacy are largest
- Security: All are secure, but Bech32 addresses are harder to mistype due to better error detection

Each private key can generate addresses in any of these formats - they're just different ways of 
representing the same underlying ownership information. The formats only affect how transactions 
are structured on the blockchain.
"""