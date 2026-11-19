"""Data models for expenses and budgets."""

from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any


@dataclass
class Expense:
    id: int
    amount: float
    category: str
    date: str  # Format: YYYY-MM-DD
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert expense instance to dictionary."""
        return {
            "id": self.id,
            "amount": round(float(self.amount), 2),
            "category": self.category.strip(),
            "date": self.date,
            "note": self.note.strip() if self.note else "",
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Expense":
        """Instantiate Expense from dictionary."""
        return cls(
            id=int(data["id"]),
            amount=round(float(data["amount"]), 2),
            category=str(data["category"]),
            date=str(data["date"]),
            note=str(data.get("note", "")),
        )


@dataclass
class Budget:
    month: str  # Format: YYYY-MM
    limit: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "month": self.month,
            "limit": round(float(self.limit), 2),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Budget":
        return cls(
            month=str(data["month"]),
            limit=round(float(data["limit"]), 2),
        )
