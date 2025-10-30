# Python Files Summary

## Overview
This is a Streamlit-based educational application that generates pandas and SQL practice problems on-the-fly using the Claude API. Users view dataframes, solve problems with code, and receive instant feedback by comparing their output to expected results.

---

## Core Application Files

### `app.py` (main Streamlit application)
**Location:** Root directory
**Purpose:** Main Streamlit application with full user interface and core functionality

**Key Functions:**
- `execute_pandas(code, input_tables)` - Executes user's pandas code in a restricted namespace, returns (DataFrame, error_message)
- `execute_sql(query, input_tables)` - Executes user's SQL query using in-memory SQLite database, returns (DataFrame, error_message)
- `compare_dataframes(user_df, expected_df)` - Compares user output with expected output, checking shape, columns, and values; returns (is_correct, feedback_message)
- `display_problem(problem)` - Displays problem question and input tables in Streamlit UI

**Key Features:**
- Session state management for problems, user code, results, and feedback
- **Topic selector with checkboxes** - Users can select multiple topics to practice or leave all unchecked for random
- Available topics: filter_columns, filter_rows, aggregations, distinct, joins, order_by, limit
- **"Reveal Problem Info" button** - Topic and difficulty are always hidden until user clicks this button (next to "Run Code")
  - Loading messages also never reveal the topic to avoid giving hints
- Language selection (Pandas or SQL)
- Side-by-side comparison of user output vs expected output
- "Generate New Problem" button that respects selected topics
- Custom CSS for monospaced code input
- Comprehensive error handling with detailed feedback messages
- Execution timeout protection (5 second limit for user code)
- Robust API failure handling (keeps previous problem on error)
- Loading spinners and informative error messages

**Session State Variables:**
- `current_problem` - Currently displayed problem
- `result_df` - User's execution result
- `error_message` - Execution error if any
- `is_correct` - Boolean indicating if answer is correct
- `feedback_message` - Comparison feedback
- `show_expected` - Boolean for showing expected output
- `user_code` - User's code input
- `selected_topics` - List of selected topics (empty list means all topics)
- `topic_{topic_name}` - Individual checkbox states for each topic
- `problem_info_revealed` - Boolean tracking whether user clicked "Reveal Problem Info" button

**References:** `models.py` (Problem), `claude_client.py` (generate_problem)

---

### `models.py` (data structures)
**Location:** Root directory
**Purpose:** Defines the Problem data structure

**Classes:**
- `Problem` (dataclass) - Represents a practice problem
  - `input_tables: Dict[str, pd.DataFrame]` - Input data tables
  - `question: str` - Problem description in plain English
  - `expected_output: pd.DataFrame` - Correct answer
  - `topic: str` - Category (e.g., "filter_rows", "group_by", "joins")
  - `difficulty: Optional[str]` - "easy", "medium", or "hard" (defaults to "easy")
  - `__repr__()` - Pretty-prints problem structure with table info

**Verification:**
- Contains standalone verification code that creates a sample filtering problem with an employees DataFrame
- Can be run directly to test the Problem structure

---

### `claude_client.py` (Claude API integration)
**Location:** Root directory
**Purpose:** Claude API client for generating practice problems

**Key Functions:**
- `get_api_key()` - Retrieves API key from environment variable or Streamlit secrets
- `get_client()` - Returns initialized Anthropic client
- `test_api_connection()` - Tests basic API call
- `strip_markdown_code_blocks(text)` - Removes ```json``` formatting from responses
- `build_problem_generation_prompt(topic, difficulty)` - Builds detailed prompt for Claude
- `generate_problem(topic, difficulty, use_cache)` - Main function to generate Problem objects from Claude API

**Key Features:**
- Uses model: `claude-sonnet-4-5-20250929`
- `@lru_cache` decorator for caching API responses during development
- Comprehensive prompt engineering with:
  - Plain English requirements (no technical terminology in questions)
  - Single-operation focus for easy difficulty
  - JSON structured output format
  - Topic descriptions mapped from technical names to plain language
