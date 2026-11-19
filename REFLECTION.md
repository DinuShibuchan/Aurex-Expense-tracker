# 💭 Reflection on AI-Assisted Development

## 1. What Worked
- **Rapid Prototyping with Immediate Guardrails:** Having predefined domain models and validation rules allowed the AI assistant to scaffold CLI handlers and business logic rapidly while maintaining clean separations between parsing, persistence, and computation.
- **Skill-Driven Discipline:** The `add-feature` skill forced a deliberate plan-before-code loop. Rather than writing ad-hoc changes across three files at once, each feature followed a clear sequence: restate goal -> propose plan -> review -> implement -> test -> summarize. This prevented scope creep and kept git diffs readable.
- **Zero-Dependency Portability:** Limiting the stack to the Python 3.12 standard library proved to be a major asset. Setup took zero seconds, avoiding virtual environment conflicts, platform-specific binaries, or package vulnerability audits.
- **Automated Pre-Commit Hook:** Wiring the pre-commit hook early in the process created an infallible safety net. Any unintentional syntax discrepancy or broken assertion immediately halted the commit, preventing bad commits from entering the history.

## 2. What Did Not Work
- **Naive Assumptions Around Data Integrity:** Out of the box, the AI tended to suggest basic implementations that worked under happy-path conditions but neglected resilience. For example, it initially used regex patterns for dates that permitted calendar impossibilities (such as `2026-02-31`), directly overwrote JSON files without atomic swaps, and omitted budget alert triggers during expense edits.
- **Dependency Drift:** Without strict negative constraints in `AGENTS.md`, the AI habitually suggested adding external packages (`pydantic`, `pytest`, `click`, `tabulate`). Human oversight was necessary to reject these and keep the solution lean.

## 3. Which Rule or Skill Changed the Results Most
- **The "Never Add a Dependency Without Asking" Rule (`AGENTS.md`):** This single constraint completely steered the technical direction toward native standard library constructs (`dataclasses`, `argparse`, `tempfile`, `unittest`), resulting in a lightweight, self-contained codebase that executes everywhere out-of-the-box.
- **The `add-feature` Skill:** This skill eliminated hallucinated requirements by enforcing a structured planning phase where CLI flags, error messages, and edge cases were agreed upon before modifying code.

## 4. What I Would Do Differently
- If undertaking this project again, I would write the edge-case unit test scenarios *first* (Test-Driven Development) using the `test-generator` skill before having the AI write the implementation logic. This would establish an automated acceptance harness even before the first line of CLI code is authored.
- I would also expand the persistence layer to support multiple user profiles or workspaces out-of-the-box via CLI environment variables.

---

## 5. Permissions Note
- **Approval Mode Used:** **Ask First (Interactive Approval)**
- **Rationale:**
  The `Ask First` mode was selected to maintain complete human-in-the-loop control over the repository. In an AI-assisted workflow, autonomous auto-editing can introduce unwanted dependencies, silent file overwrite bugs, or architectural sprawl. By requiring confirmation before executing significant multi-file updates or running terminal scripts, every modification was critically reviewed against the evaluation rubric and the strict "Never" rules in `AGENTS.md`.

---

## 6. Optional Custom Command / Automation
- **Custom Tool / Script:** Automated Pre-Commit Hook & Lint Runner (`.githooks/pre-commit`)
- **Usage & Description:**
  To guarantee code quality across all commits, a custom hook was configured using Git's native `core.hooksPath`. It automatically runs byte-code compilation verification (`python -m py_compile`) and executes the 21-test unit suite (`python -m unittest discover`) prior to recording any commit. If an error is introduced, the commit fails with actionable diagnostic feedback, ensuring zero broken states in repository history.
