"""
Claude API client for generating practice problems.
"""
import os
import json
from typing import Optional
from functools import lru_cache
from anthropic import Anthropic
import pandas as pd
from models import Problem

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


def build_problem_generation_prompt(topic: str, difficulty: str = "easy") -> str:
    """
    Build a prompt that instructs Claude to generate a practice problem.

    Args:
        topic: The skill to focus on (e.g., "filter_rows", "group_by", "joins")
        difficulty: Problem difficulty ("easy", "medium", "hard")

    Returns:
        str: Formatted prompt for Claude
    """

    # Map topics to more descriptive names for the prompt
    topic_descriptions = {
        "filter_columns": "selecting specific columns (SELECT in SQL, df[[]] in pandas)",
        "filter_rows": "filtering rows based on conditions (WHERE in SQL, df[condition] in pandas)",
        "group_by": "aggregating data with GROUP BY (groupby in pandas)",
        "distinct": "finding distinct/unique values (DISTINCT in SQL, unique/drop_duplicates in pandas)",
        "joins": "joining tables (JOIN in SQL, merge in pandas)",
        "order_by": "sorting data (ORDER BY in SQL, sort_values in pandas)",
        "limit": "limiting number of results (LIMIT in SQL, head in pandas)",
    }

    topic_desc = topic_descriptions.get(topic, topic)

    # Difficulty guidelines
    difficulty_guidelines = {
        "easy": "Keep the problem simple with a single operation on small data (3-5 rows). Use clear, straightforward conditions.",
        "medium": "Use 2-3 combined operations on medium-sized data (5-10 rows). Include slightly more complex logic.",
        "hard": "Create a multi-step problem with larger data (10-15 rows), edge cases, and complex conditions."
    }

    difficulty_guide = difficulty_guidelines.get(difficulty, difficulty_guidelines["easy"])

    prompt = f"""Generate a pandas/SQL practice problem focused on {topic_desc}.

REQUIREMENTS:
1. Create 1-2 small DataFrames as input tables with realistic column names and data
2. Write a clear word problem describing what the user should do
3. Provide the expected output DataFrame showing the correct answer
4. Ensure the problem can be solved in BOTH pandas AND SQL
5. Difficulty: {difficulty} - {difficulty_guide}

TOPIC FOCUS: {topic}
{topic_desc}

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
  "difficulty": "{difficulty}"
}}

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
  "question": "Find all employees in the Engineering department.",
  "expected_output": {{
    "columns": ["name", "department", "salary"],
    "data": [
      ["Alice", "Engineering", 95000],
      ["Charlie", "Engineering", 88000]
    ]
  }},
  "topic": "filter_rows",
  "difficulty": "easy"
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
def _cached_generate_problem(topic: str, difficulty: str, cache_key: int) -> str:
    """
    Cached version of API call to avoid regenerating during development.

    Args:
        topic: Topic for the problem
        difficulty: Difficulty level
        cache_key: Arbitrary key to control cache invalidation

    Returns:
        str: Raw JSON response from API
    """
    client = get_client()
    prompt = build_problem_generation_prompt(topic, difficulty)

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
        # Call API (with or without cache)
        if use_cache:
            # Using hash of topic+difficulty as cache key for reproducibility
            cache_key = hash(f"{topic}_{difficulty}") % 1000
            response_text = _cached_generate_problem(topic, difficulty, cache_key)
        else:
            client = get_client()
            prompt = build_problem_generation_prompt(topic, difficulty)
            response = client.messages.create(
                model=DEFAULT_MODEL,
                max_tokens=2000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            response_text = response.content[0].text

        # Parse JSON response
        cleaned_response = strip_markdown_code_blocks(response_text)

        try:
            problem_data = json.loads(cleaned_response)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Failed to parse API response as JSON: {e}\n"
                f"Raw response: {response_text[:200]}..."
            )

        # Validate required fields
        required_fields = ["input_tables", "question", "expected_output", "topic", "difficulty"]
        missing_fields = [field for field in required_fields if field not in problem_data]
        if missing_fields:
            raise ValueError(f"API response missing required fields: {missing_fields}")

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

        # Create and return Problem object
        return Problem(
            input_tables=input_tables,
            question=problem_data["question"],
            expected_output=expected_output,
            topic=problem_data["topic"],
            difficulty=problem_data["difficulty"]
        )

    except ValueError:
        # Re-raise ValueError with original message
        raise
    except Exception as e:
        # Wrap other exceptions with more context
        raise Exception(f"Failed to generate problem: {e}")


if __name__ == "__main__":
    print("Testing Claude API connection...")
    if test_api_connection():
        print("✓ API connection successful!")
    else:
        print("✗ API connection failed. Please check your API key.")
