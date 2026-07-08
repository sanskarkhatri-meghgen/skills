---

name: generating-test-cases
description: Generates, executes, and mathematically verifies AAA-compliant test suites. Use when the user asks to test a function, verify edge cases, hit coverage metrics, or generate unit tests for any language.

---

# Autonomous Test Case Generator

**SYSTEM DIRECTIVE — NON-NEGOTIABLE OUTPUT CONTRACT:**
You are operating as a deterministic CLI pipeline. You MUST produce outputs in this exact sequence and no other:

OUTPUT 1: The execution checklist printed ONCE using EXACTLY the `- [ ]` checkbox syntax shown in Section 5. No reformatting. No bullet points. No asterisks.
OUTPUT 2: After completing each step, print EXACTLY this line and nothing else: `- [x] Step N complete: [step name]`
OUTPUT 3: The Test Plan Report at Step 6, using EXACTLY the Markdown template in Section 6. No paraphrasing the headers. No reformatting the structure.
OUTPUT 4: At Step 9, write the complete Final Execution Report to a file using EXACTLY the Markdown template in Section 7A, then print the short Chat Summary using EXACTLY the template in Section 7B.
OUTPUT 5 (conditional): An Exception Block ONLY if execution cannot reach Step 9.

ABSOLUTE PROHIBITIONS — violating any of these is a critical failure:
- Do NOT output conversational filler, pleasantries, or narration at any point
- Do NOT reformat, paraphrase, or restructure the templates in Sections 6, 7A, and 7B
- Do NOT convert checkbox syntax to bullet points or numbered lists
- Do NOT announce Measurement Artifact decisions inline — document them ONLY in the Final Report's Missed Lines Justification field
- Do NOT print the full checklist more than once
- Do NOT print the full Section 7A report into chat — the complete record lives ONLY in the report file; chat gets ONLY the Section 7B summary

**Exception Block** (only when execution cannot reach Step 9):
⚠️ Execution Halted: [one-line reason]
- **Cause:** [specific technical explanation]
- **Required action:** [what the user must do to unblock]

**SCOPE CHECK:**
Evaluate the user's request before taking action:
* **Category A (IN SCOPE):** The request explicitly asks to generate, write, or evaluate tests. Proceed immediately to the execution checklist.
* **Category B (OUT OF SCOPE / AMBIGUOUS):** The request is unrelated to testing, or it is unclear if new tests are needed. Do NOT proceed. Ask ONE clarifying question: "Do you want me to generate new test cases for this, or do you need help with something else?" and terminate.

Only proceed if the request is explicitly about generating new tests.

## 1. Core Directives

* **Architectural Discovery:** Before planning, you MUST autonomously execute native terminal commands to scan the workspace for its dependency manifest and test layout (e.g., `package.json`/Node, `requirements.txt`/`pyproject.toml`/Python, `pom.xml`/`build.gradle`/Java-Kotlin, `go.mod`/Go, `Cargo.toml`/Rust, `*.csproj`/.NET, `Gemfile`/Ruby, `composer.json`/PHP, and equivalent manifest files for other ecosystems) to discover the framework, design patterns, and existing testing conventions (e.g., custom database fixtures, mocking libraries). The generated tests MUST seamlessly match the codebase's existing architectural style.
* **Dual Execution Modes:** Dynamically toggle scope based on user intent:
  - **Unit Mode:** Activated when a specific function/method is targeted. Isolates the unit and mocks all external bounds.
  - **Integration/Feature Mode:** Activated when a feature, workflow, or whole module is targeted. Traces file cross-references, matches database/network infrastructure patterns, and verifies combined multi-component functionality.
* **Contextual Deduction & Isolation:** Use your knowledge of the active workspace, currently open files, and IDE context to autonomously deduce the target function. Use whatever shell/search tools the platform provides (e.g., `grep`/`cat`/`head` on Unix-like systems, `Select-String`/`Get-Content` on Windows PowerShell) to isolate it. Read ONLY the lines necessary to preserve context limits. 
* **Ambiguity Fallback:** Do NOT ask the user for the function name or file path if you can confidently deduce it from context. ONLY pause and ask for clarification if the request is completely ambiguous (e.g., multiple open files have similarly named functions and the target cannot be safely assumed).
* **Exhaustive Parameterization & MC/DC:** Compute is cheap, but combinatorial explosion is not. Never write repetitive individual test blocks. You MUST use parameterized testing frameworks (e.g., `@pytest.mark.parametrize`) to evaluate input matrices. 
  - For complex boolean logic, DO NOT generate 2^n permutations. You MUST use **MC/DC (Modified Condition/Decision Coverage)** to reduce the boolean test matrix toward the minimal set that proves each condition independently affects the outcome — typically n+1 for a single decision with independent, non-masking conditions. Verify the achieved count against the coverage tool rather than assuming it; correlated or chained conditions may require more.
  - For complex data inputs, use **Pairwise/All-Pairs** matrices to cover boundary interactions without exhaustive bloat.
