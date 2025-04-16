import sys
from chains.util import call_go_core, generate_mnemonic,derive_key
from py_types.wallet import Wallet
from utils.bitcoin_mode import BitcoinMode
from utils.ethereum_mode import EthereumMode

def print_welcome():
    print("\n" + "="*60)
    print(" " * 20 + "🌟 MULTICHAIN WALLET 🌟")
    print("="*60)
    print("\nWelcome to the Multichain Wallet CLI!")
    print("A secure and user-friendly wallet for multiple blockchains.\n")

def print_help():
    print("\n" + "="*60)
    print(" " * 20 + "📚 COMMAND REFERENCE 📚")
    print("="*60)
    print("\n🔹 Blockchain Modes:")
    print("  btc           - Enter Bitcoin mode")
    print("\n  eth           - Enter Ethereum mode")    
    print("\n🔹 General Commands:")
    print("  generate      - Generate new BIP-39 mnemonic phrase")
    print("  help          - Show this help message")
    print("  exit          - Exit the program")
    print("\n" + "="*60)
    print("\n💡 Tips:")
    print("  - Use 'btc' or 'eth' to enter the respective blockchain mode")
    print("  - Each mode has its own set of commands (type 'help' in that mode)")
    print("  - Generated mnemonics can be used to create wallets in either mode")
    print("  - Always encrypt your wallets for security")
    print("  - Keep your mnemonics and passwords safe and secure\n")

def print_goodbye():
    print("\n" + "="*60)
    print(" " * 20 + "👋 GOODBYE! 👋")
    print("="*60)
    print("\nThank you for using Multichain Wallet!")
    print("Remember to keep your private keys and mnemonics safe.\n")

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
    print_welcome()
    last_mnemonic = None
    eth_mode = EthereumMode()
    btc_mode = BitcoinMode()
    
    while True:
        try:
            command = input("\nwallet> ").strip().lower()
            
            if not command:
                continue
                
            parts = command.split(maxsplit=1)
            command = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""

            if command == "exit":
                print_goodbye()
                break
                
            elif command == "help":
                print_help()
                
            elif command.startswith("generate"):
                last_mnemonic = generate_mnemonic()
                print("\n" + "="*60)
                print(" " * 20 + "🆕 NEW MNEMONIC 🆕")
                print("="*60)
                print(f"\nGenerated Mnemonic: {last_mnemonic}")
                print("\n⚠️ IMPORTANT: Save this mnemonic securely!")
                print("It can be used to recover your wallet if lost.\n")

            elif command == "eth":
                # Pass the current wallet state to the Ethereum mode
                # and get the updated wallet state when it returns
                eth_mode.start(last_mnemonic)

            elif command == "btc":
                # Pass the current wallet state to the Bitcoin mode
                # and get the updated wallet state when it returns
                btc_mode.start(last_mnemonic)
            else:
                print("\n" + "="*60)
                print(" " * 20 + "⚠️ UNKNOWN COMMAND ⚠️")
                print("="*60)
                print(f"\nUnknown command: {command}")
                print("Type 'help' to see available commands\n")

        except KeyboardInterrupt:
            print_goodbye()
            break
        except Exception as e:
            print("\n" + "="*60)
            print(" " * 20 + "⚠️ ERROR ⚠️")
            print("="*60)
            print(f"\nError: {str(e)}\n")

if __name__ == "__main__":
    main()