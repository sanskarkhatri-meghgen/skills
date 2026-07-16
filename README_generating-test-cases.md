# Test Case Generator

## Overview

Generates, executes, and verifies complete test suites for any function or feature. Given a target, it autonomously discovers your project's architecture, drafts a test plan for your approval, writes the suite, runs it, and self-corrects until coverage targets are met — all without touching your source code.

---

## When to Use This Skill

### In-Scope Requests
- "Write tests for `calculate_discount()`"
- "Generate a test suite for the auth module"
- "Hit 90% coverage on `parser.py`"
- "Add edge case tests for the payment flow"

### Out-of-Scope Requests
- Debugging existing tests
- Explaining what a function does
- Refactoring source code

If the request is ambiguous, the skill will ask: *"Do you want me to generate new test cases for this, or do you need help with something else?"*

---

## Execution Modes

### Unit Mode
Activated when a specific function or method is targeted. Isolates the unit under test and mocks all external dependencies.

### Integration / Feature Mode
Activated when a feature, workflow, or whole module is targeted. Traces cross-file references, matches infrastructure patterns, and verifies combined multi-component behaviour.

The skill selects the correct mode automatically based on your request.

---

## Workflow

### Step 1 — Architectural Discovery
Scans your workspace for dependency manifests (`package.json`, `pyproject.toml`, `Cargo.toml`, etc.) to detect language, framework, and existing test conventions.

### Step 2 — Test Plan & Approval Gate
Presents a structured test plan showing target components, representative inputs, and expected outputs before writing any code. **Execution pauses here — you must explicitly approve before anything is written to disk.**

### Step 3 — Test Generation
Generates the complete test suite aligned to your project's conventions and saves it to disk.

### Step 4 — Coverage Loop & Self-Correction
Runs the test suite and coverage tool natively. If coverage falls below the target, it analyses missed lines and appends new tests. Repeats up to **3 iterations**.

### Step 5 — Final Report
Writes a full execution report to a `.report.md` file alongside the test file, and prints a short summary in chat.

---

## Supported Languages & Frameworks

| Language | Framework |
|----------|-----------|
| Python | pytest |
| JavaScript / TypeScript | Jest / Vitest |
| Java | JUnit 5 |
| Go | `testing` (stdlib) |
| C++ | Google Test |
| Rust | `cargo test` |
| .NET / C# | xUnit |
| Ruby | RSpec |
| PHP | PHPUnit |

Other ecosystems are supported — the skill selects the de-facto standard for whatever it detects.

---

## What the Skill Enforces Automatically

Every generated test suite is guaranteed to comply with the following, with no extra configuration required:

- **AAA Pattern** — every test is structured into Arrange, Act, and Assert blocks with comments
- **Naming Convention** — every test name encodes the unit under test, the condition, and the expected outcome, in the idiomatic style of the detected language
- **MC/DC Coverage** — boolean logic is covered using Modified Condition/Decision Coverage, not brute-force permutations
- **Parameterized Testing** — repeated cases are collapsed into parameterized matrices, not copy-pasted blocks
- **I/O Mocking** — all external boundaries (network, disk, DB, APIs) are mocked using the framework's native mocking library; no real I/O is executed
- **State Teardown** — any global state or DB mutations are rolled back after every test
- **Async Handling** — asynchronous code is handled with the correct event loop and synchronisation primitives
- **Determinism** — system clocks and random number generators are frozen where used
- **Public Interface Only** — private methods are never tested directly; only their effects through public callers
- **Assertion Precision** — all assertions target exact values, specific error types, and precise state changes
- **Source Immutability** — your source code is never modified

---

## Configuration

### Coverage Target
Default target is **85%**. To set a custom target, state it in your prompt:

> "Generate tests for `utils.py` with 95% coverage."

### Custom Overrides (`.test-agent-config.md`)
Place a `.test-agent-config.md` file at your workspace root to define project-specific rules — legacy fixture maps, custom mathematical constraints, or framework preferences. The skill reads this silently before planning and applies your overrides automatically.

---

## Output Contract

### Test File
Saved alongside your source using the ecosystem's standard naming convention:

| Language | Output Filename |
|----------|----------------|
| Python | `test_<source_filename>.py` |
| Go | `<source_filename>_test.go` |
| Java | `<ClassName>Test.java` under `src/test/java/...` |
| JS / TS | `<name>.test.js` / `<name>.spec.ts` |

### Execution Report
A detailed `<test_file_basename>.report.md` is written alongside the test file. Contains the full test-by-test results table, coverage breakdown, and missed lines justification. This is the complete record — not printed in full to chat.

### Chat Summary
A short summary is printed in chat once execution completes:
- Pass / fail / skip counts
- Final coverage percentage and iterations used
- Path to the full report file
- Brief notes on any failing tests (only if applicable)

---

## Limitations

- **3-iteration cap** on the self-correction loop. If coverage target is not met after 3 runs, the skill stops and documents why in the report.
- **No source modification** — if the source code has structural issues preventing testability, the skill will flag this but will not refactor it.
- **Genuinely unreachable lines** (e.g., `if __name__ == '__main__':` blocks, hardware-specific guards) are documented as *Measurement Artifacts* and excluded from the coverage calculation rather than counted as misses.
- The approval gate at Step 2 is mandatory and cannot be skipped.

---

## Example Prompts

```
Write unit tests for the `is_prime` function in algorithms/primes.py
```

```
Generate a full test suite for the user authentication module, targeting 90% coverage
```

```
Add edge case and boundary tests for `calculate_shipping_cost()` in orders/pricing.py
```
