"""Expense tracker business logic and calculations."""

from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

from expense_tracker.models import Expense
from expense_tracker.storage import Storage
from expense_tracker.validators import (
    ValidationError,
    validate_amount,
    validate_category,
    validate_date,
    validate_id,
    validate_month,
)


class ExpenseTracker:
    """Core manager handling all business operations for expenses and budgets."""

    def __init__(self, storage_path: str = "expenses.json"):
        self.storage = Storage(storage_path)

    def _next_id(self, expenses: List[Expense]) -> int:
        """Compute the next sequential integer ID."""
        if not expenses:
            return 1
        return max(e.id for e in expenses) + 1

    def add_expense(
        self,
        amount: Any,
        category: str,
        date_str: Optional[str] = None,
        note: str = "",
    ) -> Tuple[Expense, Optional[str]]:
        """
        Add a new expense.
        Returns a tuple: (created_expense, budget_warning_message_or_None).
        """
        valid_amount = validate_amount(amount)
        valid_cat = validate_category(category)

        if not date_str:
            valid_date = datetime.now().strftime("%Y-%m-%d")
        else:
            valid_date = validate_date(date_str)

        expenses = self.storage.load_expenses()
        budgets = self.storage.load_budgets()

        new_id = self._next_id(expenses)
        new_expense = Expense(
            id=new_id,
            amount=valid_amount,
            category=valid_cat,
            date=valid_date,
            note=note.strip() if note else "",
        )

        expenses.append(new_expense)
        self.storage.save_expenses_and_budgets(expenses, budgets)

        # Check budget limit warning
        month = valid_date[:7]
        warning = self._check_budget_warning(expenses, budgets, month)

        return new_expense, warning

    def list_expenses(
        self,
        category: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[Expense]:
        """Filter and retrieve expenses."""
        expenses = self.storage.load_expenses()

        if category:
            cat_norm = category.strip().lower()
            expenses = [e for e in expenses if e.category.lower() == cat_norm]

        if start_date:
            valid_start = validate_date(start_date)
            expenses = [e for e in expenses if e.date >= valid_start]

        if end_date:
            valid_end = validate_date(end_date)
            expenses = [e for e in expenses if e.date <= valid_end]

        # Sort by date ascending, then ID ascending
        expenses.sort(key=lambda x: (x.date, x.id))
        return expenses

    def get_expense(self, expense_id: Any) -> Expense:
        """Retrieve single expense by ID."""
        expenses = self.storage.load_expenses()
        existing_ids = {e.id for e in expenses}
        valid_id = validate_id(expense_id, existing_ids)
        for e in expenses:
            if e.id == valid_id:
                return e
        raise ValidationError(f"Expense with ID {expense_id} was not found.")

    def edit_expense(
        self,
        expense_id: Any,
        amount: Optional[Any] = None,
        category: Optional[str] = None,
        date_str: Optional[str] = None,
        note: Optional[str] = None,
    ) -> Tuple[Expense, Optional[str]]:
        """Edit an existing expense by ID."""
        expenses = self.storage.load_expenses()
        budgets = self.storage.load_budgets()
        existing_ids = {e.id for e in expenses}
        valid_id = validate_id(expense_id, existing_ids)

        target = None
        for exp in expenses:
            if exp.id == valid_id:
                target = exp
                break

        if not target:
            raise ValidationError(f"Expense with ID {expense_id} was not found.")

        if amount is not None:
            target.amount = validate_amount(amount)
        if category is not None:
            target.category = validate_category(category)
        if date_str is not None:
            target.date = validate_date(date_str)
        if note is not None:
            target.note = note.strip()

        self.storage.save_expenses_and_budgets(expenses, budgets)

        month = target.date[:7]
        warning = self._check_budget_warning(expenses, budgets, month)

        return target, warning

    def delete_expense(self, expense_id: Any) -> Expense:
        """Delete an expense by ID."""
        expenses = self.storage.load_expenses()
        budgets = self.storage.load_budgets()
        existing_ids = {e.id for e in expenses}
        valid_id = validate_id(expense_id, existing_ids)

        target = None
        remaining = []
        for exp in expenses:
            if exp.id == valid_id:
                target = exp
            else:
                remaining.append(exp)

        if not target:
            raise ValidationError(f"Expense with ID {expense_id} was not found.")

        self.storage.save_expenses_and_budgets(remaining, budgets)
        return target

    def summary(
        self,
        category: Optional[str] = None,
        month: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Calculate total spend, spend by category, and spend by month.
        """
        expenses = self.storage.load_expenses()

        if category:
            cat_norm = category.strip().lower()
            expenses = [e for e in expenses if e.category.lower() == cat_norm]

        if month:
            valid_month = validate_month(month)
            expenses = [e for e in expenses if e.date.startswith(valid_month)]

        total_spend = sum(e.amount for e in expenses)

        by_category: Dict[str, float] = {}
        by_month: Dict[str, float] = {}

        for e in expenses:
            by_category[e.category] = round(by_category.get(e.category, 0.0) + e.amount, 2)
            m = e.date[:7]
            by_month[m] = round(by_month.get(m, 0.0) + e.amount, 2)

        return {
            "count": len(expenses),
            "total_spend": round(total_spend, 2),
            "by_category": by_category,
            "by_month": dict(sorted(by_month.items())),
        }

    # --- Stretch Goals ---

    def set_budget(self, month: str, limit_amount: Any) -> float:
        """Set monthly budget limit."""
        valid_month = validate_month(month)
        valid_limit = validate_amount(limit_amount)

        expenses = self.storage.load_expenses()
        budgets = self.storage.load_budgets()
        budgets[valid_month] = valid_limit

        self.storage.save_expenses_and_budgets(expenses, budgets)
        return valid_limit

    def get_budget_status(self, month: str) -> Dict[str, Any]:
        """Get budget status and comparison with actual spending."""
        valid_month = validate_month(month)
        expenses = self.storage.load_expenses()
        budgets = self.storage.load_budgets()

        month_expenses = [e for e in expenses if e.date.startswith(valid_month)]
        spent = round(sum(e.amount for e in month_expenses), 2)
        limit = budgets.get(valid_month)

        status = {
            "month": valid_month,
            "spent": spent,
            "limit": limit,
            "exceeded": False,
            "remaining": None,
        }

        if limit is not None:
            status["remaining"] = round(limit - spent, 2)
            if spent > limit:
                status["exceeded"] = True

        return status

    def _check_budget_warning(
        self, expenses: List[Expense], budgets: Dict[str, float], month: str
    ) -> Optional[str]:
        """Check if total spending exceeds the budget for the month."""
        if month not in budgets:
            return None
        limit = budgets[month]
        month_total = sum(e.amount for e in expenses if e.date.startswith(month))
        if month_total > limit:
            overage = month_total - limit
            return (
                f"⚠️  WARNING: Monthly budget for {month} exceeded! "
                f"Spent: ${month_total:.2f} | Limit: ${limit:.2f} | Over by: ${overage:.2f}"
            )
        return None

    def export_csv(
        self,
        output_file: str = "expenses.csv",
        category: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Tuple[int, str]:
        """Export filtered expenses to a CSV file."""
        filtered = self.list_expenses(
            category=category, start_date=start_date, end_date=end_date
        )
        self.storage.export_to_csv(filtered, output_file)
        return len(filtered), output_file

    def generate_monthly_report(self, month: str) -> str:
        """Generate a formatted monthly text report."""
        valid_month = validate_month(month)
        expenses = self.storage.load_expenses()
        month_expenses = [e for e in expenses if e.date.startswith(valid_month)]
        month_expenses.sort(key=lambda x: (x.date, x.id))

        budget_info = self.get_budget_status(valid_month)
        total_spent = sum(e.amount for e in month_expenses)

        # Categorical breakdown
        cat_map: Dict[str, float] = {}
        for exp in month_expenses:
            cat_map[exp.category] = cat_map.get(exp.category, 0.0) + exp.amount

        lines = [
            "=" * 50,
            f"          EXPENSE REPORT - {valid_month}",
            "=" * 50,
            f"Total Transactions: {len(month_expenses)}",
            f"Total Spent:        ${total_spent:.2f}",
        ]

        if budget_info["limit"] is not None:
            limit = budget_info["limit"]
            lines.append(f"Budget Limit:       ${limit:.2f}")
            rem = budget_info["remaining"]
            if budget_info["exceeded"]:
                lines.append(f"Budget Status:      ⚠️ EXCEEDED by ${abs(rem):.2f}")
            else:
                lines.append(f"Budget Status:      ✅ Under budget by ${rem:.2f}")
        else:
            lines.append("Budget Limit:       (No budget configured)")

        lines.append("-" * 50)
        lines.append("SPENDING BY CATEGORY:")
        if not cat_map:
            lines.append("  (No expenses recorded)")
        else:
            for cat, amt in sorted(cat_map.items(), key=lambda x: -x[1]):
                pct = (amt / total_spent * 100) if total_spent > 0 else 0
                lines.append(f"  • {cat:<15}: ${amt:>8.2f}  ({pct:>5.1f}%)")

        lines.append("-" * 50)
        lines.append("RECENT TRANSACTIONS:")
        if not month_expenses:
            lines.append("  (None)")
        else:
            for exp in month_expenses:
                note_str = f" - {exp.note}" if exp.note else ""
                lines.append(f"  [{exp.id:>3}] {exp.date} | {exp.category:<12} | ${exp.amount:>7.2f}{note_str}")

        lines.append("=" * 50)
        return "\n".join(lines)
