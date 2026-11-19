"""Automated demo walkthrough script for screen recording.

Run this script while recording your screen (Win + Shift + R or OBS).
It automatically executes the full demo sequentially with clean pauses,
demonstrating all core features, edge-case validations, and stretch goals.
"""

import os
import subprocess
import sys
import time

CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"


def print_step(title: str, description: str):
    print("\n" + "=" * 65)
    print(f"{BOLD}{CYAN}▶ {title}{RESET}")
    print(f"{YELLOW}  {description}{RESET}")
    print("=" * 65)
    time.sleep(1.5)


def run(cmd: str, delay: float = 2.0):
    print(f"\n{BOLD}{GREEN}$ {cmd}{RESET}")
    time.sleep(0.8)
    res = subprocess.run(cmd, shell=True)
    time.sleep(delay)
    return res.returncode


def main():
    print(f"{BOLD}{GREEN}")
    print("=" * 65)
    print("  🚀 EXPENSE TRACKER CLI - AUTOMATED DEMO RECORDING RUNNER")
    print("=" * 65)
    print(f"{RESET}")
    print("Recording starts in 3 seconds... (Get your screen recorder ready!)")
    time.sleep(3)

    # Clean previous demo run if any
    if os.path.exists("expenses.json"):
        os.remove("expenses.json")

    # Step 1: Pre-commit hook & automated testing
    print_step(
        "STEP 1: Automated Test Suite & Hook Verification",
        "Executing all 21 unit tests covering core operations and edge cases.",
    )
    run("python -m unittest discover -s tests -p \"test_*.py\" -v")

    # Step 2: Negative Validation (Handling invalid input gracefully)
    print_step(
        "STEP 2: Input Validation & Edge-Case Handling (No Crashes)",
        "Demonstrating clean rejection of negative amounts, zero amounts, and bad dates.",
    )
    run("python -m expense_tracker.cli add --amount -25.00 --category Food")
    run("python -m expense_tracker.cli add --amount 15.00 --category Food --date 2026-02-30")

    # Step 3: Setting Monthly Budget (Stretch Goal)
    print_step(
        "STEP 3: Setting Monthly Budget (Stretch Goal)",
        "Configuring a monthly budget limit of $150.00 for March 2026.",
    )
    run("python -m expense_tracker.cli budget --month 2026-03 --set 150.00")

    # Step 4: Adding Expenses
    print_step(
        "STEP 4: Adding Expenses with Categories & Notes",
        "Adding groceries, transport, and an expense that triggers budget warning.",
    )
    run("python -m expense_tracker.cli add --amount 45.00 --category Food --date 2026-03-10 --note \"Weekly groceries\"")
    run("python -m expense_tracker.cli add --amount 35.00 --category Transport --date 2026-03-12 --note \"Monthly train pass\"")
    run("python -m expense_tracker.cli add --amount 80.00 --category Tech --date 2026-03-15 --note \"Wireless keyboard\"")

    # Step 5: Listing & Filtering
    print_step(
        "STEP 5: Formatted ASCII Listing & Category Filters",
        "Displaying all records in table format, then filtering exclusively for 'Food'.",
    )
    run("python -m expense_tracker.cli list")
    run("python -m expense_tracker.cli list --category Food")

    # Step 6: Editing and Deleting
    print_step(
        "STEP 6: Editing and Deleting by ID",
        "Modifying expense #1 amount and note, then deleting an unknown ID (validation error).",
    )
    run("python -m expense_tracker.cli edit --id 1 --amount 40.00 --note \"Groceries on discount\"")
    run("python -m expense_tracker.cli delete --id 999")

    # Step 7: Summary & Monthly Text Report (Stretch Goal)
    print_step(
        "STEP 7: Spend Summary & Comprehensive Monthly Report",
        "Displaying spend breakdown by category and full monthly ASCII report.",
    )
    run("python -m expense_tracker.cli summary")
    run("python -m expense_tracker.cli report --month 2026-03")

    # Step 8: CSV Export (Stretch Goal)
    print_step(
        "STEP 8: CSV Export (Stretch Goal)",
        "Exporting all expenses to 'march_summary.csv'.",
    )
    run("python -m expense_tracker.cli export --file march_summary.csv")

    # Step 9: Skills & AI Rules Overview
    print_step(
        "STEP 9: AI Rules & Skills Integration",
        "Showing AGENTS.md rules and .skills/ directory.",
    )
    run("python -c \"print(open('AGENTS.md').read()[:320])\"")
    run("dir .skills")

    print("\n" + "=" * 65)
    print(f"{BOLD}{GREEN}🎉 DEMO COMPLETE! You can now stop your screen recording.{RESET}")
    print("=" * 65)


if __name__ == "__main__":
    main()
