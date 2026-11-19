# 💰 AI-Ready Expense Tracker CLI

A lightweight, robust, command-line personal finance and expense tracking tool built in Python 3.12 following modern AI-assisted engineering practices, automated git hooks, and strict code-quality rules.

---

## 🌟 Features

### 📋 Must-Have Features
- **Add Expense:** Record expenses with amount, category, date (defaults to today), and optional note.
- **List & Filter:** Query expenses with flexible filters by category and ISO date range (`YYYY-MM-DD`).
- **Spend Summary:** Aggregations of total spend, breakdown by category, and breakdown by month.
- **Edit & Delete:** Update or remove existing expenses by sequential ID.
- **Persistent Storage:** Local JSON storage with atomic writes (temporary file swapping) to prevent corruption.
- **Input Validation:** Friendly error messages with non-zero exit codes (handles negative amounts, zero amounts, invalid calendar days like Feb 30, malformed dates, unknown IDs) — **zero crashes or raw tracebacks**.
- **Unit Tests:** 21 unit and edge-case tests with 100% pass rate.

### 🚀 Stretch Goals Implemented
- **CSV Export:** Export filtered or unfiltered transactions into standard CSV format for Excel/Google Sheets.
- **Monthly Budget Limits:** Set a monthly budget with automated alert warnings if an expense causes spending to exceed the limit.
- **Monthly Text Report:** Clean ASCII formatted monthly financial report with budget status and category breakdown percentages.

---

## 🛠️ Architecture & Requirements

- **Runtime:** Python 3.12+
- **Dependencies:** **Zero external dependencies.** Uses only standard library modules: `argparse`, `json`, `csv`, `datetime`, `unittest`, `dataclasses`, `pathlib`, `tempfile`.

### Directory Structure
```text
.
├── .githooks/
│   └── pre-commit              # Pre-commit hook executing syntax checks & test suite
├── .skills/
│   ├── add-feature.md          # Skill 1: Structured feature lifecycle procedure
│   └── test-generator.md       # Skill 2: Automated edge-case unit test generator
├── expense_tracker/
│   ├── __init__.py             # Package marker
│   ├── cli.py                  # CLI parsing and command dispatch
│   ├── models.py               # Expense & Budget dataclasses
│   ├── storage.py              # Persistent atomic JSON storage & CSV export
│   ├── tracker.py              # Business logic, aggregations, and budget checking
│   └── validators.py           # Strict input validation functions
├── tests/
│   ├── __init__.py
│   └── test_tracker.py         # 21 unit tests covering all flows & edge cases
├── AGENTS.md                   # AI Assistant rules, code styles, and "Never" guidelines
├── CLAUDE.md                   # Compatible mirror of AGENTS.md
├── AI_USAGE_LOG.md             # 5 detailed prompt-output-correction entries
├── REFLECTION.md               # 1/2-page retrospective, permissions note & integration details
├── DEMO_GUIDE.md               # 3-5 minute demonstration script for live recording
└── README.md                   # This documentation
```

---

## 🚀 Setup & Installation

### 1. Clone & Configure Git Hooks
Clone the repository and point Git to the included hooks:
```bash
git clone <repo-url>
cd TASK-11

# Enable automated pre-commit hooks
git config core.hooksPath .githooks
```

### 2. Verify Hook Execution
Run the unit test suite directly:
```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

---

## 📖 CLI Usage & Examples

All commands are executed via `python -m expense_tracker.cli <command>`.

### 1. Add Expenses
```bash
# Add with custom date and note
python -m expense_tracker.cli add --amount 45.50 --category Food --date 2026-03-15 --note "Team lunch"

# Add with today's date automatically
python -m expense_tracker.cli add --amount 18.00 --category Transport --note "Metro pass"

# Add expense that triggers budget warning
python -m expense_tracker.cli add --amount 250.00 --category Gadgets --date 2026-03-20 --note "Mechanical keyboard"
```

### 2. List Expenses (with Optional Filters)
```bash
# List all expenses in a formatted table
python -m expense_tracker.cli list

# Filter by category
python -m expense_tracker.cli list --category Food

# Filter by date range
python -m expense_tracker.cli list --start-date 2026-03-01 --end-date 2026-03-31
```
*Output sample:*
```text
+----+------------+-----------+---------+------------+
| ID | Date       | Category  | Amount  | Note       |
+----+------------+-----------+---------+------------+
| 1  | 2026-03-15 | Food      | $45.50  | Team lunch |
| 2  | 2026-03-19 | Transport | $18.00  | Metro pass |
+----+------------+-----------+---------+------------+
Total matching items: 2 | Total: $63.50
```

### 3. Spend Summary
```bash
# Full overview
python -m expense_tracker.cli summary

# Summary filtered by month
python -m expense_tracker.cli summary --month 2026-03

# Summary filtered by category
python -m expense_tracker.cli summary --category Food
```

### 4. Edit an Existing Expense
```bash
# Update amount and note of expense #1
python -m expense_tracker.cli edit --id 1 --amount 52.00 --note "Team lunch with drinks"
```

### 5. Delete an Expense
```bash
python -m expense_tracker.cli delete --id 2
```

### 6. Set & Check Monthly Budget (Stretch Goal)
```bash
# Set monthly budget limit for March 2026
python -m expense_tracker.cli budget --month 2026-03 --set 300.00

# View current budget status and remaining balance
python -m expense_tracker.cli budget --month 2026-03
```

### 7. Monthly Text Report (Stretch Goal)
```bash
python -m expense_tracker.cli report --month 2026-03
```
*Output sample:*
```text
==================================================
          EXPENSE REPORT - 2026-03
==================================================
Total Transactions: 2
Total Spent:        $302.00
Budget Limit:       $300.00
Budget Status:      ⚠️ EXCEEDED by $2.00
--------------------------------------------------
SPENDING BY CATEGORY:
  • Gadgets        : $  250.00  ( 82.8%)
  • Food           : $   52.00  ( 17.2%)
--------------------------------------------------
RECENT TRANSACTIONS:
  [  1] 2026-03-15 | Food         | $  52.00 - Team lunch with drinks
  [  3] 2026-03-20 | Gadgets      | $ 250.00 - Mechanical keyboard
==================================================
```

### 8. Export to CSV (Stretch Goal)
```bash
python -m expense_tracker.cli export --file march_expenses.csv --month 2026-03
```

---

## 🛡️ Input Validation & Error Handling

The application validates every user input rigorously and emits clean error messages without tracebacks:

| Test Scenario | Command | Result / Error Output |
| :--- | :--- | :--- |
| **Negative Amount** | `python -m expense_tracker.cli add -a -50 -c Food` | `❌ Error: Invalid amount -50.00: Expense amount must be strictly greater than 0.` |
| **Invalid Date** | `python -m expense_tracker.cli add -a 20 -c Food -d 2026-02-30` | `❌ Error: Invalid date '2026-02-30': Must be a real calendar date in YYYY-MM-DD format.` |
| **Unknown ID** | `python -m expense_tracker.cli delete -i 999` | `❌ Error: Expense with ID 999 was not found.` |
| **Empty Category** | `python -m expense_tracker.cli add -a 20 -c ""` | `❌ Error: Category cannot be empty. Please specify a category name.` |

---

## 🧪 Automated Testing & Hooks

To run the complete test suite manually:
```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

Before every Git commit, `.githooks/pre-commit` automatically runs:
1. Syntax validation (`python -m py_compile`) across all source and test files.
2. The complete unit test suite (`python -m unittest discover`).

If any test fails or syntax error is detected, the commit is aborted.
