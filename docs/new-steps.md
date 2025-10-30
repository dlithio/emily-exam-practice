# Next Development Steps - Multi-Difficulty Implementation

## Overview
This document outlines the next phase of development, focusing on:
1. Adding dataset variety through topic templates
2. Verifying Claude-generated solutions
3. Adding "derived column" as a new easy skill
4. Implementing true difficulty levels (Easy, Medium, Hard) with skill composition
5. Python-driven topic selection and skill combination logic

---

## Phase 8: Dataset Variety & Answer Verification

### Step 8.1: Create Dataset Topic Library
**Task:** Generate 100 diverse dataset topics for more varied problems
**Actions:**
- Create `dataset_topics.py` with a list of 100 domain-only topics
- Topics should be single-word or simple domain names (e.g., "library", "restaurant", "hospital", "e-commerce", "streaming")
- This allows Claude flexibility to generate either single or multiple tables based on the problem requirements
- Topics should cover diverse domains:
  - Business: sales, customers, products, orders, employees, departments, retail, wholesale, consulting
  - Education: school, university, courses, tutoring, training, academy
  - Technology: social-media, gaming, software, cloud, cybersecurity, analytics
  - Healthcare: hospital, clinic, pharmacy, lab, telemedicine
  - Entertainment: movies, music, streaming, theater, concerts, festivals
  - Finance: banking, investments, insurance, budgeting, trading, loans
  - Sports: basketball, soccer, tennis, olympics, fitness, marathon
  - E-commerce: marketplace, shopping, auctions, subscriptions
  - Transportation: flights, trains, rideshare, logistics, delivery
  - Food & Beverage: restaurant, cafe, catering, food-truck, bakery
  - Real Estate: properties, rentals, mortgages, listings
  - Travel: hotels, tours, bookings, cruises, travel-agency
  - Manufacturing: factory, supply-chain, inventory, production
  - Media: news, publishing, podcasts, journalism, advertising
- Keep topics generic enough for any skill type and complexity level

**Verification:**
- List should have exactly 100 topics
- Topics should be diverse across domains
- Each topic should be a simple domain name (1-2 words max)
- Claude will have flexibility to create appropriate table structures based on problem needs

---

### Step 8.2: Integrate Random Topic Selection
**Task:** Use random topic selection in problem generation
**Actions:**
- Modify `claude_client.py`:
  - Import `random` and `dataset_topics`
  - Add `select_random_topic()` function that returns a random topic from the list
  - Update `build_problem_generation_prompt()` to:
    - Accept new parameter: `dataset_topic`
    - Include the dataset topic in the prompt
    - Instruct Claude to create tables/questions based on this specific topic
- Update `generate_problem()` to:
  - Call `select_random_topic()` at start
  - Pass selected topic to prompt builder
  - Log which topic was used (for debugging)

**Verification:**
- Generate 10 problems in a row → should see different dataset topics
- Problems should align with the selected topic (e.g., if topic is "movies and ratings", tables should be about movies)
- Variety should be noticeably improved

---

### Step 8.3: Add Solution Verification to Problem Structure
**Task:** Extend Problem class to include Claude's reference solutions
**Actions:**
- Update `models.py` `Problem` class:
  - Add `pandas_solution: Optional[str]` - Claude's pandas code
  - Add `sql_solution: Optional[str]` - Claude's SQL query
  - Update `__repr__()` to show solutions if present
- Modify `build_problem_generation_prompt()` in `claude_client.py`:
  - Add instruction for Claude to provide both solutions
  - Request solutions in the JSON response format:
    ```json
    {
      "input_tables": {...},
      "question": "...",
      "expected_output": {...},
      "topic": "...",
      "difficulty": "...",
      "pandas_solution": "result = ...",
      "sql_solution": "SELECT ..."
    }
    ```
  - Specify solution requirements:
    - Pandas solution should assign to `result` variable
    - SQL solution should be a complete SELECT query
    - Both should work with the provided input tables
    - Both should produce the exact expected_output

**Verification:**
- Generate a problem and inspect the Problem object
- Verify `pandas_solution` and `sql_solution` fields are populated
- Manually test both solutions to ensure they work

---

### Step 8.4: Implement Solution Verification
**Task:** Run Claude's solutions and verify they match expected output
**Actions:**
- Create `verify_problem_solutions(problem)` function in `app.py`:
  - Run `execute_pandas(problem.pandas_solution, problem.input_tables)`
  - Run `execute_sql(problem.sql_solution, problem.input_tables)`
  - Compare both results to `problem.expected_output` using `compare_dataframes()`
  - Return dict with verification results:
    ```python
    {
      'pandas_valid': bool,
      'sql_valid': bool,
      'pandas_error': str or None,
      'sql_error': str or None,
      'pandas_feedback': str or None,
      'sql_feedback': str or None
    }
    ```