- JSON parsing with markdown code block stripping
- Robust error handling and validation
- Converts JSON table representations to pandas DataFrames

**Prompt Requirements:**
- Problems must be solvable in BOTH pandas AND SQL
- Questions written in plain English (no SQL/pandas terminology)
- Easy problems test exactly ONE concept
- Returns structured JSON with input_tables, question, expected_output, topic, difficulty

---

### `dataset_topics.py` (dataset variety library)
**Location:** Root directory
**Purpose:** Provides 100 diverse dataset topics for problem generation variety

**Key Features:**
- `DATASET_TOPICS` - List of 100 domain-only topic names
- Topics organized by category for reference:
  - Business (10): sales, customers, products, orders, employees, departments, retail, wholesale, consulting, suppliers
  - Education (8): school, university, courses, tutoring, training, academy, library, workshop
  - Technology (10): social-media, gaming, software, cloud, cybersecurity, analytics, database, networking, app-store, tech-support
  - Healthcare (7): hospital, clinic, pharmacy, lab, telemedicine, dentist, veterinary
  - Entertainment (8): movies, music, streaming, theater, concerts, festivals, gallery, museum
  - Finance (8): banking, investments, insurance, budgeting, trading, loans, accounting, credit-cards
  - Sports (8): basketball, soccer, tennis, olympics, fitness, marathon, gym, swimming
  - E-commerce (6): marketplace, shopping, auctions, subscriptions, reviews, wishlist
  - Transportation (7): flights, trains, rideshare, logistics, delivery, parking, shipping
  - Food & Beverage (7): restaurant, cafe, catering, food-truck, bakery, grocery, meal-kit
  - Real Estate (5): properties, rentals, mortgages, listings, property-management
  - Travel (6): hotels, tours, bookings, cruises, travel-agency, vacation-rentals
  - Manufacturing (5): factory, supply-chain, inventory, production, warehouse
  - Media (5): news, publishing, podcasts, journalism, advertising
- `get_random_topic()` - Returns a random topic from the library
- Built-in assertions to verify exactly 100 unique topics

**Design Philosophy:**
- Topics are domain-only suggestions (1-2 words max)
- Gives Claude flexibility to create appropriate table structures
- Generic enough to work with any skill type and complexity level
- Maximizes variety without rigid schema requirements

**Verification:**
- Contains standalone verification code that checks topic count and uniqueness
- Can be run directly to test the library: `uv run python dataset_topics.py`

---

### `main.py` (simple entry point)
**Location:** Root directory
**Purpose:** Basic hello world entry point (not actively used)

**Functionality:**
- Simple print statement: "Hello from emily-exam-practice!"
- Can be used for basic testing

---

## Test Files

### `test_pandas_execution.py`
**Location:** Root directory
**Purpose:** Tests for the `execute_pandas()` function (Step 3.2 verification)

**Test Cases:**
1. Valid filtering by salary (> 70000)
2. Valid filtering by department (Engineering)
3. Valid column selection
4. Error: Missing 'result' variable
5. Error: Syntax error (missing bracket)
6. Error: Non-existent column name
7. Error: Result is not a DataFrame
8. Valid: Using pandas groupby functions

**Creates:** Sample employees DataFrame with name, department, salary, years columns

---

### `test_sql_execution.py`
**Location:** Root directory
**Purpose:** Tests for the `execute_sql()` function (Step 3.3 verification)

**Test Cases:**
1. Valid: Filter by salary > 70000
2. Valid: Select specific columns with WHERE clause
3. Error: Invalid SQL syntax (missing FROM)
4. Error: Non-existent table
5. Error: Non-existent column
6. Valid: Aggregation query with GROUP BY

**Creates:** Sample employees DataFrame

---

### `test_edge_case.py`
**Location:** Root directory
**Purpose:** Tests edge case with incomplete SQL query

**Test Cases:**
- Incomplete WHERE clause: `SELECT * FROM employees WHERE salary >`
- Verifies error is caught and returned properly

---

