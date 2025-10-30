# Python Files Summary

<!--
INSTRUCTIONS FOR THIS FILE:
This file is a context management tool for LLM-assisted development. It should be:
- Read before every step in new-steps.md
- Updated after completing each step
- Kept concise and high-level (details are in the actual code files)

PURPOSE:
- Help the LLM quickly understand which files exist and their responsibilities
- Provide enough context to know which files to read for detailed implementation
- Track development progress through the plan (completed vs pending steps)
- NOT a detailed code reference (the LLM will read actual files for details)

CONTENT GUIDELINES:
✓ Include: File names, locations, key function signatures, high-level architecture
✓ Include: Important relationships between files (imports, dependencies)
✓ Include: Critical design decisions (safety, error handling, UX patterns)
✓ Include: Current development status (what's done, what's next)
✗ Exclude: Full implementations, detailed algorithms, complete code listings
✗ Exclude: Every single function parameter or variable
✗ Exclude: Information easily found by reading the actual file

Think of this as a "map" of the codebase, not the codebase itself.
-->

## Overview
This is a Streamlit-based educational application that generates pandas and SQL practice problems on-the-fly using the Claude API. Users view dataframes, solve problems with code, and receive instant feedback by comparing their output to expected results.

---

## Core Application Files

### `app.py` (main Streamlit application)
**Purpose:** Main UI and core functionality for problem practice

**Key Functions:**
- `execute_pandas(code, input_tables)` → (DataFrame | None, error | None)
- `execute_sql(query, input_tables)` → (DataFrame | None, error | None)
- `compare_dataframes(user_df, expected_df)` → (is_correct, feedback_message)
- `verify_problem_solutions(problem)` → dict with verification results (pandas_valid, sql_valid, errors, feedback)
- `display_problem(problem)` - Renders problem UI

**Critical Features:**
- 5-second execution timeout for user code safety
- Multi-topic checkbox selector (empty = all topics)
- "Reveal Problem Info" button (hides topic/difficulty until clicked)
- Robust API error handling (keeps previous problem on failure)
- Session state for persistence across reruns
- Automatic verification of Claude's reference solutions with logging

**Available Topics:** filter_columns, filter_rows, aggregations, distinct, joins, order_by, limit

**Dependencies:** `models.py` (Problem), `claude_client.py` (generate_problem)

---

### `models.py` (data structures)
**Purpose:** Core data model for practice problems

**Classes:**
- `Problem` (dataclass) - Contains input_tables (dict), question (str), expected_output (DataFrame), topic (str), difficulty (str), pandas_solution (Optional[str]), sql_solution (Optional[str])
- Solutions are Claude's reference implementations that produce the expected output

---

### `claude_client.py` (Claude API integration)
**Purpose:** Generate problems via Claude API

**Key Functions:**
- `generate_problem(topic, difficulty, use_cache)` → Problem
- `build_problem_generation_prompt(topic, difficulty, dataset_topic)` → str
- `select_random_topic()` → str
- Helper functions: get_api_key(), get_client(), strip_markdown_code_blocks()

**Model:** `claude-sonnet-4-5-20250929`

**Prompt Design:**
- Plain English questions (no SQL/pandas terminology)
- Easy = ONE operation only
- JSON structured output with pandas_solution and sql_solution fields
- Must be solvable in both pandas AND SQL
- Random dataset topic selection for variety (integrated in Step 8.2)
- Reference solutions: pandas assigns to 'result', SQL is complete SELECT query

**Dependencies:** `models.py` (Problem), `dataset_topics.py` (get_random_topic)

---

### `dataset_topics.py` (dataset variety library)
**Purpose:** Provides 100 diverse domain topics for problem variety

**Key Content:**
- `DATASET_TOPICS` - List of 100 domain names across 14 categories (business, education, tech, healthcare, etc.)
- `get_random_topic()` - Returns random topic
- Topics are 1-2 word domains (e.g., "library", "hospital") giving Claude flexibility

**Integration:** Fully integrated in Step 8.2 - every problem now uses a random dataset topic

---

### `main.py`
**Purpose:** Simple hello world entry point (not actively used)

---

## Test Files

**Available Tests:**
- `test_pandas_execution.py` - Tests execute_pandas() with valid/invalid cases
- `test_sql_execution.py` - Tests execute_sql() with valid/invalid queries
- `test_comparison.py` - Tests compare_dataframes() logic (10 test cases covering matches, mismatches, ordering, type tolerance)
- `test_prompt_generation.py` - Tests Claude API prompt and JSON response parsing
- `test_generate_problem.py` - Tests full generate_problem() workflow
- `test_timeout.py` - Tests 5-second timeout for pandas and SQL execution
- `test_edge_case.py` - Tests incomplete SQL queries
- `test_pandas_error.py` - Tests error traceback handling
- `test_solution_verification.py` - Tests verify_problem_solutions() function with multiple problems (100% success rate)

**Key Testing Details:**
- DataFrame comparison: Lenient with int/float types, strict row/column order, float tolerance (rtol=1e-5, atol=1e-8)
- All tests use sample employees DataFrame for consistency

---

## File Dependencies

**Import Chain:**
- `app.py` → imports `models.py`, `claude_client.py`
- `claude_client.py` → imports `models.py`, `dataset_topics.py`
- `dataset_topics.py` → standalone library (provides topics)
- Test files → import from `app.py` and `claude_client.py`

---

## Key Technical Decisions

**Execution Safety:**
- Pandas: Restricted namespace (only pd, input tables, builtins)
- SQL: In-memory SQLite (`:memory:`)
- 5-second timeout using signal (Unix/macOS) with graceful fallback for Windows/Streamlit threading

**Error Handling:**
- API failures keep previous problem (don't leave user stuck)
- Full tracebacks for debugging user code errors
- Specific error messages for common API issues (auth, timeout, rate limits)
- Solution verification logs warnings when reference solutions fail but accepts problem (MVP approach)

**Comparison Logic:**
- Strict row and column order
- Lenient with int/float type differences
- Float tolerance: rtol=1e-5, atol=1e-8

**UX Patterns:**
- "Reveal Problem Info" hides topic/difficulty until clicked (prevents hints)
- Loading messages never reveal problem details
- Multi-topic selector (empty = random from all topics)

---

## Development Progress

**Completed:** Steps 1.1 through 8.4 (full basic app + topic library + random topic integration + reference solutions + solution verification)

**What's New in Step 8.4:**
- Added `verify_problem_solutions(problem)` function in app.py
- Verification runs automatically after each problem generation
- Checks both pandas and SQL solutions against expected output
- Logs warnings when solutions fail verification (MVP: accepts problem anyway)
- Test suite confirms 100% verification success rate across multiple topics

**Next Up (new-steps.md):**
- Step 8.5-8.6: UI for showing reference solutions, export/import problem functionality
- Step 9: Add "derived_column" skill
- Step 10: Medium difficulty (2-3 skill combinations)
- Step 11: Hard difficulty (3-4 skills + advanced topics like pivot/melt/cross_join)

---

## Running the App

**Start app:** `uv run streamlit run app.py`
**Run tests:** `uv run python test_*.py`
**Env required:** `ANTHROPIC_API_KEY` (or in `.streamlit/secrets.toml`)
