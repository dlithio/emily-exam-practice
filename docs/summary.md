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
- "Show Reference Solutions" button (displays Claude's verified pandas and SQL solutions in expandable sections)
- "Export Problem" button (downloads current problem as JSON file with timestamp)
- "Import Problem" file uploader (loads problem from JSON with validation and error handling)
- Robust API error handling (keeps previous problem on failure)
- Session state for persistence across reruns
- Automatic verification of Claude's reference solutions with logging

**Available Topics:** filter_columns, filter_rows, aggregations, distinct, joins, order_by, limit, derived_column

**Dependencies:** `models.py` (Problem), `claude_client.py` (generate_problem)

---

### `models.py` (data structures)
**Purpose:** Core data model for practice problems

**Classes:**
- `Problem` (dataclass) - Contains input_tables (dict), question (str), expected_output (DataFrame), topic (str), difficulty (str), pandas_solution (Optional[str]), sql_solution (Optional[str])
- Solutions are Claude's reference implementations that produce the expected output

**Key Methods:**
- `to_json()` → Dict[str, Any] - Serializes Problem to JSON-compatible dict (converts DataFrames to JSON format)
- `from_json(json_dict)` → Problem - Creates Problem from JSON dict with validation
- `__repr__()` → str - Pretty prints problem structure

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
- Derived column subtypes:
  - Easy difficulty: Arithmetic (math operations), Conditional (boolean/category)
  - Medium/Hard: Also includes Date (extract date components)

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

### `difficulty_manager.py` (skill composition logic)
**Purpose:** Handles skill selection and CTE requirements for different difficulty levels

**Key Functions:**
- `select_skills_for_difficulty(difficulty, selected_topics)` → List[str]
- `should_use_cte(difficulty, skills)` → (use_cte: bool, num_ctes: int)

**Constants:**
- `EASY_SKILLS` - List of 8 foundational topics (filter_columns, filter_rows, aggregations, distinct, joins, order_by, limit, derived_column)

**Logic:**
- Easy: 1 skill, no CTEs
- Medium: 2-3 skills, 50% chance of 1 CTE
- Hard: 3-4 skills, always uses CTEs (1-3 depending on skill count)

**Integration:** Will be used by claude_client.py for medium/hard problem generation (Step 10.2+)

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
- `test_export_import.py` - Tests Problem.to_json() and Problem.from_json() with data integrity checks and error handling
- `test_derived_column.py` - Comprehensive tests for all derived_column subtypes (Arithmetic, Conditional, Date) in both pandas and SQL

**Key Testing Details:**
- DataFrame comparison: Lenient with int/float types, strict row/column order, float tolerance (rtol=1e-5, atol=1e-8)
- All tests use sample employees DataFrame for consistency

---

## File Dependencies

**Import Chain:**
- `app.py` → imports `models.py`, `claude_client.py`
- `claude_client.py` → imports `models.py`, `dataset_topics.py` (will import `difficulty_manager.py` in Step 10.2)
- `dataset_topics.py` → standalone library (provides topics)
- `difficulty_manager.py` → standalone library (provides skill selection logic)
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

**Completed:** Steps 1.1 through 10.1 (full basic app + topic library + random topic integration + reference solutions + solution verification + reference solutions UI + export/import functionality + derived_column topic with all subtypes fully tested + skill composition logic for medium/hard difficulties)

**What's New in Step 10.1:**
- Created `difficulty_manager.py` with skill composition logic
- Added `EASY_SKILLS` constant (list of 8 foundational topics)
- Implemented `select_skills_for_difficulty(difficulty, selected_topics)` function:
  - Easy: Returns 1 skill
  - Medium: Returns 2-3 skills
  - Hard: Returns 3-4 skills
  - Respects user-selected topics when provided
- Implemented `should_use_cte(difficulty, skills)` function:
  - Easy: Never uses CTEs (False, 0)
  - Medium: 50% chance of 1 CTE
  - Hard: Always uses CTEs (1-3 based on number of skills)
- Tested all functions with multiple samples - working correctly
- Module ready for integration in claude_client.py (Step 10.2)

**What's New in Step 8.6:**
- Added "Export Problem" button in sidebar "Save & Share" section
- Export generates JSON file with format: `problem_{topic}_{timestamp}.json`
- Added "Import Problem" file uploader with comprehensive validation
- Import includes error handling for invalid JSON, missing fields, and malformed data
- JSON format preserves all problem data: input_tables, question, expected_output, topic, difficulty, pandas_solution, sql_solution
- DataFrames serialized as {columns: [...], data: [{...}, ...]} format for readability
- Import automatically clears previous session state and loads new problem
- Success messages display imported problem's topic and difficulty
- File ID tracking prevents re-processing uploads on rerun (fixes Streamlit MediaFileHandler errors)
- Import tracking resets when generating new problem (allows re-importing same file)
- Added `Problem.to_json()` and `Problem.from_json()` methods to models.py
- Added `test_export_import.py` for testing serialization integrity and error handling
- Added `test_import_logic.py` for testing file ID tracking and import logic

**What's New in Step 9.1:**
- Added "derived_column" as new easy skill (8th foundational topic)
- Added derived_column to TOPICS list in app.py
- Added topic description in claude_client.py topic_descriptions mapping
- Implemented derived_column subtypes with difficulty-based selection:
  - Arithmetic: Math operations on existing columns (e.g., total = price * quantity)
  - Conditional: Boolean/categorical columns (e.g., is_passing = score >= 60)
  - Date: Extract date components (e.g., year from timestamp) - Medium/Hard only
- Easy difficulty only uses Arithmetic and Conditional (Date requires pd.to_datetime conversion)
- Prompt builder now includes derived_column-specific instructions
- Topic appears in sidebar checkbox list for user selection

**What's New in Steps 9.2 & 9.3:**
- Step 9.2 (Prompt Enhancement): Enhanced build_problem_generation_prompt() in claude_client.py:171-196
  - Random subtype selection based on difficulty (Easy: Arithmetic/Conditional only; Medium/Hard: includes Date)
  - Detailed examples for each subtype (arithmetic formulas, conditional logic, date extraction)
  - Clear instructions for Claude to create problems requiring derived columns in output
- Step 9.3 (Comprehensive Testing): Created test_derived_column.py with 6 test cases:
  - Arithmetic derivation (single and multi-column: price*quantity, math+english)
  - Conditional derivation (boolean: score>=60, categorical: tier in ['Gold','Platinum'])
  - Date derivation (year and month extraction from date strings)
  - All tests verify both pandas and SQL implementations work correctly
- Generated and verified 5+ actual problems using Claude API - 100% success rate
- All three subtypes generate valid problems solvable in both pandas and SQL

**Next Up (new-steps.md):**
- Step 10.2: Update problem generation for multi-skill (integrate difficulty_manager with Claude API)
- Step 10.3: Update UI for difficulty selection (add radio buttons)
- Step 10.4: Test medium difficulty problems
- Step 11: Hard difficulty (3-4 skills + advanced topics like pivot/melt/cross_join)

---

## Running the App

**Start app:** `uv run streamlit run app.py`
**Run tests:** `uv run python test_*.py`
**Env required:** `ANTHROPIC_API_KEY` (or in `.streamlit/secrets.toml`)
