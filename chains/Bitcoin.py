from bitcoinlib.wallets import Wallet as BtcWallet
from bitcoinlib.wallets import wallet_create_or_open
from bitcoinlib.transactions import Transaction
from bitcoinlib.services.services import Service
from .util import  encrypt_key, decrypt_key,derive_btc
class BitcoinClient:
    def __init__(self,network="bitcoin"):
        self.network=network
        self.service = Service(network=self.network)
    
    def create_wallet(mnemonic:str,witness_type="legacy")->dict:
        """Generate Bitcoin wallet using Go core."""
        address, privkey_wif = derive_btc(mnemonic,  witness_type=witness_type)
        return {"address": address, "private_key": privkey_wif}
    
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
        
    def get_balance(self, address: str) -> float:
        """Get BTC balance for address."""
        balance_satoshi = self.service.getbalance(address)
        return balance_satoshi / 100000000  # Convert satoshis to BTC
    
    def send_transaction(
        self, 
        encrypted_privkey: str, 
        password: str, 
        to_address: str, 
        amount: float,
        fee: int = 500 
    )->str:
        """Decrypt key and send BTC."""
        # Decrypt using Go core
        privkey= self.decrypt_wallet(encrypted_privkey, password)
        
        # Import key to temporary wallet
        wallet_name = f"temp_{to_address[:8]}"
        wallet = wallet_create_or_open(
            wallet_name,
            keys=privkey,
            network=self.network,
            witness_type='segwit'  # Use segwit for lower fees
        )
        
        # Update wallet UTXOs
        wallet.scan()
        
        # Build and send transaction
        amount_satoshi = int(amount * 100000000)  # Convert BTC to satoshis
        tx = wallet.send_to(to_address, amount_satoshi, fee=fee)
        
        # Clean up - delete temporary wallet
        wallet.delete_wallet()
        
        return tx.txid
    def get_transaction_info(self, tx_hash):
        """Get transaction details from hash."""
        try:
          tx = self.service.gettransaction(tx_hash)
          return {
            "hash": tx_hash,
            "confirmations": tx.get("confirmations", 0),
            "time": tx.get("time"),
            "amount": tx.get("amount"),
            "fee": tx.get("fee"),
            "status": "confirmed" if tx.get("confirmations", 0) > 0 else "pending"
          }
        except Exception as e:
          return {"hash": tx_hash, "status": "error", "error": str(e)}
    