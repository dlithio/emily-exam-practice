import streamlit as st
import pandas as pd
import logging
import json
from datetime import datetime
from typing import Tuple, Optional
from models import Problem
from claude_client import generate_problem
from execution import execute_pandas, execute_sql, compare_dataframes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Available topics from the plan (foundational topics)
TOPICS = [
    "filter_columns",
    "filter_rows",
    "aggregations",
    "distinct",
    "joins",
    "order_by",
    "limit",
    "derived_column"
]

# Execution timeout in seconds (imported from execution module)
from execution import EXECUTION_TIMEOUT


def verify_problem_solutions(problem: Problem) -> dict:
    """Verify that Claude's reference solutions produce the expected output.

    Args:
        problem: Problem object containing pandas_solution, sql_solution, and expected_output

    Returns:
        Dictionary with verification results:
        {
            'pandas_valid': bool,
            'sql_valid': bool,
            'pandas_error': str or None,
            'sql_error': str or None,
            'pandas_feedback': str or None,
            'sql_feedback': str or None
        }
    """
    result = {
        'pandas_valid': False,
        'sql_valid': False,
        'pandas_error': None,
        'sql_error': None,
        'pandas_feedback': None,
        'sql_feedback': None
    }

    # Verify pandas solution
    if problem.pandas_solution:
        pandas_result, pandas_error = execute_pandas(
            problem.pandas_solution,
            problem.input_tables
        )
        result['pandas_error'] = pandas_error

        if pandas_error is None and pandas_result is not None:
            is_correct, feedback = compare_dataframes(pandas_result, problem.expected_output)
            result['pandas_valid'] = is_correct
            result['pandas_feedback'] = feedback
        else:
            result['pandas_feedback'] = "Pandas solution failed to execute"

    # Verify SQL solution (skip for pandas-only problems)
    if problem.sql_solution and not problem.pandas_only:
        sql_result, sql_error = execute_sql(
            problem.sql_solution,
            problem.input_tables
        )
        result['sql_error'] = sql_error

        if sql_error is None and sql_result is not None:
            is_correct, feedback = compare_dataframes(sql_result, problem.expected_output)
            result['sql_valid'] = is_correct
            result['sql_feedback'] = feedback
        else:
            result['sql_feedback'] = "SQL solution failed to execute"
    elif problem.pandas_only:
        # For pandas-only problems, mark SQL as valid (N/A)
        result['sql_valid'] = True
        result['sql_feedback'] = "N/A (pandas-only problem)"

    return result


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
if 'solutions_revealed' not in st.session_state:
    st.session_state.solutions_revealed = False
if 'last_uploaded_file_id' not in st.session_state:
    st.session_state.last_uploaded_file_id = None
if 'difficulty' not in st.session_state:
    st.session_state.difficulty = "easy"