- Call verification when problem is generated:
  - In `app.py` after `generate_problem()` succeeds
  - If either solution fails verification:
    - Log warning with details
    - Optionally: regenerate problem (with retry limit)
    - For MVP: just log and continue (accept imperfect problems)

**Verification:**
- Generate several problems and check verification logs
- Ideally all solutions should verify correctly
- If failures occur, examine the specific problems to understand why

---

### Step 8.5: Add "Show Reference Solutions" Button
**Task:** Allow users to view Claude's reference solutions
**Actions:**
- Add button next to "Reveal Problem Info" button: "Show Reference Solutions"
- Store button state in session state: `solutions_revealed`
- When clicked and `solutions_revealed == True`:
  - Display pandas solution in expandable section with syntax highlighting
  - Display SQL solution in expandable section with syntax highlighting
  - Show verification status (whether these solutions were verified)
- Reset `solutions_revealed` to `False` when new problem is generated

**Verification:**
- Click "Show Reference Solutions" → should see both pandas and SQL solutions
- Solutions should be clearly formatted and readable
- Generate new problem → button state should reset

---

### Step 8.6: Add Export/Import Problem Functionality
**Task:** Allow users to save and share problems as JSON files
**Actions:**
- Add "Export Problem" button next to "Generate New Problem" in sidebar
- When clicked:
  - Serialize current problem to JSON format
  - Include all fields: input_tables (convert DataFrames to JSON), question, expected_output, topic, difficulty, pandas_solution, sql_solution
  - Use Streamlit's download_button to offer JSON file download
  - Filename format: `problem_{topic}_{timestamp}.json`
- Add "Import Problem" file uploader in sidebar
- When file is uploaded:
  - Parse JSON file
  - Validate structure (check for required fields)
  - Convert JSON table data back to DataFrames
  - Create Problem object and load it as current_problem
  - Show success message with problem topic and difficulty
  - Handle errors gracefully (invalid JSON, missing fields, etc.)
- Add helper functions to `models.py`:
  - `Problem.to_json()` - Serialize Problem to JSON-compatible dict
  - `Problem.from_json(json_dict)` - Create Problem from JSON dict
  - Handle DataFrame serialization using `.to_dict(orient='records')` or similar

**Verification:**
- Export a problem → should download JSON file
- Import the same problem → should load correctly and be solvable
- Import/export should preserve all problem data (tables, solutions, metadata)
- Invalid JSON files should show helpful error messages
- Use case: User can save interesting problems to share with friends or revisit later

---

## Phase 9: Add Derived Column Skill (Easy)

### Step 9.1: Define Derived Column Topic
**Task:** Add "derived_column" as a new easy skill
**Actions:**
- Add `"derived_column"` to the topic list in `app.py` sidebar
- Create topic description mapping in `claude_client.py`:
  ```python
  TOPIC_DESCRIPTIONS = {
      # ... existing topics ...
      "derived_column": {
          "name": "Creating New Columns",
          "description": "Create a new column based on existing column values",
          "subtypes": [
              "Arithmetic: Create column using math operations (e.g., total = price * quantity)",
              "Conditional: Create boolean flag or category (e.g., is_passing = score >= 60)",
              "Date: Extract component from date (e.g., year from timestamp)"
          ]
      }
  }
  ```
- Update prompt to handle derived_column topic with clear instructions for each subtype

**Verification:**
- Topic appears in sidebar checkbox list
- Selecting only "derived_column" should work without errors

---

### Step 9.2: Update Prompt for Derived Column Problems
**Task:** Generate high-quality derived column problems
**Actions:**
- Modify `build_problem_generation_prompt()` to handle `topic == "derived_column"`:
  - Randomly select one of three subtypes:
    1. **Arithmetic**: "Create a new column that is calculated from one or more existing numeric columns using basic math (+, -, *, /)"
    2. **Conditional**: "Create a new boolean or categorical column based on a condition (e.g., true/false, category assignment)"
    3. **Date**: "Create a new column that extracts a component from a date/timestamp column (year, month, day, day of week)"
  - Provide examples for each:
    - Arithmetic: `discount_amount = price * 0.1`, `total_score = math_score + english_score`
    - Conditional: `is_premium = tier in ['Gold', 'Platinum']`, `status = 'pass' if score >= 60 else 'fail'`
    - Date: `year = date.dt.year` (pandas) or `strftime('%Y', date)` (SQL)
  - Specify that the question should ask for filtering/selecting the new derived column
  - Expected output should show the new column

