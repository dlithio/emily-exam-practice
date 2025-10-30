"""Test export/import functionality for Problem serialization."""

import pandas as pd
import json
from models import Problem


def test_export_import():
    """Test that problems can be exported to JSON and imported back correctly."""
    print("Testing Problem export/import functionality...\n")

    # Create a sample problem
    employees = pd.DataFrame({
        'name': ['Alice', 'Bob', 'Charlie', 'Diana'],
        'department': ['Engineering', 'Sales', 'Engineering', 'HR'],
        'salary': [95000, 65000, 88000, 72000],
        'years': [5, 3, 7, 4]
    })

    expected = pd.DataFrame({
        'name': ['Alice', 'Charlie'],
        'salary': [95000, 88000]
    })

    original_problem = Problem(
        input_tables={'employees': employees},
        question="Show the names and salaries of employees in the Engineering department.",
        expected_output=expected,
        topic="filter_columns",
        difficulty="easy",
        pandas_solution="result = employees[employees['department'] == 'Engineering'][['name', 'salary']]",
        sql_solution="SELECT name, salary FROM employees WHERE department = 'Engineering'"
    )

    print("1. Original problem created:")
    print(original_problem)
    print()

    # Export to JSON
    print("2. Exporting to JSON...")
    problem_json = original_problem.to_json()
    json_str = json.dumps(problem_json, indent=2)
    print(f"JSON size: {len(json_str)} characters")
    print()

    # Save to file
    filename = "test_problem_export.json"
    with open(filename, 'w') as f:
        f.write(json_str)
    print(f"3. Saved to {filename}")
    print()

    # Import from JSON
    print("4. Importing from JSON...")
    with open(filename, 'r') as f:
        loaded_json = json.load(f)

    imported_problem = Problem.from_json(loaded_json)
    print("Imported problem:")
    print(imported_problem)
    print()

    # Verify data integrity
    print("5. Verifying data integrity...")
    checks = []

    # Check metadata
    checks.append(("Topic", original_problem.topic == imported_problem.topic))
    checks.append(("Difficulty", original_problem.difficulty == imported_problem.difficulty))
    checks.append(("Question", original_problem.question == imported_problem.question))
    checks.append(("Pandas solution", original_problem.pandas_solution == imported_problem.pandas_solution))
    checks.append(("SQL solution", original_problem.sql_solution == imported_problem.sql_solution))

    # Check input tables
    checks.append(("Input tables count", len(original_problem.input_tables) == len(imported_problem.input_tables)))
    for table_name in original_problem.input_tables:
        original_df = original_problem.input_tables[table_name]
        imported_df = imported_problem.input_tables[table_name]
        try:
            pd.testing.assert_frame_equal(original_df, imported_df)
            checks.append((f"Table '{table_name}'", True))
        except AssertionError:
            checks.append((f"Table '{table_name}'", False))

    # Check expected output
    try:
        pd.testing.assert_frame_equal(original_problem.expected_output, imported_problem.expected_output)
        checks.append(("Expected output", True))
    except AssertionError:
        checks.append(("Expected output", False))

    # Display results
    all_passed = True
    for check_name, passed in checks:
        status = "✓" if passed else "✗"
        print(f"  {status} {check_name}: {'Passed' if passed else 'FAILED'}")
        if not passed:
            all_passed = False

    print()
    if all_passed:
        print("✓ All checks passed! Export/import functionality works correctly.")
        return True
    else:
        print("✗ Some checks failed. Please review the implementation.")
        return False


def test_error_handling():
    """Test error handling for invalid JSON files."""
    print("\n" + "="*60)
    print("Testing error handling...\n")

    # Test 1: Missing required field
    print("1. Testing missing required field...")
    try:
        invalid_json = {
            'question': 'Test question',
            'expected_output': {'columns': ['a'], 'data': [{'a': 1}]},
            # Missing 'input_tables' and 'topic'
        }
        Problem.from_json(invalid_json)
        print("  ✗ Should have raised ValueError")
    except ValueError as e:
        print(f"  ✓ Correctly raised ValueError: {e}")

    # Test 2: Invalid table structure
    print("\n2. Testing invalid table structure...")
    try:
        invalid_json = {
            'input_tables': {'test': {'data': []}},  # Missing 'columns'
            'question': 'Test question',
            'expected_output': {'columns': ['a'], 'data': [{'a': 1}]},
            'topic': 'test'
        }
        Problem.from_json(invalid_json)
        print("  ✗ Should have raised ValueError")
    except ValueError as e:
        print(f"  ✓ Correctly raised ValueError: {e}")

    print("\n✓ Error handling tests completed.")


if __name__ == "__main__":
    success = test_export_import()
    test_error_handling()

    if success:
        print("\n" + "="*60)
        print("SUCCESS: Export/import functionality is working correctly!")
        print("="*60)
