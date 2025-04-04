import getpass
from chains.Ethereum import Ethereumchain
from chains.util import derive_key, generate_mnemonic

class EthereumMode:
    def __init__(self):
        self.eth_client = None
        self.current_wallet = None

    def initialize_ethereum(self, rpc_url=None):
        """Initialize Ethereum client with default or specified RPC URL"""
        if not rpc_url:
            # Default to Infura or other provider
            rpc_url = "https://mainnet.infura.io/v3/37f0d54ba4384c3ab9c33d69ae94c604"  # Replace with your key
        
        try:
            self.eth_client = Ethereumchain(rpc_url)
            print(f"\n✅ Connected to Ethereum node")
            return True
        except Exception as e:
            print(f"\n⚠️ Failed to connect to Ethereum node: {str(e)}")
            return False

    def print_eth_help(self):
        print("\nEthereum commands:")
        print("  wallet        - Show current wallet info")
        print("  balance <addr> - Check ETH balance (uses current wallet if no address provided)")
        print("  create <mnemonic> - Create a new wallet (generates mnemonic if none provided)")
        print("  encrypt       - Encrypt the current wallet")
        print("  decrypt       - Decrypt an encrypted wallet")
        print("  send <to> <amount> - Send ETH to an address")
        print("  tx <hash>     - Check transaction status")
        print("  connect <url> - Connect to a different Ethereum node")
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

    def handle_eth_command(self, args, last_mnemonic):
        """Handle Ethereum wallet derivation"""
        mnemonic = self.get_mnemonic_from_user(args, last_mnemonic)
        try:
            address, private_key = derive_key(mnemonic)
            print(f"\n🔑 Ethereum Wallet:")
            print(f"Address: {address}")
            print(f"Private Key: {private_key}\n")
        except Exception as e:
            print(f"\n⚠️ Error deriving Ethereum keys: {str(e)}")

    def start(self, last_mnemonic=None):
        """Handle Ethereum-specific commands"""
        # Initialize Ethereum client if not already done
        if not self.eth_client:
            if not self.initialize_ethereum():
                return
        
        print("\n🔹 Ethereum Mode 🔹")
        print("Type 'help' for available Ethereum commands\n")
        
        while True:
            try:
                command = input("eth> ").strip().lower()
                
                if not command:
                    continue
                    
                parts = command.split(maxsplit=2)
                command = parts[0].lower()
                args = parts[1:] if len(parts) > 1 else []
                
                if command == "back":
                    print("\n↩️ Returning to main menu\n")
                    break
                    
                elif command == "help":
                    self.print_eth_help()
                
                elif command == "wallet":
                    if self.current_wallet:
                        print(f"\n👛 Current Wallet:")
                        print(f"Address: {self.current_wallet.get('address', 'N/A')}")
                        has_privkey = "Yes" if "private_key" in self.current_wallet else "No (Encrypted)"
                        print(f"Has Private Key: {has_privkey}\n")
                    else:
                        print("\n⚠️ No wallet loaded. Use 'create' or 'decrypt' command\n")
                
                elif command == "create":
                    mnemonic = args[0] if args else generate_mnemonic()
                    if not args:
                        print(f"\n🆕 Generated Mnemonic: {mnemonic}")
                    
                    try:
                        self.current_wallet = self.eth_client.create_wallet(mnemonic)
                        print(f"\n✅ Created new wallet:")
                        print(f"Address: {self.current_wallet['address']}")
                        print(f"Private Key: {self.current_wallet['private_key']}\n")
                    except Exception as e:
                        print(f"\n⚠️ Error creating wallet: {str(e)}")
                
                elif command == "balance":
                    address = args[0] if args else (self.current_wallet.get('address') if self.current_wallet else None)
                    
                    if not address:
                        print("\n⚠️ No address provided or wallet loaded\n")
                        continue
                    
                    try:
                        balance = self.eth_client.get_balance(address)
                        print(f"\n💰 ETH Balance for {address}: {balance} ETH\n")
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
                        encrypted_data = self.eth_client.encrypt_wallet(private_key, password)
                        
                        # Update current wallet
                        encrypted_wallet = {
                            "address": self.current_wallet["address"],
                            "encrypted_key": encrypted_data["encrypted_key"]
                        }
                        
                        self.current_wallet = encrypted_wallet
                        
                        print(f"\n🔒 Wallet encrypted successfully!")
                        print(f"Password: {encrypted_data['password_reference']}")
                        print("IMPORTANT: Save this password securely!\n")
                    except Exception as e:
                        print(f"\n⚠️ Error encrypting wallet: {str(e)}")
                
                elif command == "decrypt":
                    encrypted_key = None
                    
                    # Check if an encrypted key is provided in the command
                    if args:
                        encrypted_key = args[0]
                    # Otherwise use the current wallet's encrypted key if available
                    elif self.current_wallet and "encrypted_key" in self.current_wallet:
                        encrypted_key = self.current_wallet.get("encrypted_key")
                    
                    if not encrypted_key:
                        print("\n⚠️ No encrypted wallet loaded. Please provide encrypted key\n")
                        continue
                    
                    password = getpass.getpass("\nEnter decryption password: ")
                    
                    try:
                        private_key = self.eth_client.decrypt_wallet(encrypted_key, password)
                        
                        # This line might need adjustment based on how derive_key works
                        # If derive_key expects a mnemonic, we'd need a different approach
                        # For now, assuming derive_key can work with a private key directly
                        try:
                            address, _ = derive_key(private_key)
                        except:
                            # Alternative: derive address from private key using web3
                            account = self.eth_client.w3.eth.account.from_key(private_key)
                            address = account.address
                        
                        self.current_wallet = {
                            "address": address,
                            "private_key": private_key
                        }
                        
                        print(f"\n🔓 Wallet decrypted successfully!")
                        print(f"Address: {address}\n")
                    except Exception as e:
                        print(f"\n⚠️ Error decrypting wallet: {str(e)}")
                
                elif command == "send":
                    if len(args) < 2:
                        print("\n⚠️ Usage: send <to_address> <amount>\n")
                        continue
                    
                    if not self.current_wallet:
                        print("\n⚠️ No wallet loaded\n")
                        continue
                    
                    to_address = args[0]
                    amount = float(args[1])
                    
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
                                
                            encrypted_data = self.eth_client.encrypt_wallet(private_key, password)
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
                        gas_price = None
                        if len(args) > 2:
                            gas_price = float(args[2])
                        
                        tx_hash = self.eth_client.send_transaction(
                            encrypted_key, 
                            password, 
                            to_address, 
                            amount,
                            gas_price_gwei=gas_price
                        )
                        
                        print(f"\n✅ Transaction sent successfully!")
                        print(f"Transaction Hash: {tx_hash}")
                        print(f"Sending {amount} ETH to {to_address}\n")
                    except Exception as e:
                        print(f"\n⚠️ Error sending transaction: {str(e)}")
                
                elif command == "tx":
                    if not args:
                        print("\n⚠️ Usage: tx <hash>\n")
                        continue
                    
                    tx_hash = args[0]
                    
                    try:
                        status = self.eth_client.get_transaction_status(tx_hash)
                        print(f"\n🔍 Transaction Status:")
                        for key, value in status.items():
                            print(f"{key}: {value}")
                        print()
                    except Exception as e:
                        print(f"\n⚠️ Error checking transaction: {str(e)}")
                
                elif command == "connect":
                    if not args:
                        print("\n⚠️ Usage: connect <rpc_url>\n")
                        continue
                    
                    rpc_url = args[0]
                    
                    try:
                        self.eth_client = Ethereumchain(rpc_url)
                        print(f"\n✅ Connected to Ethereum node at {rpc_url}\n")
                    except Exception as e:
                        print(f"\n⚠️ Error connecting to node: {str(e)}")
                
                else:
                    print(f"\n❌ Unknown Ethereum command: {command}")
                    self.print_eth_help()
                    
            except KeyboardInterrupt:
                print("\n\n↩️ Returning to main menu\n")
                break
            except Exception as e:
                print(f"\n⚠️ Error: {str(e)}\n")
        
        return self.current_wallet