### `test_pandas_error.py`
**Location:** Root directory
**Purpose:** Tests pandas error handling with full tracebacks

**Test Cases:**
1. KeyError: Wrong column name ('nonexistent_column')
2. NameError: Wrong table name ('wrong_table')

**Purpose:** Verify full traceback is returned for debugging

---

### `test_comparison.py`
**Location:** Root directory
**Purpose:** Comprehensive tests for `compare_dataframes()` function (Step 4.1 verification)

**Test Cases:**
1. Exact match → should pass
2. Different values → should fail with column info
3. Missing columns → should fail with helpful message
4. Extra columns → should fail with helpful message
5. Same data, different row order → should fail
6. Same data, different column order → should fail with "column order" message
7. Non-DataFrame input → should fail with type info
8. Different shape → should fail with shape info
9. Close float values (within tolerance) → should pass
10. Int vs Float equivalence → should pass

**Comparison Settings:**
- `check_dtype=False` - Lenient with int vs float
- `check_exact=False` - Approximate float comparison
- `rtol=1e-5, atol=1e-8` - Tolerance settings
- Row order and column order must match exactly (strict ordering)

---

### `test_prompt_generation.py`
**Location:** Root directory
**Purpose:** Tests the problem generation prompt (Step 5.2 verification)

**Test Function:**
- `test_prompt_generation(topic, difficulty)` - Sends prompt to Claude, parses response, validates structure

**Validation Checks:**
- Valid JSON parsing
- All required fields present (input_tables, question, expected_output, topic, difficulty)
- Input tables dict exists with at least one table
- Question is non-empty string
- Expected output has columns and data
- Topic and difficulty match request

**Test Cases:**
- ("filter_rows", "easy")
- ("group_by", "easy")
- ("joins", "medium")

---

### `test_generate_problem.py`
**Location:** Root directory
**Purpose:** Tests the complete `generate_problem()` function (Step 5.3 verification)

**Test Function:**
- `test_generate_problem()` - Calls generate_problem() and verifies the complete Problem object

**Verifications:**
1. Returns valid Problem instance
2. Has all required attributes (input_tables, question, expected_output, topic, difficulty)
3. DataFrames are valid and non-empty
4. Question is clear (non-empty, reasonable length)
5. Manual review prompt for expected output correctness

**Additional Testing:**
- `test_multiple_topics()` - Tests with different topic/difficulty combinations
- Test cases: filter_rows, filter_columns, group_by, joins with easy/medium difficulties

---

### `test_timeout.py`
**Location:** Root directory
**Purpose:** Tests execution timeout handling for both pandas and SQL (Step 6.3 verification)

**Test Functions:**
- `test_pandas_timeout()` - Verifies pandas code with infinite loop times out correctly after 5 seconds
- `test_sql_timeout()` - Verifies SQL execution works correctly with timeout protection
- `test_pandas_normal_execution()` - Ensures normal code still executes correctly with timeout protection

**Verifications:**
1. Timeout triggers after EXECUTION_TIMEOUT seconds (5s)
2. Timeout error messages are clear and helpful
3. Normal code execution is not affected by timeout protection
4. All execution paths handle timeouts gracefully

---

## File Dependencies

```
app.py
├── models.py (Problem class)
└── claude_client.py (generate_problem)

claude_client.py
├── models.py (Problem class)
└── dataset_topics.py (will be integrated in Step 8.2)

dataset_topics.py
└── (standalone, no dependencies)

test files
├── app.py (execute_pandas, execute_sql, compare_dataframes)
└── claude_client.py (for prompt testing)
```

---

## Development Progress (Based on plan.md)

