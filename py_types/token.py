# token.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class Token:
    """Representation of a blockchain token."""
    symbol: str
    chain: str
    contract_address: Optional[str] = None
    decimals: int = 18
    name: Optional[str] = None
    icon_url: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert token to dictionary."""
        result = {
            "symbol": self.symbol,
            "chain": self.chain,
            "decimals": self.decimals
        }
        
        if self.contract_address:
            result["contract_address"] = self.contract_address
            
        if self.name:
            result["name"] = self.name
            
        if self.icon_url:
            result["icon_url"] = self.icon_url
            
        return result
    
    @classmethod
    def from_dict(cls, data: dict) -> "Token":
        """Create token from dictionary."""
        return cls(
            symbol=data["symbol"],
            chain=data["chain"],
            contract_address=data.get("contract_address"),
            decimals=int(data.get("decimals", 18)),
            name=data.get("name"),
            icon_url=data.get("icon_url")
        )
    
    @property
    def is_native(self) -> bool:
        """Check if this is a native token (e.g., ETH, BTC)."""
        return self.contract_address is None