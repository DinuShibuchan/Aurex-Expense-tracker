"""Comprehensive unit and edge-case tests for Expense Tracker."""

import csv
import json
import os
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from expense_tracker.tracker import ExpenseTracker
from expense_tracker.validators import (
    ValidationError,
    validate_amount,
    validate_date,
    validate_month,
    validate_id,
)


class TestValidators(unittest.TestCase):
    """Direct tests for validation functions and error conditions."""

    def test_validate_amount_valid_floats(self):
        self.assertEqual(validate_amount(10), 10.0)
        self.assertEqual(validate_amount("25.99"), 25.99)
        self.assertEqual(validate_amount(0.01), 0.01)

    def test_validate_amount_negative_raises_error(self):
        with self.assertRaises(ValidationError) as ctx:
            validate_amount(-15.50)
        self.assertIn("Expense amount must be strictly greater than 0", str(ctx.exception))

    def test_validate_amount_zero_raises_error(self):
        with self.assertRaises(ValidationError) as ctx:
            validate_amount(0)
        self.assertIn("Expense amount must be strictly greater than 0", str(ctx.exception))

    def test_validate_amount_non_numeric_raises_error(self):
        with self.assertRaises(ValidationError) as ctx:
            validate_amount("not-a-number")
        self.assertIn("Amount must be a valid number", str(ctx.exception))

    def test_validate_date_valid_format(self):
        self.assertEqual(validate_date("2026-03-15"), "2026-03-15")

    def test_validate_date_invalid_calendar_day_raises_error(self):
        # February 30 does not exist
        with self.assertRaises(ValidationError) as ctx:
            validate_date("2026-02-30")
        self.assertIn("Must be a real calendar date", str(ctx.exception))

    def test_validate_date_malformed_string_raises_error(self):
        with self.assertRaises(ValidationError) as ctx:
            validate_date("15/03/2026")
        self.assertIn("Must be a real calendar date in YYYY-MM-DD format", str(ctx.exception))

    def test_validate_month_valid_and_invalid(self):
        self.assertEqual(validate_month("2026-05"), "2026-05")
        with self.assertRaises(ValidationError):
            validate_month("2026-13")

    def test_validate_id_unknown_raises_error(self):
        with self.assertRaises(ValidationError) as ctx:
            validate_id(999, {1, 2, 3})
        self.assertIn("Expense with ID 999 was not found", str(ctx.exception))