**Verification:**
- Generate 10+ derived_column problems
- Should see variety across all three subtypes
- Problems should be solvable in both pandas and SQL
- Example solutions:
  ```python
  # Pandas arithmetic
  result = employees.copy()
  result['bonus'] = result['salary'] * 0.1
  result = result[['name', 'bonus']]

  # SQL arithmetic
  SELECT name, salary * 0.1 as bonus FROM employees
  ```

---

### Step 9.3: Test Derived Column Problems
**Task:** Verify derived column problems work end-to-end
**Actions:**
- Create `test_derived_column.py`:
  - Test arithmetic derivation (both pandas and SQL)
  - Test conditional derivation (both pandas and SQL)
  - Test date derivation (both pandas and SQL)
  - Verify comparison works correctly
- Manually solve 5+ generated derived column problems in the UI
- Check that both pandas and SQL approaches work

**Verification:**
- All test cases pass
- Can successfully solve derived column problems using both languages
- Feedback is clear and accurate

---

## Phase 10: Medium Difficulty Implementation

### Step 10.1: Define Skill Composition Logic
**Task:** Create system for combining multiple easy skills
**Actions:**
- Create `difficulty_manager.py` with:
  - `EASY_SKILLS` = list of all easy topics (current 7 + derived_column = 8 total)
  - `select_skills_for_difficulty(difficulty, selected_topics)` function:
    ```python
    def select_skills_for_difficulty(difficulty, selected_topics):
        """
        Selects skills to combine based on difficulty level.

        Args:
            difficulty: "easy", "medium", or "hard"
            selected_topics: List of topics user selected (empty = all)

        Returns:
            List of skill names to combine
        """
        available_skills = selected_topics if selected_topics else EASY_SKILLS

        if difficulty == "easy":
            return [random.choice(available_skills)]
        elif difficulty == "medium":
            # Select 2-3 skills
            num_skills = random.choice([2, 3])
            return random.sample(available_skills, min(num_skills, len(available_skills)))
        elif difficulty == "hard":
            # Select 3-4 skills
            num_skills = random.choice([3, 4])
            return random.sample(available_skills, min(num_skills, len(available_skills)))
    ```
  - `should_use_cte(difficulty, skills)` function:
    - Returns `False` for easy
    - Returns `True` 50% of the time for medium
    - Returns `True` 100% of the time for hard (and specifies 1-3 CTEs)

**Verification:**
- Test function with different difficulty levels
- Verify correct number of skills returned
- Verify randomization works

---

### Step 10.2: Update Problem Generation for Multi-Skill
**Task:** Modify Claude prompt to handle skill combinations
**Actions:**
- Update `generate_problem()` to:
  - Accept `difficulty` parameter (default "easy")
  - When difficulty is "medium" or "hard":
    - Call `select_skills_for_difficulty(difficulty, selected_topics)`
    - Call `should_use_cte(difficulty, skills)`
    - Pass skills list and CTE requirement to prompt builder
- Update `build_problem_generation_prompt()`:
  - When multiple skills provided:
    - List all skills that must be tested
    - Provide guidance on combining them naturally
    - Special cases:
      - `derived_column + filter_rows`: Filter should often use the derived column
      - `derived_column + aggregations`: Aggregation should often use the derived column
      - `joins + filter_rows`: Filter can be before or after join
      - `joins + aggregations`: Group by the joined data
  - When `use_cte == True`:
    - Require the SQL solution to use at least one CTE
    - For hard problems, encourage 2-3 CTEs when appropriate
    - Explain CTEs break complex queries into steps
  - Specify the problem should require all listed skills to solve efficiently

**Verification:**
- Generate medium problems with 2-3 skills
- Verify question naturally requires multiple operations
- Verify SQL solution uses CTEs when required
- Test that pandas and SQL solutions still match expected output

---

### Step 10.3: Update UI for Difficulty Selection
**Task:** Add difficulty selector to UI
**Actions:**
- In `app.py` sidebar, add radio buttons for difficulty:
  - "Easy" (default)
  - "Medium"
  - "Hard"
- Store selection in session state: `difficulty`
- When "Generate New Problem" is clicked:
  - Pass `difficulty` parameter to `generate_problem()`
