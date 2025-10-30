"""
Claude API client for generating practice problems.
"""
import os
import json
import random
from typing import Optional, List
from functools import lru_cache
from anthropic import Anthropic
import pandas as pd
from models import Problem
from dataset_topics import get_random_topic
from difficulty_manager import select_skills_for_difficulty, should_use_cte

# Default model for problem generation
# Update this to the latest available model from https://docs.anthropic.com/en/docs/models-overview
DEFAULT_MODEL = "claude-sonnet-4-5-20250929"


def get_api_key():
    """
    Get Claude API key from environment variable or Streamlit secrets.

    Returns:
        str: API key

    Raises:
        ValueError: If API key is not found
    """
    # First try environment variable
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if api_key:
        return api_key

    # Try Streamlit secrets if available
    try:
        import streamlit as st
        if "ANTHROPIC_API_KEY" in st.secrets:
            return st.secrets["ANTHROPIC_API_KEY"]
    except (ImportError, FileNotFoundError, KeyError):
        pass

    raise ValueError(
        "ANTHROPIC_API_KEY not found. Please set it as an environment variable "
        "or add it to .streamlit/secrets.toml"
    )


def get_client():
    """
    Get initialized Anthropic client.

    Returns:
        Anthropic: Initialized client
    """
    api_key = get_api_key()
    return Anthropic(api_key=api_key)


def test_api_connection():
    """
    Test basic API call to verify connection works.

    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        client = get_client()
        response = client.messages.create(
            model=DEFAULT_MODEL,
            max_tokens=100,
            messages=[
                {"role": "user", "content": "Say 'API connection successful' and nothing else."}
            ]
        )

        result = response.content[0].text
        print(f"API Response: {result}")
        return True

    except Exception as e:
        print(f"API connection failed: {e}")
        return False


def strip_markdown_code_blocks(text: str) -> str:
    """
    Remove markdown code block formatting from text if present.

    Args:
        text: Text that may contain ```json ... ``` formatting

    Returns:
        str: Text with markdown code blocks removed
    """
    text = text.strip()

    # Remove ```json at start and ``` at end
    if text.startswith("```json"):
        text = text[7:]  # Remove ```json
    elif text.startswith("```"):
        text = text[3:]  # Remove ```

    if text.endswith("```"):
        text = text[:-3]  # Remove ```

    return text.strip()


def select_random_topic() -> str:
    """
    Select a random dataset topic for problem generation.

    Returns:
        str: A random dataset topic from the library
    """
    return get_random_topic()


def build_problem_generation_prompt(
    skills: List[str],
    difficulty: str = "easy",
    dataset_topic: Optional[str] = None,
    use_cte: bool = False,
    num_ctes: int = 0
) -> str:
    """
    Build a prompt that instructs Claude to generate a practice problem.

    Args:
        skills: List of skills to focus on (e.g., ["filter_rows", "aggregations"])
        difficulty: Problem difficulty ("easy", "medium", "hard")
        dataset_topic: Optional dataset domain to use (e.g., "library", "hospital", "movies")
        use_cte: Whether to require CTEs in SQL solution
        num_ctes: Number of CTEs to require (if use_cte is True)

    Returns:
        str: Formatted prompt for Claude
    """

    # Map topics to more descriptive names for the prompt
    topic_descriptions = {
        "filter_columns": "selecting/choosing specific columns from a table",
        "filter_rows": "finding rows that meet certain conditions or criteria",
        "aggregations": "calculating summary statistics (totals, averages, counts) for groups of data",
        "distinct": "finding unique/non-repeating values",
        "joins": "combining information from two related tables",
        "order_by": "arranging data in a specific order (ascending or descending)",
        "limit": "showing only the first few rows of results",
        "derived_column": "creating a new column based on existing column values",
        "datatypes": "converting and casting column datatypes (e.g., string to number, number to string)",
        "cross_join": "creating every possible combination of rows from two tables (cartesian product)",
        "pivot": "transforming data from wide format to long format (pandas-specific reshaping)",
        "melt": "transforming data from long format to wide format (pandas-specific reshaping)",
    }

    # Check if this is a pandas-only problem (pivot or melt)
    is_pandas_only = any(skill in ["pivot", "melt"] for skill in skills)

    # Build skill descriptions
    if len(skills) == 1:
        topic_desc = topic_descriptions.get(skills[0], skills[0])
        skills_focus = f"TOPIC FOCUS: {skills[0]}\n{topic_desc}"
    else:
        # Multiple skills
        skill_list = "\n".join([f"  - {skill}: {topic_descriptions.get(skill, skill)}" for skill in skills])
        skills_focus = f"SKILLS TO COMBINE: {len(skills)} skills\n{skill_list}"
        topic_desc = f"combining multiple operations: {', '.join(skills)}"

    # Difficulty guidelines
    difficulty_guidelines = {
        "easy": "SINGLE OPERATION ONLY. Test exactly ONE concept on small data (3-5 rows). No combining multiple operations. Use clear, straightforward conditions.",
        "medium": "Use 2-3 combined operations on medium-sized data (5-10 rows). Include slightly more complex logic.",
        "hard": "Create a multi-step problem with larger data (10-15 rows), edge cases, and complex conditions."
    }

    difficulty_guide = difficulty_guidelines.get(difficulty, difficulty_guidelines["easy"])

    # Add dataset topic instruction if provided
    dataset_instruction = ""
    if dataset_topic:
        dataset_instruction = f"""
