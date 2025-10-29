# Pandas & SQL Practice App - Development Plan

## Overview
Build a Streamlit app that generates pandas/SQL problems on-the-fly using Claude API. Users view dataframes, solve problems with code, and get instant feedback by comparing their output to expected results.

## Target Skills (Priority Order)
**Foundational (Focus Here):**
1. Filter columns (SELECT/df[[]])
2. Filter rows (WHERE/df[condition])
3. Aggregations (GROUP BY/groupby)
4. Distinct values
5. Joins (inner, left, outer)
6. Order by
7. Limit

**Advanced (Lower Priority):**
8. Datatypes & conversions
9. CTEs (SQL only)
10. Cross joins
11. Creating dataframes from scratch
12. Pivot/melt (wide ↔ long)

---

## Phase 1: Basic Infrastructure

### Step 1.1: Initialize Project
**Task:** Set up project structure and dependencies
**Actions:**
- Create `app.py` for main Streamlit app
- Use `uv add` for dependencies:
  - streamlit
  - pandas (all SQL will be run using pd.read_sql(...))
  - anthropic (Claude API)
  - sqlite3 (built-in)

**Verification:**
```bash
uv run streamlit run app.py
```
Should see a blank/hello world Streamlit page in browser

---

### Step 1.2: Basic Streamlit Layout
**Task:** Create skeleton UI with placeholder content
**Actions:**
- Add title: "Pandas & SQL Practice"
- Add section headers: "Problem", "Your Code", "Result"
- Add placeholder text in each section

**Verification:**
App displays three distinct sections with headers and placeholder text

---

## Phase 2: Data Display & Problem Structure

### Step 2.1: Create Problem Data Structure
**Task:** Define how problems are represented
**Actions:**
- Create `models.py` with `Problem` class/dict containing:
  - `input_tables`: dict of {table_name: DataFrame}
  - `question`: str (description of what to do)
  - `expected_output`: DataFrame
  - `topic`: str (e.g., "filter_rows", "group_by")
  - `difficulty`: str (optional: "easy", "medium", "hard")

**Verification:**
Create a hardcoded sample problem and print it. Verify structure makes sense.

---

