import streamlit as st
import pandas as pd
import sqlite3
import traceback
from typing import Tuple, Optional
from models import Problem
from claude_client import generate_problem


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


def compare_dataframes(user_df: any, expected_df: pd.DataFrame) -> Tuple[bool, str]:
    """Compare user's output DataFrame with expected output.

    By default, both row order and column order must match exactly.

    Args:
        user_df: User's output (could be any type)
        expected_df: Expected output DataFrame

    Returns:
        Tuple of (is_correct, feedback_message)
        - is_correct: True if outputs match, False otherwise
        - feedback_message: Detailed feedback about the comparison
    """
    # Check if user_df is a DataFrame
    if not isinstance(user_df, pd.DataFrame):
        return False, f"Expected a DataFrame, but got {type(user_df).__name__}"

    # Check if shapes match
    if user_df.shape != expected_df.shape:
        return False, (
            f"Shape mismatch: Your output has shape {user_df.shape} "
            f"(rows={user_df.shape[0]}, columns={user_df.shape[1]}), "
            f"but expected shape {expected_df.shape} "
            f"(rows={expected_df.shape[0]}, columns={expected_df.shape[1]})"
        )

    # Check if column names match (exact order)
    if list(user_df.columns) != list(expected_df.columns):
        user_cols_set = set(user_df.columns)
        expected_cols_set = set(expected_df.columns)

        # Check if columns are just in wrong order or actually different
        if user_cols_set == expected_cols_set:
            return False, (
                f"Column order mismatch: Your columns are {list(user_df.columns)}, "
                f"but expected {list(expected_df.columns)}"
            )
        else:
            # Columns are actually different
            missing_cols = expected_cols_set - user_cols_set
            extra_cols = user_cols_set - expected_cols_set

            msg_parts = ["Column mismatch:"]
            if missing_cols:
                msg_parts.append(f"Missing columns: {sorted(missing_cols)}")
            if extra_cols:
                msg_parts.append(f"Extra columns: {sorted(extra_cols)}")

            return False, " ".join(msg_parts)

    # Reset index to ensure clean comparison (but don't sort)
    user_clean = user_df.reset_index(drop=True)
    expected_clean = expected_df.reset_index(drop=True)

    # Use pandas testing utility for comparison
    try:
        pd.testing.assert_frame_equal(
            user_clean,
            expected_clean,
            check_dtype=False,  # Be lenient with data types (int vs float is OK)
            check_exact=False,  # Use approximate comparison for floats
            rtol=1e-5,  # Relative tolerance for float comparison
            atol=1e-8   # Absolute tolerance for float comparison
        )
        return True, "Correct! Your output matches the expected result."
    except AssertionError as e:
        # Parse the assertion error to provide helpful feedback
        error_msg = str(e)

        # Try to provide more specific feedback
        if "dtype" in error_msg.lower():
            return False, f"Data type mismatch: {error_msg}"
        elif "values" in error_msg.lower() or "different" in error_msg.lower():
            # Find which values differ
            differences = []
            for col in user_clean.columns:
                if not user_clean[col].equals(expected_clean[col]):
                    differences.append(col)

            if differences:
                return False, (
                    f"Values don't match in column(s): {differences}. "
                    f"Check your filtering/calculation logic."
                )
            else:
                return False, f"Values don't match: {error_msg}"
        else:
            return False, f"Output doesn't match expected result: {error_msg}"


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


# Initialize session state
if 'result_df' not in st.session_state:
    st.session_state.result_df = None
if 'error_message' not in st.session_state:
    st.session_state.error_message = None
if 'is_correct' not in st.session_state:
    st.session_state.is_correct = None
if 'feedback_message' not in st.session_state:
    st.session_state.feedback_message = None
if 'show_expected' not in st.session_state:
    st.session_state.show_expected = False
if 'current_problem' not in st.session_state:
    st.session_state.current_problem = None

# Generate problem on first load
if st.session_state.current_problem is None:
    with st.spinner("Generating your first problem..."):
        try:
            # Generate a problem with a random foundational topic
            # Start with filter_rows as it's the first foundational topic
            st.session_state.current_problem = generate_problem(
                topic="filter_rows",
                difficulty="easy",
                use_cache=True
            )
        except Exception as e:
            st.error(f"Failed to generate problem: {e}")
            st.error("Please check your ANTHROPIC_API_KEY is set correctly.")
            st.stop()

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
display_problem(st.session_state.current_problem)

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

# Handle code execution when button is clicked
if run_button:
    # Reset show_expected flag when running new code
    st.session_state.show_expected = False

    if not user_code.strip():
        st.session_state.result_df = None
        st.session_state.error_message = "Please enter some code first!"
        st.session_state.is_correct = None
        st.session_state.feedback_message = None
    elif language == "Pandas":
        result_df, error = execute_pandas(user_code, st.session_state.current_problem.input_tables)
        st.session_state.result_df = result_df
        st.session_state.error_message = error

        # If execution was successful, compare with expected output
        if error is None and result_df is not None:
            is_correct, feedback = compare_dataframes(result_df, st.session_state.current_problem.expected_output)
            st.session_state.is_correct = is_correct
            st.session_state.feedback_message = feedback
        else:
            st.session_state.is_correct = None
            st.session_state.feedback_message = None
    else:  # SQL
        result_df, error = execute_sql(user_code, st.session_state.current_problem.input_tables)
        st.session_state.result_df = result_df
        st.session_state.error_message = error

        # If execution was successful, compare with expected output
        if error is None and result_df is not None:
            is_correct, feedback = compare_dataframes(result_df, st.session_state.current_problem.expected_output)
            st.session_state.is_correct = is_correct
            st.session_state.feedback_message = feedback
        else:
            st.session_state.is_correct = None
            st.session_state.feedback_message = None

# Result Section
st.header("Result")

# Display results from session state
if st.session_state.error_message:
    st.error(st.session_state.error_message)
elif st.session_state.result_df is not None:
    # Display comparison feedback
    if st.session_state.is_correct is True:
        st.success(st.session_state.feedback_message)
        # Show user's output
        st.subheader("Your Output:")
        st.dataframe(st.session_state.result_df)
    elif st.session_state.is_correct is False:
        st.error(st.session_state.feedback_message)

        # Show user's output and expected output side-by-side
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Your Output:")
            st.dataframe(st.session_state.result_df)
        with col2:
            st.subheader("Expected Output:")
            if st.session_state.show_expected:
                st.dataframe(st.session_state.current_problem.expected_output)
            else:
                if st.button("Show Expected Output"):
                    st.session_state.show_expected = True
                    st.rerun()
    else:
        # Execution successful but no comparison result (shouldn't happen)
        st.subheader("Your Output:")
        st.dataframe(st.session_state.result_df)
else:
    st.write("Your results will appear here after running your code.")