# Generate problem on first load
if st.session_state.current_problem is None:
    with st.spinner("Generating your first problem..."):
        try:
            # Generate a problem with difficulty from session state
            # For first load, use easy difficulty with no specific topic
            problem = generate_problem(
                difficulty=st.session_state.difficulty,
                selected_topics=[],
                use_cache=True
            )

            # Verify the reference solutions
            verification = verify_problem_solutions(problem)

            # Log verification results
            if not verification['pandas_valid']:
                logger.warning(f"Pandas solution verification failed for initial problem")
                logger.warning(f"Pandas error: {verification['pandas_error']}")
                logger.warning(f"Pandas feedback: {verification['pandas_feedback']}")

            if not verification['sql_valid']:
                logger.warning(f"SQL solution verification failed for initial problem")
                logger.warning(f"SQL error: {verification['sql_error']}")
                logger.warning(f"SQL feedback: {verification['sql_feedback']}")

            # Accept the problem even if verification fails (for MVP)
            st.session_state.current_problem = problem

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

    # Difficulty selector
    st.subheader("Select Difficulty:")
    difficulty = st.radio(
        "Difficulty Level:",
        options=["Easy", "Medium", "Hard"],
        index=0,
        horizontal=True,
        label_visibility="collapsed"
    )
    # Store lowercase version in session state
    st.session_state.difficulty = difficulty.lower()

    st.divider()

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
        st.session_state.solutions_revealed = False  # Hide solutions for new problem
        st.session_state.last_uploaded_file_id = None  # Reset file uploader

        # Generate new problem
        # Never reveal the topic in messages - user must click "Reveal Problem Info"
        spinner_message = "Generating practice problem..."
        success_message = "✓ New problem generated!"

        with st.spinner(spinner_message):
            try:
                new_problem = generate_problem(
                    difficulty=st.session_state.difficulty,
                    selected_topics=st.session_state.selected_topics,
                    use_cache=False  # Don't use cache for new problems
                )

                # Verify the reference solutions
                verification = verify_problem_solutions(new_problem)

                # Log verification results
                problem_label = f"{new_problem.difficulty} difficulty, topic: {new_problem.topic}"
                if not verification['pandas_valid']:
                    logger.warning(f"Pandas solution verification failed for {problem_label}")
                    logger.warning(f"Pandas error: {verification['pandas_error']}")
                    logger.warning(f"Pandas feedback: {verification['pandas_feedback']}")
                else:
                    logger.info(f"Pandas solution verified successfully for {problem_label}")

                if not verification['sql_valid']:
                    logger.warning(f"SQL solution verification failed for {problem_label}")
                    logger.warning(f"SQL error: {verification['sql_error']}")
                    logger.warning(f"SQL feedback: {verification['sql_feedback']}")
                else:
                    logger.info(f"SQL solution verified successfully for {problem_label}")

                # Accept the problem even if verification fails (for MVP)
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

    st.divider()

    # Export Problem button
    st.subheader("Save & Share")

    if st.session_state.current_problem:
        # Create filename with topic and timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        topic_name = st.session_state.current_problem.topic
        filename = f"problem_{topic_name}_{timestamp}.json"

        # Convert problem to JSON
        problem_json = st.session_state.current_problem.to_json()
        json_str = json.dumps(problem_json, indent=2)

        # Download button
        st.download_button(
            label="Export Problem",
            data=json_str,
            file_name=filename,
            mime="application/json",
            use_container_width=True,
            help="Download the current problem as a JSON file to save or share with others"
        )
    else:
        st.button("Export Problem", disabled=True, use_container_width=True, help="No problem loaded")

    # Import Problem file uploader
    uploaded_file = st.file_uploader(
        "Import Problem",
        type="json",
        help="Upload a previously exported problem JSON file"
    )

    if uploaded_file is not None:
        # Create a unique ID for this uploaded file to track if we've already processed it
        file_id = f"{uploaded_file.name}_{uploaded_file.size}"

        # Only process if this is a new file (not already processed)
        if file_id != st.session_state.last_uploaded_file_id:
            try:
                # Read and parse JSON
                json_data = json.loads(uploaded_file.read())

                # Create Problem object from JSON
                imported_problem = Problem.from_json(json_data)

                # Load as current problem
                st.session_state.current_problem = imported_problem

                # Clear previous results
                st.session_state.result_df = None
                st.session_state.error_message = None
                st.session_state.is_correct = None
                st.session_state.feedback_message = None
                st.session_state.show_expected = False
                st.session_state.user_code = ""
                st.session_state.problem_info_revealed = False
                st.session_state.solutions_revealed = False

                # Mark this file as processed
                st.session_state.last_uploaded_file_id = file_id

                # Show success message
                topic_display = imported_problem.topic.replace("_", " ").title()
                difficulty_display = imported_problem.difficulty.title() if imported_problem.difficulty else "Easy"
                st.success(f"✓ Problem imported successfully!\n\n**Topic:** {topic_display} | **Difficulty:** {difficulty_display}")
                st.rerun()

            except json.JSONDecodeError as e:
                st.error("❌ Invalid JSON file. Please check the file format.")
                st.warning(f"Error details: {str(e)}")
                st.session_state.last_uploaded_file_id = None
            except ValueError as e:
                st.error("❌ Invalid problem structure.")
                st.warning(f"Error details: {str(e)}")
                st.session_state.last_uploaded_file_id = None
            except Exception as e:
                st.error("❌ Failed to import problem.")
                st.warning(f"Error details: {str(e)}")
                st.session_state.last_uploaded_file_id = None

# Problem Section
st.header("Problem")
display_problem(st.session_state.current_problem)

# Your Code Section
st.header("Your Code")

# Check if this is a pandas-only problem
if st.session_state.current_problem.pandas_only:
    st.info("ℹ️ This problem tests pandas-specific functionality (pivot/melt)")
    language = "Pandas"  # Force pandas language
    # Show disabled language selector to indicate SQL is not available
    st.radio(
        "Select language:",
        options=["Pandas"],
        horizontal=True,
        disabled=True,
        help="SQL is not available for this problem as it tests pandas-specific operations"
    )
else:
    # Language selection (both pandas and SQL available)
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

# Buttons: Run Code, Reveal Problem Info, and Show Reference Solutions
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    run_button = st.button("Run Code", type="primary", use_container_width=True)
with col2:
    if st.button("Reveal Problem Info", use_container_width=True):
        st.session_state.problem_info_revealed = True
with col3:
    if st.button("Show Reference Solutions", use_container_width=True):
        st.session_state.solutions_revealed = True

# Show problem info if revealed
if st.session_state.problem_info_revealed and st.session_state.current_problem:
    difficulty_display = st.session_state.current_problem.difficulty.title() if st.session_state.current_problem.difficulty else "Easy"

    # Display skills/topic
    if st.session_state.current_problem.topic == "multi_skill":
        # For multi-skill problems, try to infer skills or show as "Multiple Skills"
        st.info(f"📚 **Skills:** Multiple Skills | **Difficulty:** {difficulty_display}")
    else:
        # For single-skill problems, show the topic
        topic_display = st.session_state.current_problem.topic.replace("_", " ").title()
        st.info(f"📚 **Topic:** {topic_display} | **Difficulty:** {difficulty_display}")

# Show reference solutions if revealed
if st.session_state.solutions_revealed and st.session_state.current_problem:
    st.subheader("Reference Solutions")
    st.caption("These are Claude's reference solutions that were verified to produce the expected output")

    # Display pandas solution
    if st.session_state.current_problem.pandas_solution:
        with st.expander("🐼 Pandas Solution", expanded=True):
            st.code(st.session_state.current_problem.pandas_solution, language="python")

    # Display SQL solution
    if st.session_state.current_problem.sql_solution:
        with st.expander("🗄️ SQL Solution", expanded=True):
            st.code(st.session_state.current_problem.sql_solution, language="sql")

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
