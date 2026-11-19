"""Command-line interface for Expense Tracker."""

import argparse
import sys
from datetime import datetime
from typing import Optional, List

from expense_tracker.tracker import ExpenseTracker
from expense_tracker.validators import ValidationError


def build_parser() -> argparse.ArgumentParser:
    """Construct CLI argument parser with all subcommands."""
    parser = argparse.ArgumentParser(
        prog="expense-tracker",
        description="Command-line Expense Tracker with AI-ready workflows.",
    )
    parser.add_argument(
        "--data-file",
        dest="data_file",
        default="expenses.json",
        help="Path to JSON storage file (default: expenses.json)",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: add
    p_add = subparsers.add_parser("add", help="Add a new expense")
    p_add.add_argument("--amount", "-a", required=True, help="Expense amount (e.g. 45.50)")
    p_add.add_argument("--category", "-c", required=True, help="Expense category (e.g. Food, Transport)")
    p_add.add_argument("--date", "-d", help="Expense date YYYY-MM-DD (defaults to today)")
    p_add.add_argument("--note", "-n", default="", help="Optional note or description")

    # Command: list
    p_list = subparsers.add_parser("list", help="List recorded expenses with optional filters")
    p_list.add_argument("--category", "-c", help="Filter by category")
    p_list.add_argument("--start-date", help="Filter expenses on or after YYYY-MM-DD")
    p_list.add_argument("--end-date", help="Filter expenses on or before YYYY-MM-DD")

    # Command: summary
    p_sum = subparsers.add_parser("summary", help="Show total spend summary by category and month")
    p_sum.add_argument("--category", "-c", help="Filter summary by specific category")
    p_sum.add_argument("--month", "-m", help="Filter summary by month (YYYY-MM)")

    # Command: edit
    p_edit = subparsers.add_parser("edit", help="Edit an existing expense by ID")
    p_edit.add_argument("--id", "-i", required=True, help="ID of expense to edit")
    p_edit.add_argument("--amount", "-a", help="New amount")
    p_edit.add_argument("--category", "-c", help="New category")
    p_edit.add_argument("--date", "-d", help="New date (YYYY-MM-DD)")
    p_edit.add_argument("--note", "-n", help="New note")

    # Command: delete
    p_del = subparsers.add_parser("delete", help="Delete an expense by ID")
    p_del.add_argument("--id", "-i", required=True, help="ID of expense to delete")

    # Command: export (Stretch goal)
    p_exp = subparsers.add_parser("export", help="Export expenses to a CSV file")
    p_exp.add_argument("--file", "-f", default="expenses_export.csv", help="Target CSV file path")
    p_exp.add_argument("--category", "-c", help="Filter by category before exporting")
    p_exp.add_argument("--start-date", help="Filter start date (YYYY-MM-DD)")
    p_exp.add_argument("--end-date", help="Filter end date (YYYY-MM-DD)")

    # Command: budget (Stretch goal)
    p_bud = subparsers.add_parser("budget", help="Set or inspect monthly budget limit")
    p_bud.add_argument("--month", "-m", help="Target month (YYYY-MM, defaults to current month)")
    p_bud.add_argument("--set", dest="limit", help="Set budget amount for the month")

    # Command: report (Stretch goal)
    p_rep = subparsers.add_parser("report", help="Generate a comprehensive monthly text report")
    p_rep.add_argument("--month", "-m", help="Target month (YYYY-MM, defaults to current month)")

    return parser


def format_table(headers: List[str], rows: List[List[str]]) -> str:
    """Format tabular data into a clean ASCII table."""
    if not rows:
        return "No records found."

    col_widths = [len(h) for h in headers]
    for row in rows:
        for idx, val in enumerate(row):
            col_widths[idx] = max(col_widths[idx], len(str(val)))

    sep_line = "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"
    header_line = "| " + " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers)) + " |"

    body_lines = []
    for row in rows:
        line = "| " + " | ".join(str(val).ljust(col_widths[i]) for i, val in enumerate(row)) + " |"
        body_lines.append(line)

    return "\n".join([sep_line, header_line, sep_line] + body_lines + [sep_line])


def handle_add(tracker: ExpenseTracker, args: argparse.Namespace) -> int:
    expense, warning = tracker.add_expense(
        amount=args.amount,
        category=args.category,
        date_str=args.date,
        note=args.note,
    )
    print(f"✅ Added expense #{expense.id}: ${expense.amount:.2f} for '{expense.category}' on {expense.date}")
    if expense.note:
        print(f"   Note: {expense.note}")
    if warning:
        print(f"\n{warning}")
    return 0


def handle_list(tracker: ExpenseTracker, args: argparse.Namespace) -> int:
    expenses = tracker.list_expenses(
        category=args.category,
        start_date=args.start_date,
        end_date=args.end_date,
    )
    if not expenses:
        print("No expenses found matching the criteria.")
        return 0

    headers = ["ID", "Date", "Category", "Amount", "Note"]
    rows = [
        [str(e.id), e.date, e.category, f"${e.amount:.2f}", e.note]
        for e in expenses
    ]
    print(format_table(headers, rows))
    total = sum(e.amount for e in expenses)
    print(f"Total matching items: {len(expenses)} | Total: ${total:.2f}")
    return 0


def handle_summary(tracker: ExpenseTracker, args: argparse.Namespace) -> int:
    res = tracker.summary(category=args.category, month=args.month)
    print("=" * 45)
    print("          EXPENSE SPEND SUMMARY")
    print("=" * 45)
    print(f"Total Transactions: {res['count']}")
    print(f"Total Amount Spent: ${res['total_spend']:.2f}")

    if res["by_category"]:
        print("\nBreakdown by Category:")
        for cat, amt in res["by_category"].items():
            pct = (amt / res["total_spend"] * 100) if res["total_spend"] > 0 else 0.0
            print(f"  • {cat:<15}: ${amt:>8.2f} ({pct:>5.1f}%)")

    if res["by_month"]:
        print("\nBreakdown by Month:")
        for m, amt in res["by_month"].items():
            print(f"  • {m:<15}: ${amt:>8.2f}")
    print("=" * 45)
    return 0


def handle_edit(tracker: ExpenseTracker, args: argparse.Namespace) -> int:
    if args.amount is None and args.category is None and args.date is None and args.note is None:
        raise ValidationError("No fields specified to edit. Provide at least one of: --amount, --category, --date, --note.")

    updated, warning = tracker.edit_expense(
        expense_id=args.id,
        amount=args.amount,
        category=args.category,
        date_str=args.date,
        note=args.note,
    )
    print(f"✅ Updated expense #{updated.id}: ${updated.amount:.2f} | {updated.category} | {updated.date}")
    if updated.note:
        print(f"   Note: {updated.note}")
    if warning:
        print(f"\n{warning}")
    return 0


def handle_delete(tracker: ExpenseTracker, args: argparse.Namespace) -> int:
    deleted = tracker.delete_expense(args.id)
    print(f"🗑️ Deleted expense #{deleted.id}: ${deleted.amount:.2f} ({deleted.category})")
    return 0


def handle_export(tracker: ExpenseTracker, args: argparse.Namespace) -> int:
    count, filepath = tracker.export_csv(
        output_file=args.file,
        category=args.category,
        start_date=args.start_date,
        end_date=args.end_date,
    )
    print(f"📁 Successfully exported {count} expense(s) to '{filepath}'.")
    return 0


def handle_budget(tracker: ExpenseTracker, args: argparse.Namespace) -> int:
    month = args.month if args.month else datetime.now().strftime("%Y-%m")
    if args.limit is not None:
        new_limit = tracker.set_budget(month, args.limit)
        print(f"🎯 Budget limit for {month} successfully set to ${new_limit:.2f}.")

    status = tracker.get_budget_status(month)
    print(f"\nBudget Status for {status['month']}:")
    print(f"  • Total Spent:   ${status['spent']:.2f}")
    if status["limit"] is not None:
        print(f"  • Budget Limit:  ${status['limit']:.2f}")
        if status["exceeded"]:
            print(f"  • Warning:       ⚠️ Over budget by ${abs(status['remaining']):.2f}!")
        else:
            print(f"  • Remaining:     ✅ Under budget by ${status['remaining']:.2f}.")
    else:
        print("  • Budget Limit:  Not set for this month.")
    return 0


def handle_report(tracker: ExpenseTracker, args: argparse.Namespace) -> int:
    month = args.month if args.month else datetime.now().strftime("%Y-%m")
    report = tracker.generate_monthly_report(month)
    print(report)
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    """Main CLI entrypoint."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    tracker = ExpenseTracker(storage_path=args.data_file)

    handlers = {
        "add": handle_add,
        "list": handle_list,
        "summary": handle_summary,
        "edit": handle_edit,
        "delete": handle_delete,
        "export": handle_export,
        "budget": handle_budget,
        "report": handle_report,
    }

    handler = handlers.get(args.command)
    if not handler:
        parser.print_help()
        return 1

    try:
        return handler(tracker, args)
    except ValidationError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Unexpected Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
