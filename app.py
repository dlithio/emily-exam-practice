import streamlit as st
import pandas as pd
from models import Problem


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

# Problem Section
st.header("Problem")
display_problem(sample_problem)

# Your Code Section
st.header("Your Code")
st.write("Code editor will appear here...")

# Result Section
st.header("Result")
st.write("Your results will appear here...")
