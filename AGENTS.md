# AI Assistant Rules & Instructions (AGENTS.md)

## 1. Project Overview & Tech Stack
- **Project:** Expense Tracker CLI (Aurex Intern Challenge)
- **Language:** Python 3.12+ (Standard library only: `argparse`, `json`, `csv`, `datetime`, `unittest`, `dataclasses`, `pathlib`)
- **Dependencies:** 0 third-party packages. Everything must run on vanilla Python 3.12.

## 2. Directory Structure
```text
.
├── .githooks/            # Git hooks (pre-commit automated test & lint runner)
├── .skills/              # Reusable agent workflows (add-feature, test-generator)
├── expense_tracker/      # Application core package
│   ├── __init__.py
│   ├── cli.py            # CLI entry point, argument parsing, command handlers
│   ├── models.py         # Expense data classes, budget models, serialization
│   ├── storage.py        # Persistent JSON I/O, atomic writes, CSV export
│   ├── tracker.py        # Business logic: filtering, aggregations, budget alerts
│   └── validators.py     # Strict input validation and user-friendly error messages
├── tests/                # Automated test suite
│   ├── __init__.py
│   └── test_tracker.py   # Unit and edge-case tests
├── AGENTS.md             # This rules file
├── AI_USAGE_LOG.md       # AI collaboration audit log (prompts, outputs, corrections)
├── REFLECTION.md         # Half-page retrospective, permissions note, custom commands
└── README.md             # Setup, documentation, and usage examples
```

## 3. Essential Commands
- **Run the CLI:**
  `python -m expense_tracker.cli --help`
- **Run Unit Tests:**
  `python -m unittest discover -s tests -p "test_*.py"`
- **Run Syntax / Compilation Check:**
  `python -m py_compile expense_tracker/*.py tests/*.py`

## 4. Code Style & Standards
- Follow PEP 8 guidelines: 4 spaces per indentation level, lowercase function/variable names with underscores.
- Type annotations (`typing`) on all public function signatures.
- Clean error handling: Return structured error messages to the CLI user with non-zero exit codes. Never crash with raw unhandled Python tracebacks on bad user inputs.
- Keep business logic isolated from CLI parsing and file I/O for high testability.

## 5. Strict "Never" Rules
1. **NEVER commit secrets, tokens, or credentials.**
2. **NEVER add third-party dependencies** (`pip install`, `requirements.txt`) without explicit user authorization.
3. **NEVER swallow or suppress errors silently** (`except: pass` is prohibited; log or present a descriptive error).
4. **NEVER overwrite or corrupt persistent user data** without validation or atomic write patterns (write to temp file then replace).

## 6. Definition of Done
A feature or task is considered complete ONLY when:
1. All positive and negative validation rules are enforced.
2. Unit tests covering both standard execution and edge cases are written and passing.
3. Automated pre-commit hook runs clean without syntax or test failures.
4. CLI commands are documented with examples in `README.md`.