DATASET DOMAIN: {dataset_topic}
Create your problem using the "{dataset_topic}" domain. Generate appropriate table names,
column names, and data that fit naturally with this domain. For example:
- If the domain is "library", you might create tables like "books", "members", "checkouts"
- If the domain is "hospital", you might create tables like "patients", "doctors", "appointments"
- If the domain is "movies", you might create tables like "films", "directors", "ratings"

Use your creativity to design tables that make sense for this domain and the skill being tested.
"""

    # Add special instructions for derived_column topic
    derived_column_instruction = ""
    if "derived_column" in skills:
        # Select subtypes based on difficulty
        # Easy problems: only Arithmetic or Conditional (no dates - they require pd.to_datetime conversion)
        # Medium/Hard problems: can include Date subtype
        if difficulty == "easy":
            subtypes = [
                ("Arithmetic", "Create a new column calculated from one or more existing numeric columns using basic math operations (+, -, *, /). Examples: total = price * quantity, discount_amount = price * 0.1, total_score = math_score + english_score"),
                ("Conditional", "Create a new boolean or categorical column based on a condition. Examples: is_premium = (tier == 'Gold' or tier == 'Platinum'), status = 'pass' if score >= 60 else 'fail', category = 'high' if value > 100 else 'low'")
            ]
        else:
            # Medium/Hard: include Date subtype as well
            subtypes = [
                ("Arithmetic", "Create a new column calculated from one or more existing numeric columns using basic math operations (+, -, *, /). Examples: total = price * quantity, discount_amount = price * 0.1, total_score = math_score + english_score"),
                ("Conditional", "Create a new boolean or categorical column based on a condition. Examples: is_premium = (tier == 'Gold' or tier == 'Platinum'), status = 'pass' if score >= 60 else 'fail', category = 'high' if value > 100 else 'low'"),
                ("Date", "Create a new column that extracts a component from a date/timestamp column (year, month, day, day of week). Examples: year = date.dt.year (pandas) or strftime('%Y', date) (SQL), month_name = date.dt.month_name()")
            ]
        subtype_name, subtype_desc = random.choice(subtypes)
        derived_column_instruction = f"""
DERIVED COLUMN SUBTYPE: {subtype_name}
{subtype_desc}

Your problem should ask the user to create this new derived column and show it in the output.
The expected output should include the new column.
Make sure the problem is solvable in both pandas and SQL.
"""

    # Add special instructions for pivot/melt topics (pandas-only)
    pandas_only_instruction = ""
    if is_pandas_only:
        pandas_only_instruction = f"""
PANDAS-ONLY PROBLEM:
This problem tests pandas-specific functionality (pivot or melt) that has no direct SQL equivalent.
- You only need to provide a pandas_solution
- Set sql_solution to null in your JSON response
- Focus on creating a clear, realistic example of data transformation
- For pivot: Transform wide data to long format (e.g., unpivot multiple columns into rows)
- For melt: Transform long data to wide format (e.g., create columns from row values)