- Update problem display to show:
  - Difficulty level (only if "Reveal Problem Info" clicked)
  - Skills being tested (only if "Reveal Problem Info" clicked)
- Loading message should be generic and not reveal difficulty or topics:
  - Use simple message: "Generating practice problem..." with spinner
  - Do NOT reveal difficulty level, topics, or skills in loading message
  - All problem details remain hidden until "Reveal Problem Info" is clicked

**Verification:**
- Select "Medium" difficulty → generate problem → should be noticeably more complex
- Select "Hard" difficulty → generate problem → should be significantly more complex
- Difficulty and skills should display when revealed
- Loading messages should not reveal any problem information

---

### Step 10.4: Test Medium Difficulty Problems
**Task:** Verify medium problems work correctly
**Actions:**
- Generate 20+ medium problems
- Manually solve 10 of them in both pandas and SQL
- Verify:
  - Problems genuinely require 2-3 operations
  - Both solutions work and match expected output
  - CTEs are used appropriately in SQL (when required)
  - Problems are challenging but solvable
- Create `test_medium_problems.py`:
  - Test various skill combinations
  - Verify CTE generation works
  - Verify all skills are actually needed

**Verification:**
- Medium problems feel appropriately challenging
- Success rate on manual testing: aim for 80%+ solvable
- No common failure patterns

---

## Phase 11: Hard Difficulty & Advanced Topics

### Step 11.1: Add Advanced Topics for Hard Problems
**Task:** Enable advanced topics from STUDY_GUIDE for hard difficulty
**Actions:**
- Define `ADVANCED_TOPICS` in `difficulty_manager.py`:
  - `"datatypes"` - Converting and casting datatypes
  - `"cross_join"` - Cross join operations (can be combined with other skills)
  - `"pivot"` - Wide to long format (pandas only)
  - `"melt"` - Long to wide format (pandas only)
  - (Skip "create_dataframe" for now as noted in TODO)
- Update `select_skills_for_difficulty()`:
  - For hard problems:
    - 20% chance: Use `pivot` or `melt` as standalone (pandas-only problems)
    - 20% chance: Use `datatypes` as standalone advanced topic
    - 30% chance: Include `cross_join` as one of 2-3 skills (combinable with easy skills)
    - 30% chance: Use 3-4 easy skills combined (no advanced topics)
  - Special handling:
    - `pivot` and `melt`: Always standalone, pandas-only
    - `datatypes`: Can be standalone or combined (both work well)
    - `cross_join`: Should typically be combined with other operations (filter, aggregate, etc.) for realistic problems
- Create topic descriptions for advanced topics:
  ```python
  ADVANCED_TOPIC_DESCRIPTIONS = {
      "datatypes": {
          "name": "Datatype Conversion",
          "description": "Convert column datatypes (e.g., string to number, number to string)",
          "can_combine": True
      },
      "cross_join": {
          "name": "Cross Join",
          "description": "Combine every row from one table with every row from another",
          "can_combine": True  # Should usually be combined with other operations
      },
      "pivot": {
          "name": "Pivot (Wide to Long)",
          "description": "Transform data from wide format to long format (pandas only)",
          "can_combine": False,
          "pandas_only": True
      },
      "melt": {
          "name": "Melt (Long to Wide)",
          "description": "Transform data from long format to wide format (pandas only)",
          "can_combine": False,
          "pandas_only": True
      }
  }
  ```

**Verification:**
- Generate 30 hard problems
- Should see mix of:
  - Multi-skill problems with cross_join + other operations (e.g., cross_join + filter + aggregate)
  - Multi-skill problems (3-4 easy skills only)
  - Standalone datatypes problems
  - Standalone pivot/melt problems (pandas-only)
- Cross join problems should feel realistic (not just cartesian product for its own sake)

---

### Step 11.2: Implement CTE Requirements for Hard Problems
**Task:** Ensure hard problems require multiple CTEs
**Actions:**
- Update `should_use_cte()` in `difficulty_manager.py`:
  ```python
  def should_use_cte(difficulty, skills):
      """Returns (use_cte: bool, num_ctes: int)"""
      if difficulty == "easy":
          return False, 0
      elif difficulty == "medium":
          # 50% chance of 1 CTE
          use_cte = random.random() < 0.5
          return use_cte, 1 if use_cte else 0
      elif difficulty == "hard":
          # Always use CTEs, 1-3 of them
          # More skills = more likely to need more CTEs
          if len(skills) >= 4:
              num_ctes = random.choice([2, 3])  # 4 skills: 2-3 CTEs
          elif len(skills) >= 3:
              num_ctes = random.choice([1, 2, 3])  # 3 skills: 1-3 CTEs
          else:
              num_ctes = random.choice([1, 2])  # 2 skills or advanced: 1-2 CTEs
          return True, num_ctes
  ```
