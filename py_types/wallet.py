# wallet.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class Wallet:
    """Representation of a blockchain wallet."""
    address: str
    chain: str
    private_key: Optional[str] = None
    encrypted_key: Optional[str] = None
    public_key: Optional[str] = None
    
    def is_encrypted(self) -> bool:
        """Check if the wallet has an encrypted key."""
        return self.encrypted_key is not None and self.private_key is None
    
    def to_dict(self, include_private: bool = False) -> dict:
        """Convert wallet to dictionary."""
        result = {
            "address": self.address,
            "chain": self.chain,
            "public_key": self.public_key
        }
        
        if include_private and self.private_key:
            result["private_key"] = self.private_key
        
        if self.encrypted_key:
            result["encrypted_key"] = self.encrypted_key
            
        return result
    
    @classmethod
    def from_dict(cls, data: dict) -> "Wallet":
        """Create wallet from dictionary."""
        return cls(
            address=data["address"],
            chain=data["chain"],
            private_key=data.get("private_key"),
            encrypted_key=data.get("encrypted_key"),
            public_key=data.get("public_key")
        )