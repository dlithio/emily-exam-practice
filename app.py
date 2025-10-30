import streamlit as st
import pandas as pd
import sqlite3
import traceback
from typing import Tuple, Optional
from models import Problem


def execute_pandas(code: str, input_tables: dict[str, pd.DataFrame]) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """Execute user's pandas code safely and return the result.

    Args:
        code: User's pandas code as a string
        input_tables: Dictionary of table names to DataFrames

    Returns:
        Tuple of (result_dataframe, error_message)
        - If successful: (DataFrame, None)
        - If error: (None, error_message_string)
    """
    try:
        # Prepare a restricted namespace with input tables and pandas
        namespace = {
            'pd': pd,
            '__builtins__': __builtins__,
        }

        # Add all input tables to the namespace as variables
        for table_name, df in input_tables.items():
            namespace[table_name] = df.copy()  # Use copy to prevent modification of original data

        # Execute the user's code
        exec(code, namespace)

        # Check if 'result' variable was created
        if 'result' not in namespace:
            return None, "Error: Your code must assign the output to a variable named 'result'"

        result = namespace['result']

        # Verify result is a DataFrame
        if not isinstance(result, pd.DataFrame):
            return None, f"Error: Expected result to be a DataFrame, but got {type(result).__name__}"

        return result, None

    except Exception:
        return None, traceback.format_exc()


def execute_sql(query: str, input_tables: dict[str, pd.DataFrame]) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """Execute user's SQL query safely and return the result.

    Args:
        query: User's SQL query as a string
        input_tables: Dictionary of table names to DataFrames

    Returns:
        Tuple of (result_dataframe, error_message)
        - If successful: (DataFrame, None)
        - If error: (None, error_message_string)
    """
    try:
        # Create an in-memory SQLite database
        conn = sqlite3.connect(':memory:')

        # Load all input tables into the database
        for table_name, df in input_tables.items():
            df.to_sql(table_name, conn, index=False, if_exists='replace')

        # Execute the user's SQL query and fetch results as a DataFrame
        result = pd.read_sql_query(query, conn)

        # Close the connection
        conn.close()

        return result, None

    except Exception:
        return None, traceback.format_exc()


def display_problem(problem: Problem) -> None:
    """Display a problem with its input tables and question.

    Args:
        problem: A Problem object containing input tables, question, and expected output
    """
    # Display the question
    st.subheader("Question")
    st.write(problem.question)

    # Display input tables
    st.subheader("Input Tables")
    for table_name, df in problem.input_tables.items():
        st.write(f"**Table: `{table_name}`**")
        st.dataframe(df, width='stretch')
        st.write("")  # Add spacing between tables

    # Note: We intentionally hide the expected_output - that's the answer!


# Create a hardcoded sample problem for testing
employees = pd.DataFrame({
    'name': ['Alice', 'Bob', 'Charlie', 'Diana'],
    'department': ['Engineering', 'Sales', 'Engineering', 'HR'],
    'salary': [95000, 65000, 88000, 72000],
    'years': [5, 3, 7, 4]
})

expected = pd.DataFrame({
    'name': ['Alice', 'Charlie'],
    'department': ['Engineering', 'Engineering'],
    'salary': [95000, 88000],
    'years': [5, 7]
})

sample_problem = Problem(
    input_tables={'employees': employees},
    question="Filter the employees table to show only employees in the Engineering department.",
    expected_output=expected,
    topic="filter_rows",
    difficulty="easy"
)

# Main App Layout
st.title("Pandas & SQL Practice")

# Custom CSS for monospaced code input
st.markdown("""
    <style>
    textarea {
        font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', 'source-code-pro', monospace !important;
        font-size: 14px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Problem Section
st.header("Problem")
display_problem(sample_problem)

# Your Code Section
st.header("Your Code")

# Language selection
language = st.radio(
    "Select language:",
    options=["Pandas", "SQL"],
    horizontal=True
)

# Code input
user_code = st.text_area(
    "Enter your code:",
    height=200,
    placeholder="# Write your Pandas code here..." if language == "Pandas" else "-- Write your SQL query here..."
)

# Run button
run_button = st.button("Run Code", type="primary")

# Result Section
st.header("Result")
if run_button:
    if not user_code.strip():
        st.warning("Please enter some code first!")
    elif language == "Pandas":
        result_df, error = execute_pandas(user_code, sample_problem.input_tables)

        if error:
            st.error(error)
        else:
            st.success("Code executed successfully!")
            st.subheader("Your Output:")
            st.dataframe(result_df)
    else:  # SQL
        result_df, error = execute_sql(user_code, sample_problem.input_tables)

        if error:
            st.error(error)
        else:
            st.success("Code executed successfully!")
            st.subheader("Your Output:")
            st.dataframe(result_df)
else:
    st.write("Your results will appear here after running your code.")
