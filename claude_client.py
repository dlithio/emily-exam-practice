"""
Claude API client for generating practice problems.
"""
import os
import json
import random
from typing import Optional
from functools import lru_cache
from anthropic import Anthropic
import pandas as pd
from models import Problem
from dataset_topics import get_random_topic

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


def build_problem_generation_prompt(topic: str, difficulty: str = "easy", dataset_topic: Optional[str] = None) -> str:
    """
    Build a prompt that instructs Claude to generate a practice problem.

    Args:
        topic: The skill to focus on (e.g., "filter_rows", "group_by", "joins")
        difficulty: Problem difficulty ("easy", "medium", "hard")
        dataset_topic: Optional dataset domain to use (e.g., "library", "hospital", "movies")

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
    }

    topic_desc = topic_descriptions.get(topic, topic)

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
    if topic == "derived_column":
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

    prompt = f"""Generate a pandas/SQL practice problem focused on {topic_desc}.
{dataset_instruction}{derived_column_instruction}
REQUIREMENTS:
1. Create 1-2 small DataFrames as input tables with realistic column names and data
2. Write a clear word problem describing what the user should do
3. Provide the expected output DataFrame showing the correct answer
4. Ensure the problem can be solved in BOTH pandas AND SQL
5. Difficulty: {difficulty} - {difficulty_guide}

TOPIC FOCUS: {topic}
{topic_desc}

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
  "expected_output": {{
    "columns": ["col1", "col2", ...],
    "data": [
      [val1, val2, ...],
      [val1, val2, ...]
    ]
  }},
  "topic": "{topic}",
  "difficulty": "{difficulty}",
  "pandas_solution": "result = ...",
  "sql_solution": "SELECT ..."
}}

REFERENCE SOLUTIONS REQUIREMENT:
You MUST provide both a pandas solution and a SQL solution that produce the exact expected_output:
- pandas_solution: Complete pandas code that assigns the final result to a variable named 'result'.
  The input table names will be available as DataFrame variables.
  Example: "result = employees[employees['salary'] > 70000]"
- sql_solution: Complete SELECT query that works with standard SQL.
  The input tables will be available as SQL tables with the same names.
  Example: "SELECT * FROM employees WHERE salary > 70000"
- Both solutions MUST produce exactly the expected_output DataFrame
- Test your solutions mentally to ensure they work correctly
- Make sure column names, types, and row order match the expected_output exactly

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
  "expected_output": {{
    "columns": ["name", "department", "salary"],
    "data": [
      ["Alice", "Engineering", 95000],
      ["Charlie", "Engineering", 88000]
    ]
  }},
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
def _cached_generate_problem(topic: str, difficulty: str, dataset_topic: str, cache_key: int) -> str:
    """
    Cached version of API call to avoid regenerating during development.

    Args:
        topic: Topic for the problem
        difficulty: Difficulty level
        dataset_topic: Dataset domain for the problem
        cache_key: Arbitrary key to control cache invalidation

    Returns:
        str: Raw JSON response from API
    """
    client = get_client()
    prompt = build_problem_generation_prompt(topic, difficulty, dataset_topic)

    response = client.messages.create(
        model=DEFAULT_MODEL,
        max_tokens=2000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.content[0].text


def generate_problem(topic: str, difficulty: str = "easy", use_cache: bool = True) -> Problem:
    """
    Generate a practice problem using Claude API.

    Args:
        topic: The skill to focus on (e.g., "filter_rows", "group_by", "joins")
        difficulty: Problem difficulty ("easy", "medium", "hard")
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

        # Call API (with or without cache)
        if use_cache:
            # Using hash of topic+difficulty+dataset_topic as cache key for reproducibility
            cache_key = hash(f"{topic}_{difficulty}_{dataset_topic}") % 1000
            response_text = _cached_generate_problem(topic, difficulty, dataset_topic, cache_key)
        else:
            try:
                client = get_client()
                prompt = build_problem_generation_prompt(topic, difficulty, dataset_topic)
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

        # Validate required fields
        required_fields = ["input_tables", "question", "expected_output", "topic", "difficulty"]
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

        # Convert expected output to DataFrame
        try:
            expected_output = _json_to_dataframe(problem_data["expected_output"])
        except Exception as e:
            raise ValueError(f"Failed to convert expected output to DataFrame: {e}")

        # Validate that we have at least one input table
        if not input_tables:
            raise ValueError("API response contains no input tables. Please try again.")

        # Validate that expected output has data
        if expected_output.empty:
            raise ValueError("API response contains empty expected output. Please try again.")

        # Extract optional solution fields
        pandas_solution = problem_data.get("pandas_solution")
        sql_solution = problem_data.get("sql_solution")

        # Create and return Problem object
        return Problem(
            input_tables=input_tables,
            question=problem_data["question"],
            expected_output=expected_output,
            topic=problem_data["topic"],
            difficulty=problem_data["difficulty"],
            pandas_solution=pandas_solution,
            sql_solution=sql_solution
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