### Completed Steps:
- ✅ Step 1.1: Project initialization
- ✅ Step 1.2: Basic Streamlit layout
- ✅ Step 2.1: Problem data structure (models.py)
- ✅ Step 2.2: Display dataframes
- ✅ Step 3.1: Code input interface
- ✅ Step 3.2: Execute pandas code
- ✅ Step 3.3: Execute SQL code
- ✅ Step 3.4: Wire up code execution
- ✅ Step 4.1: DataFrame comparison
- ✅ Step 4.2: Display feedback
- ✅ Step 5.1: Claude API client setup
- ✅ Step 5.2: Problem generation prompt design
- ✅ Step 5.3: Problem generator implementation
- ✅ Step 6.1: Connect generator to app
- ✅ Step 6.2: Add "New Problem" button
- ✅ Step 6.3: Handle edge cases (loading states, API failures, timeouts)
- ✅ Step 7.1: Add topic selector (sidebar with checkboxes for multiple topic selection)

### Current Development (from new-steps.md):
- ✅ Step 8.1: Create Dataset Topic Library (dataset_topics.py with 100 diverse topics)

### Next Steps (from new-steps.md):
- Step 8.2: Integrate random topic selection into problem generation
- Step 8.3: Add solution verification to Problem structure
- Step 8.4: Implement solution verification
- Step 8.5: Add "Show Reference Solutions" button
- Step 8.6: Add export/import problem functionality
- Step 9.1+: Add derived column skill
- Step 10.1+: Implement medium difficulty
- Step 11.1+: Implement hard difficulty with advanced topics

---

## Key Technical Details

### Execution Safety
- Pandas: Uses `exec()` with restricted namespace (contains only pd, input tables, and builtins)
- SQL: Uses in-memory SQLite database (`:memory:`)
- Both return (result, error) tuple for safe error handling
- **Timeout Protection**: 5 second execution limit using signal-based timeout (Unix/macOS)
  - Prevents infinite loops and slow operations
  - Graceful timeout error messages with helpful guidance
  - Cross-platform timeout context manager with fallback for Windows and Streamlit threading
  - Catches both AttributeError (Windows) and ValueError (Streamlit threading) gracefully

### Error Handling & Robustness
- **Code Execution Errors**:
  - Timeout detection with user-friendly messages
  - Full traceback for debugging syntax and runtime errors
  - Validation of result type and presence
- **API Failure Handling**:
  - Keeps previous problem available when new problem generation fails
  - Specific error messages for common API issues (auth, timeout, rate limit, overload)
  - Helpful troubleshooting guidance with API key setup instructions
  - Validates API responses for required fields and data integrity
- **Loading States**:
  - Spinners for initial problem generation and new problem requests
  - Topic-specific loading messages (e.g., "Generating new filter_rows problem...")
  - Success notifications when problems are generated

### Comparison Logic
- Strict row order and column order matching
- Lenient data type comparison (int == float)
- Float tolerance: rtol=1e-5, atol=1e-8
- Detailed error messages for different failure modes

### API Configuration
- Model: claude-sonnet-4-5-20250929
- Max tokens: 2000
- Caching: LRU cache for development (hash-based cache key)
- Error handling: Validates JSON structure and required fields

### Streamlit Features
- Session state for persistence across reruns
- **Multi-topic selector**: Checkboxes allow users to select one or more topics to practice
  - Empty selection = all topics (random mode)
  - Specific selections = only generate problems from selected topics
- **Manual problem info reveal**: "Reveal Problem Info" button always keeps topic/difficulty hidden until clicked
  - Resets to hidden state on every new problem
  - Encourages users to attempt problems without hints
- Custom CSS for monospaced code input
- Spinners for API calls
- Side-by-side column layout for output comparison
- Success/error message styling
- Sidebar organization with topic selector and problem generator controls
- Two-column button layout for "Run Code" and "Reveal Problem Info"

---

## Usage Notes

### Running the App
```bash
uv run streamlit run app.py
```

### Running Tests
```bash
uv run python test_pandas_execution.py
uv run python test_sql_execution.py
uv run python test_comparison.py
uv run python test_prompt_generation.py
uv run python test_generate_problem.py
uv run python test_timeout.py  # Takes ~5 seconds due to timeout test
```

### Environment Variables
- `ANTHROPIC_API_KEY` - Required for Claude API access
- Can also be set in `.streamlit/secrets.toml`