### Step 2.2: Display Dataframes
**Task:** Show input tables nicely formatted in Streamlit
**Actions:**
- Use `st.dataframe()` or `st.table()` to display DataFrames
- Create a function `display_problem(problem)` that:
  - Shows the question text
  - Displays all input tables with labels
  - Hides the expected output (that's the answer!)

**Verification:**
Run app with hardcoded problem. Tables should display cleanly with proper formatting.

---

## Phase 3: User Input & Code Execution

### Step 3.1: Add Code Input Interface
**Task:** Create UI for user to write and submit code
**Actions:**
- Add radio button to select language: "Pandas" or "SQL"
- Add `st.text_area()` for code input (use `height=200` for better UX)
- Add "Run Code" button
- Add placeholder for result display

**Verification:**
Type code in text area, select language, click button. Nothing happens yet but UI is ready.

---

### Step 3.2: Execute Pandas Code Safely
**Task:** Run user's pandas code and capture result
**Actions:**
- Create `execute_pandas()` function:
  - Prepare namespace with input tables as variables
  - Use `exec()` to run user code in restricted namespace
  - Capture result (expect user to assign to `result` variable)
  - Handle errors gracefully with try/except
- Test with simple hardcoded example

**Verification:**
```python
# Example user code
result = employees[employees['salary'] > 70000]
```
Should execute and return filtered DataFrame. Test error handling with invalid code.

---

### Step 3.3: Execute SQL Code Safely
**Task:** Run user's SQL code and capture result
**Actions:**
- Create `execute_sql()` function:
  - Create in-memory SQLite/DuckDB database
  - Load input tables into database
  - Execute user's SQL query with `pd.read_sql()`
  - Handle errors gracefully
- Test with simple hardcoded example

**Verification:**
```sql
SELECT * FROM employees WHERE salary > 70000
```
Should execute and return filtered DataFrame. Test error handling with invalid SQL.

---

### Step 3.4: Wire Up Code Execution
**Task:** Connect user input to execution functions
**Actions:**
- When "Run Code" is clicked:
  - Check selected language
  - Call appropriate execution function
  - Store result in session state
  - Display result (or error) to user

**Verification:**
Try both pandas and SQL code with a hardcoded problem. Should see results displayed.

---

## Phase 4: Result Comparison & Feedback

### Step 4.1: Implement DataFrame Comparison
**Task:** Check if user's output matches expected output
**Actions:**
- Create `compare_dataframes(user_df, expected_df)` function:
  - Check if both are DataFrames (user might return wrong type)
  - Check shape matches
  - Sort both DataFrames consistently (to handle order differences)
  - Use `pd.testing.assert_frame_equal()` or custom comparison
  - Return (is_correct, feedback_message)
- Handle edge cases: wrong columns, wrong dtypes, close floats

**Verification:**
Test with:
- Exact match → should pass
- Different values → should fail with helpful message
- Wrong columns → should fail with helpful message
- Same data, different order → should pass (if order doesn't matter)

---

### Step 4.2: Display Feedback
**Task:** Show user if they got it right or wrong
**Actions:**
- After code execution, run comparison
- If correct: show success message (green, `st.success()`)
- If wrong: show error message with details (red, `st.error()`)
- Show both user's output and expected output side-by-side for comparison
- Add optional "Show Expected Output" button if wrong

**Verification:**
Try correct and incorrect solutions. Verify feedback is clear and helpful.

---

## Phase 5: Claude API Integration

### Step 5.1: Set Up Claude API Client
**Task:** Configure API access
**Actions:**
- Add `anthropic` package
- Create `claude_client.py` with client initialization
- Store API key in environment variable or Streamlit secrets
- Test basic API call

**Verification:**
Send simple prompt to Claude and print response. Verify API key works.

---

### Step 5.2: Design Problem Generation Prompt
**Task:** Create prompt that generates problems in correct format
**Actions:**
- Write prompt that instructs Claude to:
  - Create 1-2 small DataFrames (input tables)
  - Create a word problem asking to do a specific operation
  - Provide the expected output DataFrame
  - Ensure problem is solvable in both pandas AND SQL
  - Return everything in structured JSON format
- Specify which topic/skill to focus on (pass as parameter)
- Test prompt in Claude.ai first to refine

**Verification:**
Manually send prompt to Claude API and inspect response. Verify format is parseable and complete.

---

### Step 5.3: Implement Problem Generator
**Task:** Function that calls Claude and returns Problem object
**Actions:**
- Create `generate_problem(topic, difficulty)` function:
  - Build prompt with topic/difficulty
  - Call Claude API
  - Parse JSON response
  - Convert string representations to actual DataFrames
  - Return Problem object
- Handle API errors gracefully
- Add caching to avoid regenerating during development

**Verification:**
Call `generate_problem("filter_rows", "easy")` and verify:
- Returns valid Problem object
- DataFrames look reasonable
- Question is clear
- Expected output is correct

---

## Phase 6: Full Integration

### Step 6.1: Connect Generator to App
**Task:** Generate problems on demand in Streamlit
**Actions:**
- Use `st.session_state` to store current problem
- On first load, generate a problem
- Display the generated problem using existing display functions
- Test that everything works together

**Verification:**
Start app → should automatically generate and display a problem. Solve it and verify comparison works.

---

### Step 6.2: Add "New Problem" Button
**Task:** Let user request new problems
**Actions:**
- Add button "Generate New Problem"
- Add dropdown to select topic (or "Random")
- On click, generate new problem and update session state
- Clear user's code input and previous results

**Verification:**
Click "New Problem" multiple times. Should get different problems. Try different topics.

---

### Step 6.3: Handle Edge Cases
**Task:** Make app robust
**Actions:**
- Handle slow API responses (add spinner)
- Handle API failures (show error, keep previous problem)
- Handle user code timeout (set execution timeout)
- Handle malformed API responses (retry or show error)
- Add loading states for better UX

**Verification:**
Test various failure scenarios. App should never crash, always give helpful feedback.

---

## Phase 7: Polish & Enhancement

### Step 7.1: Add Topic Selector
**Task:** Let user focus on specific skills
**Actions:**
- Add sidebar with checkboxes for each foundational topic
- Generate problems only from selected topics
- Show which topic the current problem is testing

**Verification:**
Select only "filter_rows" → should only get filtering problems

---

### Step 7.2: Add Difficulty Levels
**Task:** Support progressive difficulty
**Actions:**
- Add difficulty selector: Easy, Medium, Hard
- Update prompt to generate appropriate difficulty:
  - Easy: Single operation, small data
  - Medium: Combined operations, medium data
  - Hard: Multi-step, larger data, edge cases
- Show current difficulty in UI

**Verification:**
Try each difficulty level. Verify problems get appropriately harder.

---

### Step 7.3: Add Progress Tracking (Optional)
**Task:** Track user's practice session
**Actions:**
- Use session state to track:
  - Problems attempted
  - Problems solved correctly
  - Topics covered
- Display stats in sidebar
- Optional: Add streak counter, timing

**Verification:**
Solve several problems. Stats should update correctly.

---

### Step 7.4: Improve UX & Styling (Optional)
**Task:** Make app more pleasant to use
**Actions:**
- Add syntax highlighting to code input (via custom component or st.code)
- Add better formatting for DataFrames
- Add instructions/help text
- Add keyboard shortcuts (e.g., Ctrl+Enter to run)
- Add dark mode support
- Add example solutions (show after user tries)

**Verification:**
Use the app for 5-10 problems. Note any friction points and improve.

---

## Testing Strategy

After each phase:
1. **Manual Testing:** Try the feature yourself
2. **Edge Cases:** Try to break it (invalid input, empty data, etc.)
3. **User Flow:** Can someone who's never seen it understand what to do?

---

## Future Enhancements (Post-MVP)

- **Multiple choice questions** for faster practice
- **Hints system** (progressively revealing hints)
- **Solution explanations** from Claude after each problem
- **Leaderboard/persistence** (save progress across sessions)
- **Mobile-friendly** design
- **Export practice history** (CSV of problems and solutions)
- **Pre-generated problem bank** (for offline use or faster loading)
- **Spaced repetition** (re-show problems user struggled with)

---

## Notes

- **Security:** `exec()` is dangerous. For production, consider a safer sandbox (containers, pyodide, etc.)
- **Cost:** Each problem generation costs API credits. Monitor usage.
- **Quality:** Claude-generated problems should be validated. Add manual review process if needed.
- **Database Choice:** SQLite is simple but limited. DuckDB has better SQL feature support.
