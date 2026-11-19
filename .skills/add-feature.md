# Skill: Add-Feature Workflow

## 1. Goal
Provide a disciplined, repeatable, and safe procedure for introducing new features or enhancements to the Expense Tracker codebase while maintaining high code quality, comprehensive test coverage, and clear user alignment.

## 2. Procedure Steps

### Step 1: Restate the Goal
- Clarify the user's requirement in plain English.
- Identify the impacted CLI arguments, data models, storage changes, and potential edge cases (e.g., negative inputs, bad date formats, empty datasets).

### Step 2: Propose the Plan
- Break down the proposed solution into small, incremental modifications:
  - Data model adjustments (`expense_tracker/models.py`)
  - Input validation updates (`expense_tracker/validators.py`)
  - Business logic / storage logic (`expense_tracker/tracker.py` or `storage.py`)
  - CLI parser & command handling (`expense_tracker/cli.py`)
  - Unit tests to write (`tests/test_tracker.py`)
- Outline the command syntax and expected output.

### Step 3: Wait for Approval
- Present the plan to the user or team lead.
- Do NOT proceed to write production code until the user approves or confirms the architectural approach.

### Step 4: Implement in Small Steps
- Adhere strictly to `AGENTS.md` rules (PEP 8, type hints, zero external dependencies).
- Keep changes modular and atomic.
- Provide descriptive user feedback for errors (exit with code 1, never raw traceback).

### Step 5: Write & Run Unit Tests
- Add at least 2 tests per feature:
  1. *Happy path test* verifying correct functionality and output.
  2. *Edge case / negative test* verifying appropriate rejection and error messaging.
- Run `python -m unittest discover -s tests`. Ensure 100% of tests pass.

### Step 6: Summarise the Change
- Produce a concise summary of files changed, features added, test results, and command examples for the user.

---

## 3. Output Format
When executing this skill, output should follow this format:

```markdown
### 🎯 Feature Goal
[Concise description of the feature and problem it solves]

### 📋 Proposed Plan
1. **Model / Storage:** [Changes needed]
2. **Validation:** [Validation rules added]
3. **CLI:** [New arguments/commands]
4. **Testing:** [Specific test scenarios to cover]

*Awaiting approval before implementation.*
```

---

## 4. Concrete Example

**User Prompt:** "Add an export command that dumps filtered expenses to a CSV file."

**Agent Response:**
> ### 🎯 Feature Goal
> Enable users to export filtered or all recorded expenses into a standard CSV format for external analysis in spreadsheet software.
>
> ### 📋 Proposed Plan
> 1. **Storage (`expense_tracker/storage.py`):** Add `export_to_csv(expenses, filepath)` using Python's built-in `csv` module.
> 2. **Validation (`expense_tracker/validators.py`):** Validate that the target filepath is writable and has a `.csv` extension.
> 3. **CLI (`expense_tracker/cli.py`):** Add `export` sub-command with optional `--category`, `--start-date`, `--end-date`, and `--out` (defaulting to `expenses_export.csv`).
> 4. **Testing (`tests/test_tracker.py`):** Test exporting 3 items to a temp file, verify CSV headers `[id, date, amount, category, note]`, and test handling invalid output directory paths.
>
> *Shall I proceed with this implementation plan?*
