"""Data models for the Pandas & SQL Practice App."""

from dataclasses import dataclass
from typing import Dict, Optional, Any
import pandas as pd
import json


@dataclass
class Problem:
    """Represents a practice problem with input data, question, and expected output.

    Attributes:
        input_tables: Dictionary mapping table names to pandas DataFrames
        question: Description of what the user needs to do
        expected_output: DataFrame showing the correct answer
        topic: Category of the problem (e.g., "filter_rows", "group_by", "joins")
        difficulty: Optional difficulty level ("easy", "medium", "hard")
        pandas_solution: Optional reference solution using pandas (should assign to 'result' variable)
        sql_solution: Optional reference solution using SQL (complete SELECT query)
        pandas_only: Whether this problem is pandas-only (e.g., pivot/melt operations)
    """
    input_tables: Dict[str, pd.DataFrame]
    question: str
    expected_output: pd.DataFrame
    topic: str
    difficulty: Optional[str] = "easy"
    pandas_solution: Optional[str] = None
    sql_solution: Optional[str] = None
    pandas_only: bool = False

    def __repr__(self) -> str:
        """Pretty print the problem structure."""
        tables_info = ", ".join(f"{name}({len(df)} rows)" for name, df in self.input_tables.items())
        result = (
            f"Problem(\n"
            f"  topic='{self.topic}',\n"
            f"  difficulty='{self.difficulty}',\n"
            f"  tables=[{tables_info}],\n"
            f"  question='{self.question[:50]}...',\n"
            f"  expected_output=({self.expected_output.shape[0]} rows, {self.expected_output.shape[1]} cols)"
        )

        # Add solution information if present
        if self.pandas_solution or self.sql_solution:
            result += ",\n  solutions=["
            solutions = []
            if self.pandas_solution:
                solutions.append("pandas")
            if self.sql_solution:
                solutions.append("SQL")
            result += ", ".join(solutions) + "]"

        result += "\n)"
        return result

    def to_json(self) -> Dict[str, Any]:
        """Serialize Problem to JSON-compatible dictionary.

        Returns:
            Dictionary containing all problem fields with DataFrames converted to JSON format
        """
        # Convert input tables DataFrames to JSON-compatible format
        input_tables_json = {}
        for table_name, df in self.input_tables.items():
            input_tables_json[table_name] = {
                'columns': list(df.columns),
                'data': df.to_dict(orient='records')
            }

        # Convert expected output DataFrame to JSON format
        expected_output_json = {
            'columns': list(self.expected_output.columns),
            'data': self.expected_output.to_dict(orient='records')
        }

        return {
            'input_tables': input_tables_json,
            'question': self.question,
            'expected_output': expected_output_json,
            'topic': self.topic,
            'difficulty': self.difficulty,
            'pandas_solution': self.pandas_solution,
            'sql_solution': self.sql_solution,
            'pandas_only': self.pandas_only
        }

    @classmethod
    def from_json(cls, json_dict: Dict[str, Any]) -> 'Problem':
        """Create Problem from JSON dictionary.

        Args:
            json_dict: Dictionary containing problem data in JSON format

        Returns:
            Problem object

        Raises:
            ValueError: If required fields are missing or data is invalid
        """
        # Validate required fields
        required_fields = ['input_tables', 'question', 'expected_output', 'topic']
        missing_fields = [field for field in required_fields if field not in json_dict]
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")

        # Convert input tables from JSON to DataFrames
        input_tables = {}
        for table_name, table_data in json_dict['input_tables'].items():
            if 'columns' not in table_data or 'data' not in table_data:
                raise ValueError(f"Table '{table_name}' missing 'columns' or 'data' field")
            input_tables[table_name] = pd.DataFrame(table_data['data'], columns=table_data['columns'])

        # Convert expected output from JSON to DataFrame
        expected_data = json_dict['expected_output']
        if 'columns' not in expected_data or 'data' not in expected_data:
            raise ValueError("Expected output missing 'columns' or 'data' field")
        expected_output = pd.DataFrame(expected_data['data'], columns=expected_data['columns'])

        # Create and return Problem object
        return cls(
            input_tables=input_tables,
            question=json_dict['question'],
            expected_output=expected_output,
            topic=json_dict['topic'],
            difficulty=json_dict.get('difficulty', 'easy'),
            pandas_solution=json_dict.get('pandas_solution'),
            sql_solution=json_dict.get('sql_solution'),
            pandas_only=json_dict.get('pandas_only', False)
        )


if __name__ == "__main__":
    # Verification: Create a hardcoded sample problem
    print("Creating sample problem for verification...\n")

    # Create sample input data
    employees = pd.DataFrame({
        'name': ['Alice', 'Bob', 'Charlie', 'Diana'],
        'department': ['Engineering', 'Sales', 'Engineering', 'HR'],
        'salary': [95000, 65000, 88000, 72000],
        'years': [5, 3, 7, 4]
    })

    # Expected output for a filtering problem
    expected = pd.DataFrame({
        'name': ['Alice', 'Charlie'],
        'department': ['Engineering', 'Engineering'],
        'salary': [95000, 88000],
        'years': [5, 7]
    })

    # Create Problem instance
    sample_problem = Problem(
        input_tables={'employees': employees},
        question="Filter the employees table to show only employees in the Engineering department.",
        expected_output=expected,
        topic="filter_rows",
        difficulty="easy"
    )

    # Display the problem
    print(sample_problem)
    print("\n" + "="*60 + "\n")
    print("Input Table 'employees':")
    print(sample_problem.input_tables['employees'])
    print("\nQuestion:")
    print(sample_problem.question)
    print("\nExpected Output:")
    print(sample_problem.expected_output)
    print("\n✓ Problem structure verified successfully!")