Examples:
- Pivot: Convert monthly sales columns (Jan, Feb, Mar) into rows with (Month, Sales) pairs
- Melt: Convert transaction rows (Customer, Product, Amount) into columns (Customer, Product1_Amount, Product2_Amount)
"""

    # Add multi-skill combination guidance
    multi_skill_instruction = ""
    if len(skills) > 1:
        multi_skill_instruction = f"""
MULTI-SKILL REQUIREMENT:
Your problem must naturally require ALL {len(skills)} of these skills to solve efficiently:
{skill_list}

Design the problem so that all skills are needed in a logical, realistic way. Some natural combinations:
- derived_column + filter_rows: Filter based on the derived column's value
- derived_column + aggregations: Aggregate using the derived column
- joins + filter_rows: Filter the data before OR after joining (or both)
- joins + aggregations: Calculate aggregates on the joined data
- filter_rows + aggregations: Filter first, then aggregate the filtered results
- aggregations + order_by: Sort the aggregated results
- Any skill + limit: Show only top N results after other operations

The user should need to apply all {len(skills)} skills to arrive at the correct answer.
"""

    # Add CTE requirement for SQL solutions
    cte_instruction = ""
    if use_cte and num_ctes > 0:
        cte_instruction = f"""
SQL CTE REQUIREMENT:
Your SQL solution MUST use Common Table Expressions (CTEs) to break the problem into logical steps.
- Require at least {num_ctes} CTE{"s" if num_ctes > 1 else ""} in the SQL solution
- Each CTE should represent a meaningful intermediate step
- CTEs help organize complex queries into readable, maintainable parts
- Use WITH clause syntax: WITH cte_name AS (SELECT ...), another_cte AS (SELECT ...) SELECT * FROM ...

Example structure for {num_ctes} CTE{"s" if num_ctes > 1 else ""}:
"""
        if num_ctes == 1:
            cte_instruction += """
WITH filtered_data AS (
    SELECT ... FROM table WHERE ...
)
SELECT ... FROM filtered_data
"""
        elif num_ctes == 2:
            cte_instruction += """
WITH filtered_data AS (
    SELECT ... FROM table WHERE ...
),
aggregated_data AS (
    SELECT ... FROM filtered_data GROUP BY ...
)
SELECT ... FROM aggregated_data
"""
        else:  # 3+ CTEs
            cte_instruction += """
WITH step1 AS (
    SELECT ... FROM table WHERE ...
),
step2 AS (
    SELECT ... FROM step1 JOIN another_table ...
),
step3 AS (
    SELECT ... FROM step2 GROUP BY ...
)
SELECT ... FROM step3 ORDER BY ...
"""

    # Adjust requirements based on whether it's pandas-only
    if is_pandas_only:
        compatibility_requirement = "4. This is a PANDAS-ONLY problem (no SQL solution required)"
    else:
        compatibility_requirement = "4. Ensure the problem can be solved in BOTH pandas AND SQL"

    prompt = f"""Generate a pandas/SQL practice problem focused on {topic_desc}.
{dataset_instruction}{derived_column_instruction}{pandas_only_instruction}{multi_skill_instruction}{cte_instruction}
REQUIREMENTS:
1. Create 1-2 small DataFrames as input tables with realistic column names and data
2. Write a clear word problem describing what the user should do
3. Provide the expected output DataFrame showing the correct answer
{compatibility_requirement}
5. Difficulty: {difficulty} - {difficulty_guide}

{skills_focus}

CRITICAL REQUIREMENT - PLAIN ENGLISH ONLY:
- Write the question in PLAIN ENGLISH that anyone could understand
- DO NOT use SQL terminology (no "JOIN", "GROUP BY", "SELECT", "WHERE", "ORDER BY", "LIMIT", "DISTINCT", etc.)
- DO NOT use pandas terminology (no "merge", "groupby", "filter", "sort_values", etc.)
- DO NOT mention programming concepts or function names
- Use everyday language like: "show", "find", "list", "combine", "calculate", "arrange", "get", "display"
- Describe WHAT the user should accomplish, not HOW to do it technically

