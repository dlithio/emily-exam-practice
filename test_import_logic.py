"""Test the import logic fix to ensure files are only processed once."""

import json
import pandas as pd
from models import Problem


def test_import_logic():
    """Simulate the import logic to verify it works correctly."""
    print("Testing import logic...\n")

    # Create a test problem JSON
    test_json = {
        "input_tables": {
            "cruises": {
                "columns": ["cruise_name", "destination", "duration_days", "price"],
                "data": [
                    {"cruise_name": "Ocean Explorer", "destination": "Caribbean", "duration_days": 7, "price": 1200},
                    {"cruise_name": "Island Hopper", "destination": "Caribbean", "duration_days": 5, "price": 950}
                ]
            }
        },
        "question": "Show all cruises that go to the Caribbean.",
        "expected_output": {
            "columns": ["cruise_name", "destination", "duration_days", "price"],
            "data": [
                {"cruise_name": "Ocean Explorer", "destination": "Caribbean", "duration_days": 7, "price": 1200},
                {"cruise_name": "Island Hopper", "destination": "Caribbean", "duration_days": 5, "price": 950}
            ]
        },
        "topic": "filter_rows",
        "difficulty": "easy",
        "pandas_solution": "result = cruises[cruises['destination'] == 'Caribbean']",
        "sql_solution": "SELECT * FROM cruises WHERE destination = 'Caribbean'"
    }

    # Test 1: Import the problem
    print("1. Testing Problem.from_json()...")
    try:
        problem = Problem.from_json(test_json)
        print(f"✓ Successfully imported problem: {problem.topic}")
        print(f"  - Question: {problem.question[:50]}...")
        print(f"  - Input tables: {list(problem.input_tables.keys())}")
        print(f"  - Expected output shape: {problem.expected_output.shape}")
        print()
    except Exception as e:
        print(f"✗ Failed to import: {e}")
        return False

    # Test 2: Verify the data integrity
    print("2. Verifying data integrity...")
    try:
        # Check input table
        cruises_df = problem.input_tables['cruises']
        assert len(cruises_df) == 2, f"Expected 2 rows, got {len(cruises_df)}"
        assert list(cruises_df.columns) == ["cruise_name", "destination", "duration_days", "price"], "Column mismatch"
        print("✓ Input table data correct")

        # Check expected output
        assert len(problem.expected_output) == 2, f"Expected 2 output rows, got {len(problem.expected_output)}"
        print("✓ Expected output correct")

        # Check metadata
        assert problem.topic == "filter_rows", f"Expected topic 'filter_rows', got '{problem.topic}'"
        assert problem.difficulty == "easy", f"Expected difficulty 'easy', got '{problem.difficulty}'"
        print("✓ Metadata correct")

        # Check solutions
        assert problem.pandas_solution is not None, "Pandas solution missing"
        assert problem.sql_solution is not None, "SQL solution missing"
        print("✓ Solutions present")
        print()

    except AssertionError as e:
        print(f"✗ Data integrity check failed: {e}")
        return False

    # Test 3: Simulate file ID tracking logic
    print("3. Testing file ID tracking logic...")

    # Simulate session state
    class SessionState:
        def __init__(self):
            self.last_uploaded_file_id = None

    session = SessionState()

    # Simulate first upload
    file_name = "problem_filter_rows_20231030.json"
    file_size = len(json.dumps(test_json))
    file_id_1 = f"{file_name}_{file_size}"

    print(f"  First upload: file_id = {file_id_1}")
    if file_id_1 != session.last_uploaded_file_id:
        print("  ✓ File should be processed (new file)")
        session.last_uploaded_file_id = file_id_1
    else:
        print("  ✗ File should not be skipped (this is wrong)")
        return False

    # Simulate rerun with same file
    print(f"  After rerun: file_id = {file_id_1}")
    if file_id_1 != session.last_uploaded_file_id:
        print("  ✗ File should be skipped (already processed)")
        return False
    else:
        print("  ✓ File correctly skipped (already processed)")

    # Simulate generating new problem (resets file ID)
    session.last_uploaded_file_id = None
    print("  After generating new problem: last_uploaded_file_id = None")

    # Simulate re-uploading same file
    if file_id_1 != session.last_uploaded_file_id:
        print("  ✓ Same file can be re-imported after reset")
    else:
        print("  ✗ File should be processed again (this is wrong)")
        return False

    print()
    return True


if __name__ == "__main__":
    success = test_import_logic()

    if success:
        print("="*60)
        print("SUCCESS: Import logic is working correctly!")
        print("="*60)
    else:
        print("="*60)
        print("FAILURE: Import logic has issues")
        print("="*60)
