"""Code execution and comparison utilities for pandas and SQL."""
import pandas as pd
import sqlite3
import traceback
import signal
from contextlib import contextmanager
from typing import Tuple, Optional


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