BAD EXAMPLES (too technical):
- "Join the customers and orders tables using an inner join"
- "Group by product and calculate total revenue"
- "Use WHERE to filter rows where salary > 70000"

GOOD EXAMPLES (plain English):
- "Show all orders along with the customer's name and city for each order"
- "For each product, calculate the total revenue"
- "Find all employees earning more than $70,000"

ADDITIONAL REQUIREMENT FOR EASY DIFFICULTY:
If difficulty is "easy", the problem should test EXACTLY ONE concept:
- For filter_rows: Just filtering, nothing else (no sorting, no aggregations)
- For aggregations: Just one aggregation operation (e.g., just sum OR just count, not both)
- For joins: Just combining tables, no additional filtering or calculations
- For order_by: Just sorting, no calculations
DO NOT combine multiple concepts in easy problems. For example, DON'T ask users to:
- Calculate a new column AND group AND sort (that's 3 operations)
- Filter AND join (that's 2 operations)
Easy = One operation only.

Return your response as a JSON object with this EXACT structure:
{{
  "input_tables": {{
    "table_name": {{
      "columns": ["col1", "col2", ...],
      "data": [
        [val1, val2, ...],
        [val1, val2, ...]
      ]
    }}
  }},
  "question": "Clear description of what to do...",
  "topic": "{skills[0] if len(skills) == 1 else 'multi_skill'}",
  "difficulty": "{difficulty}",
  "pandas_solution": "result = ...",
  "sql_solution": {"null" if is_pandas_only else '"SELECT ..."'}
}}

REFERENCE SOLUTIONS REQUIREMENT (CRITICAL):
{"For pandas-only problems (pivot/melt), you only need to provide a pandas solution:" if is_pandas_only else "You MUST provide both a pandas solution and a SQL solution that produce IDENTICAL results:"}
- pandas_solution: Complete pandas code that assigns the final result to a variable named 'result'.
  The input table names will be available as DataFrame variables.
  Example: "result = employees[employees['salary'] > 70000]"
{"- sql_solution: Set to null (this is a pandas-only problem)" if is_pandas_only else """- sql_solution: Complete SELECT query that works with standard SQL.
  The input tables will be available as SQL tables with the same names.
  Example: "SELECT * FROM employees WHERE salary > 70000"
- CRITICAL: Both solutions MUST produce EXACTLY THE SAME output DataFrame
- Both solutions must return the same columns in the same order
- Both solutions must return the same rows in the same order
- Test your solutions mentally to ensure they work correctly and produce identical results
- The pandas and SQL solutions will be executed and compared - they MUST match exactly"""}

IMPORTANT GUIDELINES:
- Keep data small and realistic (real-world scenarios like employees, sales, products)
- Column names should be lowercase and descriptive
- Use diverse data types (strings, integers, floats where appropriate)
- Make sure the expected output is actually correct!
- For pandas: user will have table names as DataFrame variables
- For SQL: user will query from table names using standard SQL
- Test your logic: ensure the problem is actually solvable

Example JSON format (for reference only - generate a NEW problem):
{{
  "input_tables": {{
    "employees": {{
      "columns": ["name", "department", "salary"],
      "data": [
        ["Alice", "Engineering", 95000],
        ["Bob", "Sales", 65000],
        ["Charlie", "Engineering", 88000]
      ]
    }}
  }},
  "question": "Show all employees who work in the Engineering department.",
  "topic": "filter_rows",
  "difficulty": "easy",
  "pandas_solution": "result = employees[employees['department'] == 'Engineering']",
  "sql_solution": "SELECT * FROM employees WHERE department = 'Engineering'"
}}

Generate a NEW problem now (not the example above).

CRITICAL: Return ONLY the raw JSON object. Do NOT wrap it in markdown code blocks or ```json tags. Do NOT include any explanatory text before or after the JSON. Start your response with {{ and end with }}."""

    return prompt


def _json_to_dataframe(json_table: dict) -> pd.DataFrame:
    """
    Convert JSON table representation to pandas DataFrame.

    Args:
        json_table: Dict with "columns" and "data" keys

    Returns:
        pd.DataFrame: Converted DataFrame
    """
    columns = json_table["columns"]
    data = json_table["data"]
    return pd.DataFrame(data, columns=columns)


@lru_cache(maxsize=32)
def _cached_generate_problem(
    skills_tuple: tuple,
    difficulty: str,
    dataset_topic: str,
    use_cte: bool,
    num_ctes: int,
    cache_key: int
) -> str:
    """
    Cached version of API call to avoid regenerating during development.

    Args:
        skills_tuple: Tuple of skills for the problem (tuple for hashability)
        difficulty: Difficulty level
        dataset_topic: Dataset domain for the problem
        use_cte: Whether to require CTEs in SQL solution
        num_ctes: Number of CTEs to require
        cache_key: Arbitrary key to control cache invalidation

    Returns:
        str: Raw JSON response from API
    """
    client = get_client()
    skills = list(skills_tuple)  # Convert back to list
    prompt = build_problem_generation_prompt(skills, difficulty, dataset_topic, use_cte, num_ctes)

    response = client.messages.create(
        model=DEFAULT_MODEL,
        max_tokens=2000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.content[0].text


def generate_problem(
    topic: Optional[str] = None,
    difficulty: str = "easy",
    selected_topics: Optional[List[str]] = None,
    use_cache: bool = True
) -> Problem:
    """
    Generate a practice problem using Claude API.

    Args:
        topic: (Deprecated) Single skill to focus on. Use selected_topics instead.
        difficulty: Problem difficulty ("easy", "medium", "hard")
        selected_topics: List of topics user selected (empty/None = all topics)
        use_cache: Whether to use cached responses (default True for development)

    Returns:
        Problem: Generated problem object with input tables, question, and expected output

    Raises:
        ValueError: If API response is invalid or unparseable
        Exception: If API call fails
    """
    try:
        # Select random dataset topic for variety
        dataset_topic = select_random_topic()
        print(f"[DEBUG] Using dataset topic: {dataset_topic}")

        # Determine which skills to use based on difficulty
        if topic:
            # Legacy single-topic mode (for backward compatibility)
            skills = [topic]
            use_cte = False
            num_ctes = 0
        else:
            # Multi-skill mode based on difficulty
            selected_topics_list = selected_topics if selected_topics else []
            skills = select_skills_for_difficulty(difficulty, selected_topics_list)
            use_cte, num_ctes = should_use_cte(difficulty, skills)

        print(f"[DEBUG] Skills selected: {skills}")
        print(f"[DEBUG] CTE requirement: use_cte={use_cte}, num_ctes={num_ctes}")

        # Call API (with or without cache)
        if use_cache:
            # Using hash of skills+difficulty+dataset_topic as cache key for reproducibility
            skills_str = "_".join(sorted(skills))  # Sort for consistent caching
            cache_key = hash(f"{skills_str}_{difficulty}_{dataset_topic}_{use_cte}_{num_ctes}") % 1000
            response_text = _cached_generate_problem(tuple(skills), difficulty, dataset_topic, use_cte, num_ctes, cache_key)
        else:
            try:
                client = get_client()
                prompt = build_problem_generation_prompt(skills, difficulty, dataset_topic, use_cte, num_ctes)
                response = client.messages.create(
                    model=DEFAULT_MODEL,
                    max_tokens=2000,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                response_text = response.content[0].text
            except Exception as api_error:
                # Provide more specific error message for API failures
                error_msg = str(api_error)
                if "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
                    raise Exception("API authentication failed. Please check your ANTHROPIC_API_KEY.")
                elif "timeout" in error_msg.lower():
                    raise Exception("API request timed out. Please check your internet connection and try again.")
                elif "rate_limit" in error_msg.lower():
                    raise Exception("API rate limit exceeded. Please wait a moment and try again.")
                elif "overloaded" in error_msg.lower():
                    raise Exception("API is temporarily overloaded. Please try again in a moment.")
                else:
                    raise Exception(f"API request failed: {error_msg}")

        # Parse JSON response
        cleaned_response = strip_markdown_code_blocks(response_text)

        try:
            problem_data = json.loads(cleaned_response)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"API returned invalid JSON format. This may be a temporary issue. "
                f"Error: {e}\n"
                f"Response preview: {response_text[:200]}..."
            )

        # Validate required fields (note: expected_output is now derived from solutions, not provided by Claude)
        required_fields = ["input_tables", "question", "topic", "difficulty", "pandas_solution", "sql_solution"]
        missing_fields = [field for field in required_fields if field not in problem_data]
        if missing_fields:
            raise ValueError(
                f"API response is missing required fields: {missing_fields}. "
                f"This may be a temporary issue with the AI model. Please try again."
            )

        # Convert JSON tables to DataFrames
        input_tables = {}
        for table_name, table_data in problem_data["input_tables"].items():
            try:
                input_tables[table_name] = _json_to_dataframe(table_data)
            except Exception as e:
                raise ValueError(f"Failed to convert input table '{table_name}' to DataFrame: {e}")

        # Validate that we have at least one input table
        if not input_tables:
            raise ValueError("API response contains no input tables. Please try again.")

        # Extract solution fields
        pandas_solution = problem_data.get("pandas_solution")
        sql_solution = problem_data.get("sql_solution")

        # Check if this is a pandas-only problem
        is_pandas_only = any(skill in ["pivot", "melt"] for skill in skills)

        # Validate solutions based on problem type
        if not pandas_solution:
            raise ValueError("API response is missing pandas_solution. Please try again.")

        if not is_pandas_only and not sql_solution:
            raise ValueError("API response is missing sql_solution. Please try again.")

        # Execute both solutions to derive expected_output and verify they match
        # Import here to avoid circular dependency
        from execution import execute_pandas, execute_sql, compare_dataframes

        # Execute pandas solution
        pandas_result, pandas_error = execute_pandas(pandas_solution, input_tables)
        if pandas_error:
            raise ValueError(
                f"Claude's pandas solution failed to execute. This is a problem generation error.\n"
                f"Pandas solution: {pandas_solution}\n"
                f"Error: {pandas_error}"
            )

        if pandas_result is None or pandas_result.empty:
            raise ValueError(
                f"Claude's pandas solution produced no output. This is a problem generation error.\n"
                f"Pandas solution: {pandas_solution}"
            )

        # For pandas-only problems, skip SQL execution and comparison
        if is_pandas_only:
            # Use the pandas result as the expected output
            expected_output = pandas_result.copy()
            sql_solution = None  # Set to None for pandas-only problems
        else:
            # Execute SQL solution
            sql_result, sql_error = execute_sql(sql_solution, input_tables)
            if sql_error:
                raise ValueError(
                    f"Claude's SQL solution failed to execute. This is a problem generation error.\n"
                    f"SQL solution: {sql_solution}\n"
                    f"Error: {sql_error}"
                )

            if sql_result is None or sql_result.empty:
                raise ValueError(
                    f"Claude's SQL solution produced no output. This is a problem generation error.\n"
                    f"SQL solution: {sql_solution}"
                )

            # Compare pandas and SQL results - they must match EXACTLY
            is_match, feedback = compare_dataframes(pandas_result, sql_result)
            if not is_match:
                raise ValueError(
                    f"Claude's pandas and SQL solutions produce different results. This is a problem generation error.\n"
                    f"Pandas solution: {pandas_solution}\n"
                    f"SQL solution: {sql_solution}\n"
                    f"Mismatch details: {feedback}\n"
                    f"Pandas result shape: {pandas_result.shape}, SQL result shape: {sql_result.shape}"
                )

            # Use the pandas result as the expected output (they're identical)
            expected_output = pandas_result.copy()

        # Create and return Problem object
        return Problem(
            input_tables=input_tables,
            question=problem_data["question"],
            expected_output=expected_output,
            topic=problem_data["topic"],
            difficulty=problem_data["difficulty"],
            pandas_solution=pandas_solution,
            sql_solution=sql_solution,
            pandas_only=is_pandas_only
        )

    except ValueError as ve:
        # Re-raise ValueError with original message
        raise ve
    except Exception as e:
        # Wrap other exceptions with more context
        error_type = type(e).__name__
        raise Exception(f"{error_type}: {str(e)}")


if __name__ == "__main__":
    print("Testing Claude API connection...")
    if test_api_connection():
        print("✓ API connection successful!")
    else:
        print("✗ API connection failed. Please check your API key.")
