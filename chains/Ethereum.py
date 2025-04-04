from web3 import Web3
from .util import derive_key, encrypt_key, decrypt_key
from py_types.wallet import Wallet
from eth_account import Account
#from web3.middleware import geth_poa_middleware
import json

class Ethereumchain:
    def __init__(self, rpc_url=""):
        """Initialize Ethereum chain connection with optional RPC URL."""
        "https://mainnet.infura.io/v3/37f0d54ba4384c3ab9c33d69ae94c604"
        try:
            self.w3 = Web3(Web3.HTTPProvider(rpc_url))
            # Add middleware for POA chains like BSC, Polygon
            #self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Ethereum node: {str(e)}")

    def create_wallet(self, mnemonic: str) -> dict:
        """
        Generate Ethereum Wallet using Go core.
        
        Args:
            mnemonic (str): The mnemonic phrase to derive keys from
            
        Returns:
            dict: Contains the address and private key
        """
        try:
            address, priv_key = derive_key(mnemonic)
            return {"address": address, "private_key": priv_key}
        except Exception as e:
            raise ValueError(f"Failed to create wallet: {str(e)}")
    
    def get_balance(self, address: str) -> float:
        """
        Get ETH balance for address.
        
        Args:
            address (str): The Ethereum address to check balance for
            
        Returns:
            float: Balance in ether
        """
        try:
            balance_wei = self.w3.eth.get_balance(address)
            return self.w3.from_wei(balance_wei, "ether")
        except Exception as e:
            raise ValueError(f"Failed to get balance: {str(e)}")
    
    def encrypt_wallet(self, private_key: str, password: str = None) -> dict:
        """
        Encrypt the wallet's private key with a password.
        
        Args:
            private_key (str): The private key to encrypt
            password (str, optional): The password to use for encryption. If None, a password will be generated.
            
        Returns:
            dict: Contains the encrypted key and password reference
        """
        try:
            # If password is provided, use it; otherwise, encrypt_key will generate one
            if password:
                encrypted_key = encrypt_key(private_key, password)
                return {
                    "encrypted_key": encrypted_key,
                    "password_reference": password
                }
            else:
                encrypted_key, password = encrypt_key(private_key)
                return {
                    "encrypted_key": encrypted_key,
                    "password_reference": password
                }
        except Exception as e:
            raise ValueError(f"Failed to encrypt wallet: {str(e)}")
    
    def decrypt_wallet(self, encrypted_key: str, password: str) -> str:
        """
        Decrypt the wallet's private key with a password.
        
        Args:
            encrypted_key (str): The encrypted private key
            password (str): The password to decrypt the key
            
        Returns:
            str: The decrypted private key
        """
        try:
            decrypted_key = decrypt_key(encrypted_key, password)
            return decrypted_key
        except Exception as e:
            raise ValueError(f"Failed to decrypt wallet: {str(e)}")
    
    def send_transaction(
        self, 
        encrypted_privkey: str, 
        password: str, 
        to_address: str, 
        amount: float,
        gas_limit: int = 21000,
        gas_price_gwei: float = None
    ) -> str:
        """
        Decrypt key and send ETH.
        
        Args:
            encrypted_privkey (str): Encrypted private key
            password (str): Password to decrypt the key
            to_address (str): Recipient address
            amount (float): Amount of ETH to send
            gas_limit (int): Gas limit for transaction
            gas_price_gwei (float): Gas price in Gwei
            
        Returns:
            str: Transaction hash
        """
        try:
            # Decrypt using the correctly parameterized method
            privkey = self.decrypt_wallet(encrypted_privkey, password)
            
            # Build and send transaction
            account = self.w3.eth.account.from_key(privkey)
            
            # Get gas price if not specified
            if gas_price_gwei is None:
                gas_price = self.w3.eth.gas_price
            else:
                gas_price = self.w3.to_wei(gas_price_gwei, "gwei")
            
            # Build transaction
            tx = {
                "from": account.address,
                "to": to_address,
                "value": self.w3.to_wei(amount, "ether"),
                "gas": gas_limit,
                "gasPrice": gas_price,
                "nonce": self.w3.eth.get_transaction_count(account.address),
                "chainId": self.w3.eth.chain_id
            }
            
            # Sign and send transaction
            signed_tx = account.sign_transaction(tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            return tx_hash.hex()
        except Exception as e:
            raise ValueError(f"Failed to send transaction: {str(e)}")
    
    def get_transaction_status(self, tx_hash: str) -> dict:
        """
        Get transaction status and details.
        
        Args:
            tx_hash (str): Transaction hash to check
            
        Returns:
            dict: Transaction details including status
        """
        try:
            tx = self.w3.eth.get_transaction(tx_hash)
            receipt = None
            
            try:
                receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            except Exception:
                # Transaction not yet mined
                pass
            
            return {
                "hash": tx_hash,
                "from": tx["from"],
                "to": tx["to"],
                "value": self.w3.from_wei(tx["value"], "ether"),
                "block_number": receipt["blockNumber"] if receipt else None,
                "status": "confirmed" if receipt and receipt["status"] == 1 else 
                          "failed" if receipt and receipt["status"] == 0 else "pending",
                "confirmations": self.w3.eth.block_number - receipt["blockNumber"] if receipt else 0
            }
        except Exception as e:
            return {"hash": tx_hash, "status": "error", "error": str(e)}