import streamlit as st
import pandas as pd
import sqlite3
import traceback
import random
import signal
from contextlib import contextmanager
from typing import Tuple, Optional
from models import Problem
from claude_client import generate_problem


# Available topics from the plan (foundational topics)
TOPICS = [
    "filter_columns",
    "filter_rows",
    "aggregations",
    "distinct",
    "joins",
    "order_by",
    "limit"
]

# Execution timeout in seconds
EXECUTION_TIMEOUT = 5


class TimeoutError(Exception):
    """Raised when code execution times out."""
    pass


@contextmanager
def time_limit(seconds):
    """
    Context manager to limit execution time of code block.

    Args:
        seconds: Maximum number of seconds to allow execution

    Raises:
        TimeoutError: If execution exceeds time limit
    """
    def signal_handler(signum, frame):
        raise TimeoutError(f"Code execution exceeded {seconds} second time limit")

    # Set up signal handler (Unix/macOS only)
    try:
        signal.signal(signal.SIGALRM, signal_handler)
        signal.alarm(seconds)
        try:
            yield
        finally:
            signal.alarm(0)  # Disable alarm
    except (AttributeError, ValueError):
        # AttributeError: On Windows, signal.SIGALRM doesn't exist
        # ValueError: signal only works in main thread (Streamlit threading)
        # In both cases, just yield without timeout protection
        yield


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
        with time_limit(EXECUTION_TIMEOUT):
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

    except TimeoutError as e:
        return None, f"Timeout Error: {str(e)}\n\nYour code took too long to execute. Check for infinite loops or very slow operations."
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
    conn = None
    try:
        with time_limit(EXECUTION_TIMEOUT):
            # Create an in-memory SQLite database
            conn = sqlite3.connect(':memory:')

            # Load all input tables into the database
            for table_name, df in input_tables.items():
                df.to_sql(table_name, conn, index=False, if_exists='replace')

            # Execute the user's SQL query and fetch results as a DataFrame
            result = pd.read_sql_query(query, conn)

            return result, None

    except TimeoutError as e:
        return None, f"Timeout Error: {str(e)}\n\nYour SQL query took too long to execute. Check for infinite loops or very slow operations."
    except Exception:
        return None, traceback.format_exc()
    finally:
        # Always close the connection if it was opened
        if conn is not None:
            try:
                conn.close()
            except:
                pass


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
        st.table(df)
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
if 'user_code' not in st.session_state:
    st.session_state.user_code = ""
if 'selected_topics' not in st.session_state:
    st.session_state.selected_topics = []  # Empty list means "all topics"
if 'problem_info_revealed' not in st.session_state:
    st.session_state.problem_info_revealed = False

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
            st.error("⚠️ Failed to generate initial problem")
            st.error(f"Error details: {str(e)}")

            # Provide helpful troubleshooting information
            with st.expander("Troubleshooting"):
                st.markdown("""
                **Common issues:**
                1. **API Key**: Make sure your `ANTHROPIC_API_KEY` environment variable is set
                2. **Network**: Check your internet connection
                3. **API Status**: Visit https://status.anthropic.com to check if the API is operational

                **To set your API key:**
                ```bash
                export ANTHROPIC_API_KEY="your-key-here"
                ```

                Or add it to `.streamlit/secrets.toml`:
                ```toml
                ANTHROPIC_API_KEY = "your-key-here"
                ```
                """)

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

# Sidebar: Topic Selection and New Problem Button
with st.sidebar:
    st.header("Problem Generator")

    # Topic selector with checkboxes
    st.subheader("Select Topics to Practice:")
    st.caption("Select topics to focus on (or leave all unchecked for random)")

    # Create a list to track which topics are selected
    selected_topics = []

    # Create a checkbox for each topic
    for topic in TOPICS:
        # Format topic name for display (convert underscores to spaces and title case)
        display_name = topic.replace("_", " ").title()

        # Use session state to persist checkbox state
        checkbox_key = f"topic_{topic}"
        if checkbox_key not in st.session_state:
            st.session_state[checkbox_key] = False

        if st.checkbox(display_name, key=checkbox_key):
            selected_topics.append(topic)

    # Update selected topics in session state
    st.session_state.selected_topics = selected_topics

    # New problem button
    if st.button("Generate New Problem", type="primary", use_container_width=True):
        # Clear previous results and code
        st.session_state.result_df = None
        st.session_state.error_message = None
        st.session_state.is_correct = None
        st.session_state.feedback_message = None
        st.session_state.show_expected = False
        st.session_state.user_code = ""
        st.session_state.problem_info_revealed = False  # Hide info for new problem

        # Determine which topics to choose from
        if st.session_state.selected_topics:
            # Use only selected topics
            available_topics = st.session_state.selected_topics
        else:
            # No topics selected, use all topics
            available_topics = TOPICS

        # Choose a random topic from available topics
        topic = random.choice(available_topics)

        # Generate new problem
        # Never reveal the topic in messages - user must click "Reveal Problem Info"
        spinner_message = "Generating new problem..."
        success_message = "✓ New problem generated!"

        with st.spinner(spinner_message):
            try:
                new_problem = generate_problem(
                    topic=topic,
                    difficulty="easy",
                    use_cache=False  # Don't use cache for new problems
                )
                # Only update current problem if generation succeeded
                st.session_state.current_problem = new_problem
                st.success(success_message)
                st.rerun()
            except Exception as e:
                # Keep the previous problem - don't overwrite it
                st.error("⚠️ Failed to generate new problem. Your current problem is still available.")
                st.warning(f"Error details: {str(e)}")

                # Provide retry guidance
                st.info("💡 Try again or select different topics. The API may be temporarily busy.")

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

# Helpful info about code execution
st.caption(f"💡 Code execution has a {EXECUTION_TIMEOUT} second timeout limit")

# Code input
user_code = st.text_area(
    "Enter your code:",
    value=st.session_state.user_code,
    height=200,
    placeholder="# Write your Pandas code here..." if language == "Pandas" else "-- Write your SQL query here...",
    key="code_input"
)

# Update session state with current code
st.session_state.user_code = user_code

# Buttons: Run Code and Reveal Problem Info
col1, col2 = st.columns([1, 1])
with col1:
    run_button = st.button("Run Code", type="primary", use_container_width=True)
with col2:
    if st.button("Reveal Problem Info", use_container_width=True):
        st.session_state.problem_info_revealed = True

# Show problem info if revealed
if st.session_state.problem_info_revealed and st.session_state.current_problem:
    topic_display = st.session_state.current_problem.topic.replace("_", " ").title()
    difficulty_display = st.session_state.current_problem.difficulty.title() if st.session_state.current_problem.difficulty else "Easy"
    st.info(f"📚 **Topic:** {topic_display} | **Difficulty:** {difficulty_display}")

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
        st.table(st.session_state.result_df)
    elif st.session_state.is_correct is False:
        st.error(st.session_state.feedback_message)

        # Show user's output and expected output side-by-side
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Your Output:")
            st.table(st.session_state.result_df)
        with col2:
            st.subheader("Expected Output:")
            if st.session_state.show_expected:
                st.table(st.session_state.current_problem.expected_output)
            else:
                if st.button("Show Expected Output"):
                    st.session_state.show_expected = True
                    st.rerun()
    else:
        # Execution successful but no comparison result (shouldn't happen)
        st.subheader("Your Output:")
        st.table(st.session_state.result_df)
else:
    st.write("Your results will appear here after running your code.")