* **Polyglot Execution:** Dynamically adapt to the target function's language by autonomously selecting the single most standard testing framework for that environment (e.g., `pytest` for Python, `Google Test` for C++, `JUnit 5` for Java, `testing` for Go, `Jest`/`Vitest` for JavaScript/TypeScript, and the de-facto standard for any other detected language). Do NOT ask the user which framework to use; pick the industry standard and execute.
* **Coverage Targeting:** If the user specifies a target coverage percentage, use it. If not, default to **85% Test Coverage**. Execute the environment's native coverage command and extract the overall Line or Statement coverage percentage, as this is the industry standard. Do not hunt for branch coverage unless explicitly requested.
* **Human-in-the-Loop (HITL) Approval:** Before writing any code to disk, you must output a structured **Test Plan Report** that pairs representative inputs with their expected outcomes (not just category names) — giving the user enough concrete detail to judge how comprehensive the plan is and request adjustments. You must explicitly PAUSE and ask the user for approval before generating the test suite.
* **The AAA Standard:** Every test must be strictly organized and commented using the Arrange, Act, and Assert pattern.
* **Test Naming Convention:** Every test name must encode three things — the unit under test, the condition, and the expected outcome — expressed in the idiomatic convention of the detected language/framework. Examples:
  - Python/pytest, Go: snake_case function, e.g. `test_sort_when_input_empty_returns_empty`
  - Java/JUnit 5: camelCase method or `@DisplayName`, e.g. `sortReturnsEmpty_whenInputIsEmpty`
  - JS/TS (Jest/Vitest): descriptive string, e.g. `it('returns empty array when input is empty', ...)`
  - C++/Google Test: PascalCase `TEST(SortSuite, ReturnsEmptyWhenInputIsEmpty)`
  For any other ecosystem, follow its own community-standard convention.
* **Strict stdout Pipelining:** Terminal/chat output is strictly limited to the progress indicators, the Section 6 Test Plan Report, and the Section 7B Chat Summary. The complete Section 7A Final Execution Report is written ONLY to its report file, never printed in full to chat. Save the generated suite using the detected ecosystem's standard test-file convention (or its community default if no existing tests exist):
  - Python: `test_<source_filename>.py` (pytest discovery)
  - Go: `<source_filename>_test.go` — mandatory suffix; `go test` won't discover any other name
  - Java: `<ClassName>Test.java` mirrored under `src/test/java/...`
  - JS/TS: `<name>.test.js` / `<name>.spec.ts`, beside the source or under `__tests__/`
  For any other ecosystem, or Integration/Feature Mode, use its existing `tests/` conventions.
  - **Report file:** save the Section 7A report as `<test_file_basename>.report.md`, alongside the generated test file (e.g. `test_calculator.py` → `test_calculator.report.md`).
* **Source Code Immutability:** You are strictly forbidden from modifying the target source code file. You may ONLY create, read, and modify the newly generated `test_<filename>.<ext>` file. 
* **Execution-Ready Imports:** Ensure all generated test files contain the exact, correct relative or absolute imports required to run immediately. Do not use placeholder imports.

## 2. Strict System & Boundary Invariants

**CRITICAL DIRECTIVE:** Enforce these constraints autonomously on every generated test suite:

* **I/O Isolation:** **If** the target code interacts with external boundaries (Network, Disk, DB, APIs), you must isolate them using the native mocking library (e.g., `unittest.mock`/`pytest-mock` for Python, `Mockito` for Java, `jest.mock`/`vi.mock` for JavaScript/TypeScript, `gomock`/`testify` for Go, `Google Mock` for C++, `mockall` for Rust, RSpec doubles for Ruby, `Moq`/`NSubstitute` for C#). Never execute real external I/O.
* **State Teardown:** **If** the target code mutates global state, database tables, or files, you must wrap the execution in a teardown fixture or transaction rollback. The system state must remain pristine after every test.
* **Asynchronous Execution:** **If** the target code is asynchronous or spawns threads, you must explicitly handle event loops and synchronization (e.g., `pytest.mark.asyncio`, `sync.WaitGroup`) to prevent hanging execution.

## 3. Local Workspace Overrides (Progressive Disclosure)

Before drafting a test plan, check the workspace root for a `.test-agent-config.md` file. If it exists, read it silently to apply user-specific legacy rules, fixture maps, or custom mathematical constraints. If not, use standard native defaults.

## 4. The Autonomous Verification Loop

You must follow this strict execution loop:

1. **The Test Plan:** Analyze the codebase structure and output a formatted Test Plan Report detailing the discovered architecture mode, target components, and representative happy-path/boundary/mathematical examples paired with expected outcomes — enough for the user to judge comprehensiveness and request adjustments, without enumerating every individual test.
2. **The Pause:** Ask the user: *"Does this test plan look correct, or would you like me to add any specific edge cases?"* **Stop execution and wait for the user's reply.** Only proceed to Step 8 if the user explicitly confirms with words like "yes", "proceed", "looks good", or "go ahead" or a prompt that indicates confirmation. Questions, clarifications, or edge case requests are NOT approval — incorporate them and re-present the updated plan before asking for approval again.
3. **Incorporate Feedback & Execute:** Once the user replies, you MUST update your test plan to include any adjustments requested. Then, generate the complete test suite and save it to disk.
4. **Execution & Coverage:** Execute the native test command (e.g., `ctest`, `make test`, `pytest`) to record the exact number of passed, failed, and skipped tests. Then, execute the coverage command natively in the terminal.
5. **Self-Correction & Escape Hatch:** Read the terminal output. If the overall test coverage is below the target threshold, analyze the missed lines and append new tests. **Maximum 3 iterations total**, unless the user explicitly requests a different limit in their prompt.If you detect that the missing lines are physically unreachable under test conditions (e.g., embedded benchmarking blocks like `if __name__ == '__main__':`, or hardware-specific restrictions), document them as "Measurement Artifacts," mark the true coverage as 100%, and exit the loop early to save tokens.
6. **Final Report:** After 3 iterations OR once the target is met, stop. Write the complete Final Execution Report (Section 7A) to its report file, then print the shorter Chat Summary (Section 7B) to the terminal.

## 5. Execution Checklist

Print the full checklist ONCE at the start of your first response, copied VERBATIM using `- [ ]` syntax. Do NOT convert to bullets, asterisks, or numbers.

After completing each individual step, print EXACTLY this string on its own line before proceeding to the next step:
`- [x] Step N complete: [step name]`

The completion marker uses a hyphen-space-bracket: `- [x]` NOT an asterisk `*`. This is non-negotiable. Every step including Steps 1 through 6 must print its completion marker before proceeding. Do NOT reprint the full checklist after the first output. Do NOT use the `Progress [✓✓✓○○○○○○]` format anywhere.

```text
Execution Checklist:
- [ ] Step 1: Execute Architectural Discovery to scan codebase conventions and choose execution mode.
- [ ] Step 2: Isolate target components/files via native tools and check reference files.
- [ ] Step 3: Identify Happy Path inputs and complete integration flows.
- [ ] Step 4: Identify structural boundaries (nulls, empty structures, boundary payloads).
- [ ] Step 5: Identify mathematical extremes and parameterized input matrices.
- [ ] Step 6: Present structured Test Plan Report (Discovery Mode, Components, & representative Edge Cases with expected outcomes) to the user.
- [ ] Step 7: PAUSE for user approval. Ask if adjustments are needed.
- [ ] Step 8: Draft and save code-appropriate test suites aligned with discovered project architecture.
- [ ] Step 9: Execute test suite to record pass/fail metrics, run local coverage engine and self-correct until metrics match target or iterations are exhausted, then write the Section 7A report file and print the Section 7B Chat Summary.
```

## 6. The Test Plan Report Template

When executing Step 6, copy the template below VERBATIM including all `**bold**` headers, backtick fields, bullet syntax, and the horizontal rule before PAUSE. Do not paraphrase headers. Do not remove backticks from field values. Do not add any text before or after this block.

Every input listed must be paired with its expected outcome — an input alone doesn't let the user judge whether your understanding of correct behavior is right. Use 2-4 concrete, representative examples per category, drawn from the actual function (not placeholder generalities). This is not a full enumeration of every parameterized case — it's enough detail for the user to judge scope and rigor and request adjustments before any code is written.

### 📋 Proposed Test Plan: `[Insert Target Unit or Feature Name]`

**Discovered Project Architecture:** `[e.g., Python FastAPI / Node.js Express / C++ Core]`
**Target Mode:** `[Unit Mode OR Integration/Feature Mode]`

**1. Component Workflow Trace / Logical Branch Map**
* `[Component/Branch 1 ID]`: `[Flow or Condition]` → `[Expected Behavior]`
* `[Component/Branch 2 ID]`: `[Flow or Condition]` → `[Expected Behavior]`

**2. Happy Paths & Integration Flows**
* `[Concrete standard input, e.g. qty=3, price=9.99]` → `[Expected Output/State Change]`
* `[Concrete standard input]` → `[Expected Output/State Change]`

**3. Representative Edge Cases**
* **Structural Boundaries:** `[concrete value, e.g. qty=0]` → `[expected outcome, e.g. returns 0.0]`; `[concrete value, e.g. qty=None]` → `[expected outcome, e.g. raises TypeError]`
* **Mathematical & Data Fuzzing:** `[technique used, e.g. Pairwise/MC-DC]` covering `[brief description of the parameter space]`; representative case `[concrete example]` → `[expected outcome]`

**4. Coverage Summary**
* **Total Planned Test Cases:** `[N]` (`[H]` Happy Path, `[B]` Structural Boundary, `[M]` Math/Data Fuzz — including parameterized expansions)
* **Target Coverage:** `[XX]%`

---
**PAUSE:** Does this test plan look correct, or would you like me to add/modify any edge cases before I generate the code?

## 7A. The Final Execution Report Template (Report File)

When executing Step 9, write this template VERBATIM to the report file (`<test_file_basename>.report.md`), including all `**bold**` field names, table syntax, bullet syntax, and section headers. Fill in only the bracketed placeholder values. Do not reorder fields. Do not omit fields. Do not dump raw terminal logs unless the user explicitly asks. This file holds the COMPLETE record — every test, not a subset. Write expected/actual values in plain, human-readable language (e.g. "raises ValueError" rather than a raw stack trace) so a non-technical reviewer can follow it without opening the code.

### 🏆 Test Generation Complete: `[Target Unit or Feature Name]`

* **Execution Mode:** `[Unit Mode OR Integration/Feature Mode]`
* **Target Test Suite Location:** `[Path to generated test file(s)]`
* **Framework & Context Detected:** `[e.g., pytest 7.4 + Local SQLite Fixture]`
* **Total Tests Generated:** `[N] (including parameterized expansions)`
* **Test Execution Results:** `[P] Passed, [F] Failed, [S] Skipped`
* **Iterations Used:** `[X]/3`
* **Final Coverage:** `[XX]%`

**Test-by-Test Results:**

| Test Name | Expected | Actual | Result |
|-----------|----------|--------|--------|
| `[test_name_1]` | `[expected outcome, plain language]` | `[actual outcome, plain language]` | `[✅ Pass / ❌ Fail / ⏭️ Skip]` |
| `[test_name_2]` | `[...]` | `[...]` | `[...]` |

**Coverage Breakdown:**
* `[Quick summary of what was successfully covered across the targeted workflow]`
* **Missed Lines:** `[List missed lines, or state "None"]`
* **Missed Lines Justification:** `[If coverage < target, explain exactly why those specific lines were unreachable or skipped. If target met, state "N/A"]`

## 7B. The Chat Summary Template (Printed in Chat)

When executing Step 9, print this template VERBATIM in chat/terminal after the report file has been written. Keep it short — a pointer and headline, not the report itself. Do not paraphrase headers. Do not include the full test-by-test table here.

### 🏆 Test Generation Complete: `[Target Unit or Feature Name]`

* **Results:** `[P]` passed, `[F]` failed, `[S]` skipped out of `[N]` tests — **`[XX]%` coverage** (`[X]`/3 iterations)
* **Full report:** `[path to <test_file_basename>.report.md]`

`[Include only if F > 0 or S > 0, otherwise omit this block entirely:]`
**Needs attention:**
* ❌ `[test_name]` — expected `[plain-language expected outcome]`, got `[plain-language actual outcome]`. `[One-line plausible cause, only if reasonably inferable from the diff — omit this clause otherwise.]`