- Update prompt builder to specify number of CTEs when `num_ctes > 1`:
  - "Your SQL solution should use at least {num_ctes} CTEs to break the problem into logical steps"
  - Provide example of multi-CTE structure

**Verification:**
- Generate 10 hard problems
- Check SQL solutions all use CTEs
- Should see variety in number of CTEs (1-3)

---

### Step 11.3: Handle Pandas-Only Problems (Pivot/Melt)
**Task:** Support problems that only work in pandas
**Actions:**
- Update `Problem` class in `models.py`:
  - Add `pandas_only: bool` field (default False)
  - When `True`, SQL solution will be None
- Update UI in `app.py`:
  - When `current_problem.pandas_only == True`:
    - Disable "SQL" language option
    - Show message: "This problem tests pandas-specific functionality (pivot/melt)"
    - Only allow pandas code execution
- Update prompt for pivot/melt topics:
  - Specify this is pandas-only
  - No need to generate SQL solution
  - Focus on clear pivot/melt examples

**Verification:**
- Generate pivot problem → SQL option should be disabled
- Generate melt problem → SQL option should be disabled
- Other problems → both options available

---

### Step 11.4: Test Hard Difficulty Problems
**Task:** Verify hard problems are appropriately challenging
**Actions:**
- Generate 30+ hard problems
- Categorize by type:
  - Multi-skill (3-4 easy skills): ~15 problems
  - Multi-skill with cross_join: ~5 problems
  - Advanced topics (datatypes): ~5 problems
  - Pivot/melt: ~5 problems
- Manually solve 15 of them
- Verify:
  - Problems are genuinely difficult but solvable with thought and effort
  - CTEs are helpful/necessary in SQL solutions
  - Advanced topics are tested correctly
  - Expected outputs match user solutions
  - All solutions (pandas and SQL) are correct and verified
- Create `test_hard_problems.py`:
  - Test multi-skill generation
  - Test CTE generation
  - Test advanced topics
  - Test pandas-only handling

**Verification:**
- Hard problems feel significantly more challenging than medium
- Problems should require careful thinking and multiple steps
- All generated problems should be solvable (solutions should verify correctly)
- CTE structure makes SQL solutions cleaner
- Advanced topics are correctly implemented

---

## Phase 12: Polish & Integration

### Step 12.1: Add Statistics Tracking
**Task:** Track problem attempts and success rate by difficulty
**Actions:**
- Add session state variables:
  - `attempts_by_difficulty` = {"easy": 0, "medium": 0, "hard": 0}
  - `correct_by_difficulty` = {"easy": 0, "medium": 0, "hard": 0}
- Update counts when user submits code:
  - Increment `attempts_by_difficulty[current_difficulty]`
  - If correct, increment `correct_by_difficulty[current_difficulty]`
- Display stats in sidebar:
  ```
  Session Stats:
  Easy: 8/10 (80%)
  Medium: 3/5 (60%)
  Hard: 1/3 (33%)
  ```

**Verification:**
- Solve several problems at each difficulty
- Stats should update correctly
- Percentages should calculate correctly

---

### Step 12.2: Update Loading Messages
**Task:** Make loading states informative without revealing problem details
**Actions:**
- When generating problem, show generic loading messages with progress spinner
- Loading messages should NEVER reveal:
  - Dataset topic/domain
  - Skills being tested
  - Problem difficulty
- All of this information should remain hidden until user clicks "Reveal Problem Info"
- Examples:
  - Easy: "Generating new practice problem..."
  - Medium: "Generating new practice problem..."
  - Hard: "Generating new practice problem..."
  - Or use a single message: "Generating practice problem..." with a spinner
- Optional: Add variety to loading messages without revealing content:
  - "Creating your next challenge..."
  - "Preparing a new problem..."
  - "Generating practice problem..."

**Verification:**
- Loading messages should not reveal any hints about the problem
- All problem details (topic, difficulty, skills) remain hidden until "Reveal Problem Info" is clicked
- Consistent with existing design principle from summary.md: "Loading messages also never reveal the topic to avoid giving hints"

---

