# transaction.py
from dataclasses import dataclass
from typing import Optional, Any
from datetime import datetime

@dataclass
class Transaction:
    """Representation of a blockchain transaction."""
    tx_hash: str
    chain: str
    from_address: str
    to_address: str
    amount: float
    status: str  # pending, confirmed, failed
    timestamp: Optional[datetime] = None
    confirmations: int = 0
    fee: Optional[float] = None
    block_number: Optional[int] = None
    raw_data: Optional[dict] = None
    
    def to_dict(self) -> dict:
        """Convert transaction to dictionary."""
        result = {
            "tx_hash": self.tx_hash,
            "chain": self.chain,
            "from_address": self.from_address,
            "to_address": self.to_address,
            "amount": self.amount,
            "status": self.status,
            "confirmations": self.confirmations
        }
        
        if self.timestamp:
            result["timestamp"] = self.timestamp.isoformat()
        
        if self.fee is not None:
            result["fee"] = self.fee
            
        if self.block_number is not None:
            result["block_number"] = self.block_number
            
        return result
    
    @classmethod
    def from_dict(cls, data: dict) -> "Transaction":
        """Create transaction from dictionary."""
        # Handle timestamp conversion
        timestamp = None
        if "timestamp" in data and data["timestamp"]:
            if isinstance(data["timestamp"], str):
                timestamp = datetime.fromisoformat(data["timestamp"])
            else:
                timestamp = datetime.fromtimestamp(data["timestamp"])
                
        return cls(
            tx_hash=data["tx_hash"],
            chain=data["chain"],
            from_address=data["from_address"],
            to_address=data["to_address"],
            amount=float(data["amount"]),
            status=data["status"],
            timestamp=timestamp,
            confirmations=int(data.get("confirmations", 0)),
            fee=float(data["fee"]) if "fee" in data else None,
            block_number=int(data["block_number"]) if "block_number" in data else None,
            raw_data=data.get("raw_data")
        )