# Skill: Unit Test Generator

## 1. Goal
Generate thorough, meaningful unit tests for any function, CLI command, or module within the Expense Tracker, ensuring coverage for normal flows, boundary conditions, edge cases, and invalid inputs without requiring third-party testing libraries.

## 2. Procedure Steps

### Step 1: Analyze the Target Component
- Inspect the function signature, argument types, return types, and exceptions raised.
- Identify preconditions, postconditions, and side effects (such as file I/O).

### Step 2: Enumerate Test Scenarios
For every target component, identify at least four classes of test cases:
1. **Happy Path:** Valid input returning expected result or modifying state as expected.
2. **Boundary Cases:** Zero amounts, single-character strings, boundary dates (e.g., leap years, month ends).
3. **Negative / Input Validation Cases:** Negative amounts, invalid date strings (e.g. `2024-02-30`, `invalid-date`), nonexistent IDs, empty strings.
4. **State / Persistence Cases:** Empty storage files, missing JSON files, corrupted JSON payloads.

### Step 3: Implement Isolated Test Methods using `unittest`
- Use Python's built-in `unittest.TestCase`.
- Use `tempfile.TemporaryDirectory` for file-system isolation so tests never mutate real user data.
- Use `assertRaises` or inspect returned error objects/exit codes.
- Adhere to clean naming: `test_<function>_<scenario>_<expected_behavior>`.

### Step 4: Run and Verify
- Run the test suite: `python -m unittest discover -s tests`.
- Confirm that the new tests pass and fail when assertions are deliberately broken.

---

## 3. Output Format
When generating tests, produce a Python test module or test class adhering to this structure:

```python
import unittest
import tempfile
from pathlib import Path
from expense_tracker.tracker import ExpenseTracker
from expense_tracker.validators import ValidationError

class Test<FeatureName>(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.storage_file = Path(self.temp_dir.name) / "test_expenses.json"
        self.tracker = ExpenseTracker(str(self.storage_file))

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_<method>_success(self):
        # arrange, act, assert
        pass

    def test_<method>_negative_or_edge_case(self):
        # arrange, act, assert
        pass
```

---

## 4. Concrete Example

**User Prompt:** "Generate tests for expense ID validation and deletion."

**Expected Output:**
```python
import unittest
import tempfile
from pathlib import Path
from expense_tracker.tracker import ExpenseTracker
from expense_tracker.validators import ValidationError

class TestExpenseDelete(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.storage_file = Path(self.temp_dir.name) / "test_data.json"
        self.tracker = ExpenseTracker(str(self.storage_file))
        self.expense = self.tracker.add_expense(amount=45.50, category="Food", date_str="2024-03-15", note="Lunch")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_delete_existing_expense_removes_from_store(self):
        deleted = self.tracker.delete_expense(self.expense.id)
        self.assertTrue(deleted)
        self.assertEqual(len(self.tracker.list_expenses()), 0)

    def test_delete_nonexistent_id_raises_validation_error(self):
        with self.assertRaises(ValidationError) as ctx:
            self.tracker.delete_expense("non-existent-uuid-999")
        self.assertIn("Expense with ID 'non-existent-uuid-999' not found", str(ctx.exception))
```