class TestExpenseTracker(unittest.TestCase):
    """End-to-end tests for ExpenseTracker operations using isolated temporary storage."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.storage_file = Path(self.temp_dir.name) / "test_expenses.json"
        self.tracker = ExpenseTracker(str(self.storage_file))

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_add_expense_with_all_fields(self):
        expense, warning = self.tracker.add_expense(
            amount=45.50,
            category="Dining",
            date_str="2026-03-10",
            note="Team lunch",
        )
        self.assertEqual(expense.id, 1)
        self.assertEqual(expense.amount, 45.50)
        self.assertEqual(expense.category, "Dining")
        self.assertEqual(expense.date, "2026-03-10")
        self.assertEqual(expense.note, "Team lunch")
        self.assertIsNone(warning)

        # Verify persistent read from storage
        all_expenses = self.tracker.list_expenses()
        self.assertEqual(len(all_expenses), 1)
        self.assertEqual(all_expenses[0].id, 1)

    def test_add_expense_defaults_date_to_today(self):
        expense, _ = self.tracker.add_expense(amount=12.00, category="Coffee")
        today = datetime.now().strftime("%Y-%m-%d")
        self.assertEqual(expense.date, today)
        self.assertEqual(expense.note, "")

    def test_list_expenses_with_category_filter(self):
        self.tracker.add_expense(10.0, "Food", "2026-01-01")
        self.tracker.add_expense(20.0, "Transport", "2026-01-02")
        self.tracker.add_expense(30.0, "food", "2026-01-03")

        food_expenses = self.tracker.list_expenses(category="food")
        self.assertEqual(len(food_expenses), 2)
        for e in food_expenses:
            self.assertEqual(e.category, "Food")

    def test_list_expenses_with_date_range_filter(self):
        self.tracker.add_expense(10.0, "Books", "2026-01-05")
        self.tracker.add_expense(20.0, "Books", "2026-01-15")
        self.tracker.add_expense(30.0, "Books", "2026-01-25")

        filtered = self.tracker.list_expenses(
            start_date="2026-01-10", end_date="2026-01-20"
        )
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].amount, 20.0)

    def test_summary_aggregations(self):
        self.tracker.add_expense(50.0, "Food", "2026-01-10")
        self.tracker.add_expense(25.0, "Food", "2026-01-15")
        self.tracker.add_expense(100.0, "Travel", "2026-02-01")

        summary = self.tracker.summary()
        self.assertEqual(summary["count"], 3)
        self.assertEqual(summary["total_spend"], 175.0)
        self.assertEqual(summary["by_category"]["Food"], 75.0)
        self.assertEqual(summary["by_category"]["Travel"], 100.0)
        self.assertEqual(summary["by_month"]["2026-01"], 75.0)
        self.assertEqual(summary["by_month"]["2026-02"], 100.0)

    def test_edit_expense_updates_fields(self):
        exp, _ = self.tracker.add_expense(15.0, "Snacks", "2026-03-01", "Chips")
        updated, _ = self.tracker.edit_expense(
            expense_id=exp.id,
            amount=18.50,
            category="Groceries",
            note="Groceries and snacks",
        )
        self.assertEqual(updated.amount, 18.50)
        self.assertEqual(updated.category, "Groceries")
        self.assertEqual(updated.note, "Groceries and snacks")

        # Verify persistence
        reloaded = self.tracker.get_expense(exp.id)
        self.assertEqual(reloaded.amount, 18.50)
        self.assertEqual(reloaded.category, "Groceries")

    def test_edit_nonexistent_id_raises_validation_error(self):
        with self.assertRaises(ValidationError) as ctx:
            self.tracker.edit_expense(expense_id=404, amount=50.0)
        self.assertIn("Expense with ID 404 was not found", str(ctx.exception))

    def test_delete_expense_removes_from_store(self):
        exp1, _ = self.tracker.add_expense(10.0, "Food")
        exp2, _ = self.tracker.add_expense(20.0, "Tech")

        self.assertEqual(len(self.tracker.list_expenses()), 2)
        deleted = self.tracker.delete_expense(exp1.id)
        self.assertEqual(deleted.id, exp1.id)

        remaining = self.tracker.list_expenses()
        self.assertEqual(len(remaining), 1)
        self.assertEqual(remaining[0].id, exp2.id)

    def test_delete_nonexistent_id_raises_validation_error(self):
        with self.assertRaises(ValidationError) as ctx:
            self.tracker.delete_expense(999)
        self.assertIn("Expense with ID 999 was not found", str(ctx.exception))

    def test_budget_limit_exceeded_warning(self):
        self.tracker.set_budget("2026-04", 100.0)
        _, warning1 = self.tracker.add_expense(60.0, "Utilities", "2026-04-05")
        self.assertIsNone(warning1)

        _, warning2 = self.tracker.add_expense(50.0, "Internet", "2026-04-10")
        self.assertIsNotNone(warning2)
        self.assertIn("WARNING: Monthly budget for 2026-04 exceeded", warning2)

    def test_export_to_csv(self):
        self.tracker.add_expense(12.50, "Food", "2026-03-01", "Coffee & Bagel")
        self.tracker.add_expense(45.00, "Transport", "2026-03-02", "Monthly pass")

        csv_path = Path(self.temp_dir.name) / "exported.csv"
        count, path_out = self.tracker.export_csv(str(csv_path))
        self.assertEqual(count, 2)
        self.assertTrue(csv_path.exists())

        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]["Category"], "Food")
            self.assertEqual(rows[0]["Amount"], "12.50")

    def test_monthly_report_generation(self):
        self.tracker.set_budget("2026-05", 200.0)
        self.tracker.add_expense(80.0, "Rent", "2026-05-01", "Storage unit")
        report = self.tracker.generate_monthly_report("2026-05")

        self.assertIn("EXPENSE REPORT - 2026-05", report)
        self.assertIn("Total Spent:        $80.00", report)
        self.assertIn("Budget Limit:       $200.00", report)
        self.assertIn("Rent", report)


if __name__ == "__main__":
    unittest.main()
