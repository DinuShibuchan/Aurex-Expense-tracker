"""Input validation logic for the expense tracker."""

from datetime import datetime
from typing import Any, Iterable


class ValidationError(ValueError):
    """Raised when user input fails business rule validation."""
    pass


def validate_amount(raw_amount: Any) -> float:
    """Validate that amount is a positive numeric value."""
    try:
        amount = float(raw_amount)
    except (ValueError, TypeError):
        raise ValidationError(
            f"Invalid amount '{raw_amount}': Amount must be a valid number (e.g., 25.50)."
        )

    if amount <= 0:
        raise ValidationError(
            f"Invalid amount {amount:.2f}: Expense amount must be strictly greater than 0."
        )

    return round(amount, 2)


def validate_date(raw_date: Any) -> str:
    """Validate that date is a valid calendar date in YYYY-MM-DD format."""
    if not isinstance(raw_date, str) or not raw_date.strip():
        raise ValidationError("Date cannot be empty. Please provide date in YYYY-MM-DD format.")

    date_str = raw_date.strip()
    try:
        parsed = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise ValidationError(
            f"Invalid date '{date_str}': Must be a real calendar date in YYYY-MM-DD format (e.g., 2026-03-15)."
        )

    return parsed.strftime("%Y-%m-%d")


def validate_month(raw_month: Any) -> str:
    """Validate month in YYYY-MM format."""
    if not isinstance(raw_month, str) or not raw_month.strip():
        raise ValidationError("Month cannot be empty. Please provide month in YYYY-MM format.")

    month_str = raw_month.strip()
    try:
        parsed = datetime.strptime(month_str, "%Y-%m")
    except ValueError:
        raise ValidationError(
            f"Invalid month '{month_str}': Must be in YYYY-MM format (e.g., 2026-03)."
        )

    return parsed.strftime("%Y-%m")


def validate_category(raw_category: Any) -> str:
    """Validate that category is a non-empty string."""
    if not isinstance(raw_category, str) or not raw_category.strip():
        raise ValidationError("Category cannot be empty. Please specify a category name (e.g., Food, Transport).")

    return raw_category.strip().title()


def validate_id(raw_id: Any, existing_ids: Iterable[int]) -> int:
    """Validate that ID is a valid integer and exists in the store."""
    try:
        expense_id = int(raw_id)
    except (ValueError, TypeError):
        raise ValidationError(f"Invalid ID '{raw_id}': ID must be a positive integer.")

    if expense_id <= 0:
        raise ValidationError(f"Invalid ID '{expense_id}': ID must be greater than 0.")

    if expense_id not in existing_ids:
        raise ValidationError(f"Expense with ID {expense_id} was not found.")

    return expense_id
