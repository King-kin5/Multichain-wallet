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
 

def encrypt_key(privkey_hex:str, password:str=None)->str:
    """
    Encrypt a private key using Go core
    
    Args:
        privkey_hex (str): The private key to encrypt in hex format
        password (str, optional): Password to use for encryption. If None, one will be generated.
        
    Returns:
        str or tuple: If password is provided, returns encrypted key. If not, returns (encrypted_key, generated_password)
    """
    if password:
        # Use provided password
        return call_go_core(["encrypt", privkey_hex, password])
    else:
        # Generate a password
        import secrets
        generated_password = secrets.token_hex(16)
        encrypted_key = call_go_core(["encrypt", privkey_hex, generated_password])
        return encrypted_key, generated_password

def decrypt_key(encrypted_key:str, password:str)->str:
    """
    Decrypt a private key using Go core
    
    Args:
        encrypted_key (str): The encrypted private key in hex format
        password (str): Password to use for decryption
        
    Returns:
        str: Decrypted private key
    """
    return call_go_core(["decrypt", encrypted_key, password])


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
def derive_sol(mnemonic:str)->tuple[str,str]:
    """
    Derive address and private key for Solana.
    
    Args:
        mnemonic: BIP-39 mnemonic phrase
    """
    output = call_go_core(["derive-sol", mnemonic])
    lines = output.split("\n")
    
    # Parse output lines for address and private key
    if len(lines) < 2:
        raise ValueError(f"Unexpected output format: {output}")
    
    address_line, privkey_line = lines[0], lines[1]
    
    return (
        address_line.split(": ")[1].strip(),  # Address
        privkey_line.split(": ")[1].strip()   # Private Key
    )

def derive_btc(mnemonic: str, witness_type="legacy") -> tuple[str, str]:
    """
    Derive address and private key for Bitcoin.
    
    Args:
        mnemonic: BIP-39 mnemonic phrase
        witness_type: Address format (legacy, segwit, bech32)
    """
    output = call_go_core(["derive-btc", mnemonic, witness_type])
    lines = output.split("\n")
    
    # Parse output lines for address and private key
    if len(lines) < 2:
        raise ValueError(f"Unexpected output format: {output}")
    
    address_line, privkey_line = lines[0], lines[1]
    
    return (
        address_line.split(": ")[1].strip(),  # Address
        privkey_line.split(": ")[1].strip()   # Private Key
    )