### Step 12.3: Comprehensive Testing
**Task:** Test full system with all features
**Actions:**
- Run all existing tests to ensure nothing broke
- Create comprehensive test suite:
  - `test_full_workflow.py` - Complete end-to-end test
  - Test all difficulty levels
  - Test all easy skills
  - Test all advanced topics
  - Test topic selection
  - Test solution verification
- Manual testing checklist:
  - [ ] Easy problems work for all 8 topics
  - [ ] Medium problems combine 2-3 skills naturally
  - [ ] Hard problems are appropriately challenging
  - [ ] Advanced topics work correctly
  - [ ] Pivot/melt disable SQL correctly
  - [ ] CTEs are used in medium/hard SQL solutions
  - [ ] Reference solutions button works
  - [ ] Solution verification works
  - [ ] Dataset variety is noticeable (100 diverse domains)
  - [ ] Statistics tracking works
  - [ ] Export problem to JSON works
  - [ ] Import problem from JSON works and preserves all data
  - [ ] Loading messages never reveal topic or difficulty
  - [ ] Problem info (topic, difficulty, skills) only shows after clicking "Reveal Problem Info"
  - [ ] UI is intuitive and responsive

**Verification:**
- All tests pass
- Manual checklist completed
- No obvious bugs or UX issues

---

## Implementation Order Recommendation

Given the dependencies and complexity, here's the recommended implementation order:

1. **Start with Phase 8 (Dataset Variety & Verification)**
   - Step 8.1, 8.2: Add variety quickly (high value, low risk)
   - Step 8.3, 8.4: Solution verification (important for quality)
   - Step 8.5: Reference solutions button (nice UX improvement)
   - Step 8.6: Export/Import functionality (enables problem sharing/saving)

2. **Then Phase 9 (Derived Column)**
   - Step 9.1, 9.2, 9.3: Add new easy skill (relatively simple)
   - This gives you 8 easy skills before tackling difficulty levels

3. **Then Phase 10 (Medium Difficulty)**
   - Steps 10.1, 10.2, 10.3, 10.4: Medium is simpler than hard
   - Test thoroughly before moving to hard

4. **Then Phase 11 (Hard Difficulty)**
   - Steps 11.1, 11.2, 11.3, 11.4: Build on medium difficulty
   - Advanced topics are the most complex

5. **Finally Phase 12 (Polish)**
   - Steps 12.1, 12.2, 12.3: Polish everything once core features work

---

## Key Technical Decisions

### Skill Selection Logic (Python vs Claude)
- **Python decides**: Which skills to combine, how many, whether to use CTEs
- **Claude executes**: Creates concrete problem based on the requirements
- **Why**: More consistent difficulty, better control, cheaper API calls

### CTE Usage Strategy
- Easy: Never
- Medium: Optional (50% chance)
- Hard: Always (1-3 CTEs depending on complexity)
- **Why**: CTEs are a key skill for complex SQL, should be required for hard problems

### Advanced Topics Approach
- Hard only, 30% chance as solo topic
- Pivot/melt are pandas-only (disable SQL option)
- **Why**: Advanced topics are genuinely hard, deserve focused practice

### Dataset Topic Selection
- Random selection from 100 topics for every problem
- Topics are domain suggestions, not rigid schemas
- **Why**: Maximum variety without overwhelming Claude's prompt

---

## Testing Strategy

For each phase:
1. **Unit tests**: Test individual functions in isolation
2. **Integration tests**: Test features work together
3. **Manual testing**: Solve 5-10 generated problems yourself
4. **Edge cases**: Test with empty selections, all selections, etc.

---

## Future Enhancements (Post-Implementation)

- **Adaptive difficulty**: Adjust difficulty based on user success rate
- **Problem bank**: Cache generated problems for faster loading
- **Hints system**: Progressive hints for struggling users
- **Explanation mode**: Have Claude explain the solution approach
- **Custom topics**: Let users add their own dataset topics
- **Download solutions**: Export reference solutions for offline study

---

## Notes

- The complexity jump from easy → medium → hard should be noticeable
- Medium problems should feel like "2 easy problems combined"
- Hard problems should feel like "multiple steps, need to think carefully"
- All generated problems should be solvable (solutions should verify correctly)
- Solution verification is critical for quality control
- Dataset variety will make practice feel less repetitive
- **Loading messages must NEVER reveal problem information** - all details (topic, difficulty, skills) should only be visible after clicking "Reveal Problem Info"
- Domain-only dataset topics (e.g., "library", "hospital") give Claude flexibility to create appropriate table structures
- Export/import enables users to save and share interesting problems with others
