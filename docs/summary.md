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
Streamlit educational app that generates pandas/SQL practice problems on-the-fly using Claude API. Users solve problems with code and receive instant feedback by comparing output to expected results.

---

## Core Application Files

### `app.py` (main Streamlit application)
**Purpose:** Main UI and problem practice workflow

**Key Functions:**
- `verify_problem_solutions(problem)` → verification results dict
- `display_problem(problem)` - Renders problem UI
- Imports execution functions from `execution.py`

**UI Features:**
- Difficulty selector: Easy (1 skill), Medium (2-3 skills), Hard (3-4 skills)
- Multi-topic checkbox selector (empty = all topics)
- "Reveal Problem Info" button (hides topic/difficulty until clicked)
- "Show Reference Solutions" button (displays verified pandas/SQL solutions)
- Export/Import problem as JSON
- Generic loading messages (never reveal difficulty or topics)
- Automatic solution verification with logging

**Available Topics:** filter_columns, filter_rows, aggregations, distinct, joins, order_by, limit, derived_column

**Dependencies:** `models.py`, `claude_client.py`, `execution.py`

---

### `execution.py` (code execution and comparison)
**Purpose:** Shared execution utilities used by both `app.py` and `claude_client.py`

**Key Functions:**
- `execute_pandas(code, input_tables)` → (DataFrame | None, error | None)
- `execute_sql(query, input_tables)` → (DataFrame | None, error | None)
- `compare_dataframes(user_df, expected_df)` → (is_correct, feedback_message)
- `time_limit(seconds)` - Context manager for 5-second timeout

**Safety Features:**
- Restricted namespace for pandas execution
- In-memory SQLite for SQL execution
- 5-second timeout with graceful fallback for Windows/Streamlit

**Note:** Avoids circular imports by being standalone module

---

### `models.py` (data structures)
**Purpose:** Core data model

**Classes:**
- `Problem` (dataclass) - input_tables, question, expected_output, topic, difficulty, pandas_solution, sql_solution, pandas_only

**Key Methods:**
- `to_json()` / `from_json()` - Serialize/deserialize with DataFrame conversion
- `pandas_only` field indicates pivot/melt problems (SQL disabled in UI)

---

### `claude_client.py` (Claude API integration)
**Purpose:** Generate problems via Claude API

**Key Functions:**
- `generate_problem(topic, difficulty, selected_topics, use_cache)` → Problem
- `build_problem_generation_prompt(skills, difficulty, dataset_topic, use_cte, num_ctes)` → str

**Model:** `claude-sonnet-4-5-20250929`

**Critical Behavior:**
- Claude generates `pandas_solution` and `sql_solution` (NOT expected_output)
- Both solutions are executed using `execution.py`
- `expected_output` is derived from executed solutions (must match exactly)
- Problems are rejected if solutions don't match or fail execution
- This ensures every generated problem is guaranteed solvable and correct

**Prompt Design:**
- Plain English questions, solvable in both pandas and SQL
- Uses random dataset topic from 100-topic library for variety
- Multi-skill combinations for medium/hard (2-3 or 3-4 skills)
- CTE requirements: Easy (none), Medium (50% chance), Hard (1-3 CTEs)
- Derived column subtypes: Arithmetic, Conditional (Easy+), Date (Medium+)

**Dependencies:** `models.py`, `dataset_topics.py`, `difficulty_manager.py`, `execution.py`

---

### `dataset_topics.py`
**Purpose:** 100 diverse domain topics for variety

**Key Content:**
- `DATASET_TOPICS` - 100 domains across 14 categories
- `get_random_topic()` - Returns random topic
- Topics are 1-2 words (e.g., "library", "hospital")

---

### `difficulty_manager.py`
**Purpose:** Skill selection and CTE requirements logic

**Key Functions:**
- `select_skills_for_difficulty(difficulty, selected_topics)` → List[str]
- `should_use_cte(difficulty, skills)` → (use_cte, num_ctes)

**Logic:**
- Easy: 1 skill, no CTEs
- Medium: 2-3 skills, 50% CTE
- Hard: Advanced topic handling with probabilities:
  - 20% chance: pivot/melt (standalone, pandas-only)
  - 20% chance: datatypes (standalone)
  - 30% chance: cross_join + 2-3 easy skills
  - 30% chance: 3-4 easy skills
  - Always uses 1-3 CTEs

**Advanced Topics:** datatypes, cross_join, pivot, melt

---

## Test Files

**Test Coverage:**
- Execution: pandas/SQL execution, timeout, error handling
- Comparison: DataFrame comparison with type tolerance
- Generation: Claude API integration, prompt generation, solution verification
- Features: Export/import, derived_column subtypes
- Edge cases: Invalid queries, incomplete code, timeouts

**Note:** DataFrame comparison is lenient with int/float types but strict on row/column order

---

## File Dependencies

**Import Chain:**
- `app.py` → `models.py`, `claude_client.py`, `execution.py`
- `claude_client.py` → `models.py`, `dataset_topics.py`, `difficulty_manager.py`, `execution.py`
- `execution.py` → standalone (avoids circular imports)
- `dataset_topics.py`, `difficulty_manager.py` → standalone libraries

---

## Key Technical Decisions

**Quality Assurance (Critical):**
- Claude generates solutions, NOT expected_output
- Expected output derived by executing both solutions
- Problems rejected if solutions don't match or fail
- Guarantees every problem is solvable and correct

**Execution Safety:**
- 5-second timeout with graceful fallback
- Restricted namespace (pandas), in-memory DB (SQL)
- Strict row/column order, lenient type comparison

**UX Patterns:**
- Loading messages never reveal problem details
- "Reveal Problem Info" hides topic/difficulty until clicked
- API failures keep previous problem (don't leave user stuck)

---

## Development Progress

**Completed Steps:** 1.1 through 11.3

**Current State:**
- ✅ Full basic app with execution and comparison
- ✅ Claude API integration with quality assurance (solutions verified before accepting problem)
- ✅ 100-topic dataset library for variety
- ✅ 8 foundational skills including derived_column (arithmetic, conditional, date subtypes)
- ✅ Difficulty levels: Easy (1 skill), Medium (2-3 skills), Hard (advanced topics + multi-skill)
- ✅ CTE requirements: Easy (never), Medium (50% chance, 1 CTE), Hard (always, 1-3 CTEs based on skill count)
- ✅ Reference solutions UI, export/import functionality
- ✅ Shared execution module (`execution.py`) prevents circular imports
- ✅ Medium difficulty tested end-to-end (`test_medium_problems.py`)
- ✅ Advanced topics for hard problems: datatypes, cross_join, pivot, melt
- ✅ Hard problems always use CTEs with smart distribution (more skills = more CTEs)
- ✅ Pandas-only problems (pivot/melt) supported: SQL option disabled, sql_solution skipped

**Next Up (new-steps.md):**
- Step 11.4: Test hard difficulty problems

---

## Running the App

**Commands:**
- Start: `uv run streamlit run app.py`
- Tests: `uv run python test_*.py`
- Env: `ANTHROPIC_API_KEY` required
