# 🎬 Demo Script & Walkthrough Guide (3–5 Minutes)

Use this guide to record your screen recording or present your live demo of the Expense Tracker CLI and AI workflow.

---

## ⏱️ Video / Demo Timeline Overview

| Minute | Segment | Focus Area |
| :---: | :--- | :--- |
| **0:00 - 0:45** | **1. AI Setup & Repository Rules** | Show `AGENTS.md`, `.skills/`, and pre-commit hook in `.githooks/`. |
| **0:45 - 1:30** | **2. Pre-Commit Hook in Action** | Run test suite and demonstrate commit hook verification. |
| **1:30 - 3:00** | **3. Core Features & Edge Cases** | Add, list, edit, delete, and test negative validation (bad dates, negative amounts). |
| **3:00 - 4:15** | **4. Stretch Goals & Reports** | Monthly budget warnings, monthly report, and CSV export. |
| **4:15 - 5:00** | **5. AI Workflow Reflection** | Highlight `AI_USAGE_LOG.md` and `add-feature.md` skill execution. |

---

## 📋 Exact Terminal Commands to Run

### Step 1: Show Rules & Automated Testing (0:45)
1. Display the AI rules:
   ```bash
   head -n 25 AGENTS.md
   ```
2. Run the automated test suite (all 21 tests pass):
   ```bash
   python -m unittest discover -s tests -p "test_*.py" -v
   ```

### Step 2: Input Validation & Edge Cases (1:30)
Show how the application gracefully catches invalid user inputs without throwing raw Python tracebacks:
1. Try adding a negative amount (gracefully rejected):
   ```bash
   python -m expense_tracker.cli add --amount -30.00 --category Food
   ```
   *Expected:* `❌ Error: Invalid amount -30.00: Expense amount must be strictly greater than 0.`
2. Try adding an impossible calendar date (February 30):
   ```bash
   python -m expense_tracker.cli add --amount 15.00 --category Food --date 2026-02-30
   ```
   *Expected:* `❌ Error: Invalid date '2026-02-30': Must be a real calendar date in YYYY-MM-DD format.`

### Step 3: Core Workflow (2:30)
1. Set a monthly budget for March 2026:
   ```bash
   python -m expense_tracker.cli budget --month 2026-03 --set 150.00
   ```
2. Add valid expenses:
   ```bash
   python -m expense_tracker.cli add --amount 45.00 --category Food --date 2026-03-10 --note "Grocery shopping"
   python -m expense_tracker.cli add --amount 35.00 --category Transport --date 2026-03-12 --note "Bus pass"
   ```
3. Add an expense that exceeds the budget to show the automated alert:
   ```bash
   python -m expense_tracker.cli add --amount 80.00 --category Tech --date 2026-03-15 --note "Noise-canceling earphones"
   ```
   *Notice the warning:* `⚠️ WARNING: Monthly budget for 2026-03 exceeded! Spent: $160.00 | Limit: $150.00 | Over by: $10.00`

### Step 4: Listing, Filtering & Editing (3:30)
1. List all expenses in the ASCII table:
   ```bash
   python -m expense_tracker.cli list
   ```
2. Filter expenses by category:
   ```bash
   python -m expense_tracker.cli list --category Food
   ```
3. Edit an existing expense:
   ```bash
   python -m expense_tracker.cli edit --id 1 --amount 40.00 --note "Discounted groceries"
   ```

### Step 5: Stretch Goals & Reports (4:15)
1. Generate the formatted text report:
   ```bash
   python -m expense_tracker.cli report --month 2026-03
   ```
2. Export to CSV:
   ```bash
   python -m expense_tracker.cli export --file march_summary.csv
   ```
3. Show the CSV content:
   ```bash
   python -c "print(open('march_summary.csv').read())"
   ```

### Step 6: Wrap-up & AI Deliverables (5:00)
- Briefly show `.skills/add-feature.md` explaining how the feature lifecycle was structured.
- Show `AI_USAGE_LOG.md` highlighting how the assistant's initial proposals (e.g. adding third-party deps, regex date validation) were audited and corrected.
