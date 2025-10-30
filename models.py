"""Data models for the Pandas & SQL Practice App."""

from dataclasses import dataclass
from typing import Dict, Optional
import pandas as pd


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
    """
    input_tables: Dict[str, pd.DataFrame]
    question: str
    expected_output: pd.DataFrame
    topic: str
    difficulty: Optional[str] = "easy"
    pandas_solution: Optional[str] = None
    sql_solution: Optional[str] = None

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
