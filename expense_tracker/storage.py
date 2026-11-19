"""Persistent storage for expenses and budgets using JSON and CSV export."""

import csv
import json
import os
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional

from expense_tracker.models import Expense, Budget
from expense_tracker.validators import ValidationError


class Storage:
    """Handles JSON file persistence with atomic writing."""

    def __init__(self, filepath: str = "expenses.json"):
        self.filepath = Path(filepath)

    def _ensure_directory(self) -> None:
        """Ensure parent directory exists."""
        self.filepath.parent.mkdir(parents=True, exist_ok=True)

    def load_data(self) -> Dict[str, Any]:
        """Load data from JSON file. Returns empty structure if file does not exist."""
        if not self.filepath.exists():
            return {"expenses": [], "budgets": {}}

        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, dict):
                    # Fallback if file was a plain array
                    if isinstance(data, list):
                        return {"expenses": data, "budgets": {}}
                    return {"expenses": [], "budgets": {}}
                data.setdefault("expenses", [])
                data.setdefault("budgets", {})
                return data
        except (json.JSONDecodeError, OSError) as e:
            raise ValidationError(f"Failed to read data file '{self.filepath}': {e}")

    def save_data(self, data: Dict[str, Any]) -> None:
        """Save data atomically using a temp file to prevent corruption."""
        self._ensure_directory()
        dir_name = self.filepath.parent
        # Create temp file in same directory for atomic replace
        with tempfile.NamedTemporaryFile("w", dir=dir_name, delete=False, encoding="utf-8") as tmp:
            json.dump(data, tmp, indent=2)
            temp_path = tmp.name

        os.replace(temp_path, self.filepath)

    def load_expenses(self) -> List[Expense]:
        """Load and return list of Expense instances."""
        data = self.load_data()
        return [Expense.from_dict(item) for item in data.get("expenses", [])]

    def save_expenses_and_budgets(self, expenses: List[Expense], budgets: Dict[str, float]) -> None:
        """Save all expenses and budgets."""
        data = {
            "expenses": [e.to_dict() for e in expenses],
            "budgets": budgets,
        }
        self.save_data(data)

    def load_budgets(self) -> Dict[str, float]:
        """Load month -> budget amount dictionary."""
        data = self.load_data()
        return data.get("budgets", {})

    @staticmethod
    def export_to_csv(expenses: List[Expense], output_filepath: str) -> None:
        """Export given expenses to CSV format."""
        out_path = Path(output_filepath)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(out_path, "w", newline="", encoding="utf-8") as csvfile:
                fieldnames = ["ID", "Date", "Category", "Amount", "Note"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for exp in expenses:
                    writer.writerow({
                        "ID": exp.id,
                        "Date": exp.date,
                        "Category": exp.category,
                        "Amount": f"{exp.amount:.2f}",
                        "Note": exp.note,
                    })
        except OSError as e:
            raise ValidationError(f"Failed to write CSV file '{output_filepath}': {e}")
