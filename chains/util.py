import subprocess
import json
from pathlib import Path
import os
from py_types.wallet import Wallet

# Print the current working directory
print(f"Current working directory: {os.getcwd()}")

GO_CORE_PATH=Path("go-core/core.exe")
# Print the absolute path to the executable
print(f"Absolute path to go core: {os.path.abspath(GO_CORE_PATH)}")

def call_go_core(args:list)->str:
    """Execute go command with fallback to interactive mode"""
    try:
        # First try direct command execution
        print(f"Executing: {str(GO_CORE_PATH)} {' '.join(args)}")
        
        result = subprocess.run(
            [str(GO_CORE_PATH)] + args,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5  # Add timeout to prevent hanging
        )
        
    
        
        return result.stdout.strip()
    
    except Exception as e:
        print(f"General exception: {str(e)}")
        raise
    

def generate_mnemonic()->str:
    """Generate a BIP-39 mnemonic"""
    # Debug: Print when function is called                 
    return call_go_core(["generate-mnemonic"])
 

def encrypt_key(privkey_hex:str,password:str)->str:
    """Encrypt a private key using Go core"""
    return call_go_core(["encrypt"],privkey_hex,password)

def decrypt_key(privkey_hex:str,password:str)->str:
    """Decrypt a private key using Go core"""
    return call_go_core(["decrypt"],privkey_hex,password)


def derive_key(mnemonic: str) -> tuple[str, str]:
    """
    Derive address and private key for a specific blockchain.
    
    Args:
        chain_type: Type of blockchain (eth, btc, sol)
        mnemonic: BIP-39 mnemonic phrase
        
    Returns:
        Tuple of (address, private_key)
    """
    output = call_go_core(["derive-key", mnemonic])
    lines = output.split("\n")
    
    # Parse output lines for address and private key
    if len(lines) < 2:
        raise ValueError(f"Unexpected output format: {output}")
    
    address_line, privkey_line = lines[0], lines[1]
    
    return (
        address_line.split(": ")[1].strip(),  # Address
        privkey_line.split(": ")[1].strip()   # Private Key
    )
    