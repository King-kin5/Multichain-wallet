import sys
from chains.util import call_go_core, generate_mnemonic,derive_key
from py_types.wallet import Wallet
from utils.ethereum_mode import EthereumMode

def print_help():
    print("\nAvailable commands:")
    print("  generate       - Create new BIP-39 mnemonic phrase")
    print("  derive - Derive wallet for chain ")
    print("  exit           - Quit the program")
    print("  help           - Show this help message\n")


def get_mnemonic_from_user(args, last_mnemonic):
    """Helper to extract mnemonic from args or prompt user"""
    if args.strip():
        return args.strip()
    
    if last_mnemonic:
        print(f"\n🔍 Last generated mnemonic available. Use it? (y/n)")
        if input("> ").strip().lower() == 'y':
            return last_mnemonic
    
    print("\nEnter mnemonic phrase:")
    return input("> ").strip()

def handle_eth_command(args, last_mnemonic):
    """Handle Ethereum wallet derivation"""
    mnemonic = get_mnemonic_from_user(args, last_mnemonic)
    try:
        address, private_key = derive_key(mnemonic)
        print(f"\n🔑 Ethereum Wallet:")
        print(f"Address: {address}")
        print(f"Private Key: {private_key}\n")
    except Exception as e:
        print(f"\n⚠️  Error deriving Ethereum keys: {str(e)}")

def main():
    print("\n🌟 Multichain Wallet CLI 🌟")
    print("Type 'help' for available commands\n")
    last_mnemonic = None
    eth_mode = EthereumMode()
    while True:
        try:
            command = input("wallet> ").strip().lower()

            
            if not command:
                continue
                
            parts = command.split(maxsplit=1)
            command = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""

            if command == "exit":
                print("\n👋 Goodbye!\n")
                break
                
            elif command == "help":
                print_help()
                
            elif command.startswith("generate"):
                last_mnemonic = generate_mnemonic()
                print(f"\n🆕 Generated Mnemonic: {last_mnemonic}")

            
            elif command == "ethh":
                handle_eth_command(args, last_mnemonic)    
                   
            elif command == "eth":
                # Pass the current wallet state to the Ethereum mode
                # and get the updated wallet state when it returns
                eth_mode.start(last_mnemonic)    
            else:
                print(f"\n❌ Unknown command: {command}")
                print_help()
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!\n")
            break
        except Exception as e:
            print(f"\n⚠️  Error: {str(e)}\n")

if __name__ == "__main__":
    main()