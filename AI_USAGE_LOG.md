# 📝 AI Usage Log

This log documents interactions with the AI assistant during the development of the Expense Tracker CLI, demonstrating critical evaluation, verification of outputs, and iterative refinements.

---

### Entry 1: Architecture & Third-Party Dependencies
- **Prompt:**
  > "Design the CLI architecture for the expense tracker. Provide recommendations for data modeling, CLI table printing, and argument parsing."
- **What the AI produced:**
  > The AI suggested using `pydantic` for data validation, `click` or `typer` for CLI commands, and `tabulate` for rendering ASCII tables in the terminal.
- **What was wrong or missing:**
  > The intern challenge rules explicitly state: *"never add a dependency without asking"* and *"Keep it focused, not long."* Introducing three external third-party dependencies would introduce unnecessary package management overhead, vulnerability surface, and environment setup friction.
- **What I changed:**
  > Rejected all third-party libraries. Directed the assistant to use Python 3.12 standard library exclusively: `argparse` for CLI commands, `dataclasses` for models, and a custom ~20 line pure Python table formatter function (`format_table`) in `expense_tracker/cli.py`.

---

### Entry 2: Date & Input Validation Robustness
- **Prompt:**
  > "Write input validation functions for amount, category, and date in `expense_tracker/validators.py`."
- **What the AI produced:**
  > The AI generated a regex pattern `r'^\d{4}-\d{2}-\d{2}$'` to validate date strings, and checked `if amount < 0:` for amounts.
- **What was wrong or missing:**
  > 1. Regex date checking verifies string shape but accepts invalid calendar dates such as `2026-02-31` or `2026-11-31`.
  > 2. Checking `amount < 0` allowed `amount = 0`, whereas an expense must be strictly positive (> 0.0).
  > 3. Errors threw raw `ValueError` exceptions with inconsistent messaging.
- **What I changed:**
  > 1. Replaced regex with `datetime.strptime(date_str, "%Y-%m-%d")`, ensuring calendar validation catches non-existent leap days and invalid calendar days.
  > 2. Updated amount validator to reject `<= 0`.
  > 3. Created a unified `ValidationError` domain exception class and surfaced clean user-facing error messages without stack traces.

---

### Entry 3: Atomic Persistence & Corrupt State Prevention
- **Prompt:**
  > "Implement the JSON storage module in `expense_tracker/storage.py` to save and load expenses."
- **What the AI produced:**
  > A basic `Storage` class that directly opened `expenses.json` with `open(self.filepath, "w")` and dumped the JSON payload.
- **What was wrong or missing:**
  > Direct overwrites truncate the target file before writing. If the script is abruptly killed or crashes during serialization, `expenses.json` is left blank or corrupted, violating Rule #4: *"NEVER overwrite or corrupt persistent user data without validation or atomic write patterns."*
- **What I changed:**
  > Rewrote `save_data` to write to a temporary file (`tempfile.NamedTemporaryFile`) within the same directory, flush and close it, and then perform an atomic replacement via `os.replace`. Also added graceful fallback for non-existent or blank files.

---

### Entry 4: Budget Warning Coverage Across Mutation Operations
- **Prompt:**
  > "Implement monthly budget limits with an alert warning when total spending exceeds the limit."
- **What the AI produced:**
  > The AI created a `budget` command and added budget checking logic solely inside the `add_expense` method.
- **What was wrong or missing:**
  > It missed the `edit_expense` flow. If an existing expense amount is updated from $10 to $500, or its date is modified into a month with a tight budget, the limit could be breached without alerting the user.
- **What I changed:**
  > Extracted the budget calculation into a private helper `_check_budget_warning(expenses, budgets, month)` and integrated it into both `add_expense` and `edit_expense`. If either operation causes total spending for the month to surpass the limit, a clear warning header `⚠️ WARNING: Monthly budget exceeded` is displayed to the user.

---

### Entry 5: Pre-Commit Hook Portability & Test Runner
- **Prompt:**
  > "Create a pre-commit hook that runs the linter and tests before committing."
- **What the AI produced:**
  > A bash script calling `flake8` and `pytest -v`.
- **What was wrong or missing:**
  > `flake8` and `pytest` are external dependencies not installed by default in standard Python environments. Furthermore, the script assumed standard Unix paths and failed if tests directory was not yet initialized or when executed inside Git for Windows bash.
- **What I changed:**
  > Rewrote `.githooks/pre-commit` to use Python's built-in `py_compile` module for static syntax verification and `python -m unittest discover` for running tests. Added directory checks and informative status banners so the hook works portably on both Windows Git Bash and Linux environments.
