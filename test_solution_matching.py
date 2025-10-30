"""
Test that pandas and SQL solutions are verified to match during problem generation.

This test file uses fake Claude responses to test various scenarios:
1. Both solutions work and match (should succeed)
2. Both solutions work but don't match (should fail with error)
3. Pandas solution fails (should fail with error)
4. SQL solution fails (should fail with error)
5. Solutions produce empty results (should fail with error)
"""
import json
import pandas as pd
from unittest.mock import patch, MagicMock
from claude_client import generate_problem


def test_matching_solutions():
    """Test that problem generation succeeds when pandas and SQL solutions match."""
    print("\n" + "="*80)
    print("TEST 1: Matching Solutions (Should Succeed)")
    print("="*80)

    fake_response = {
        "input_tables": {
            "employees": {
                "columns": ["name", "department", "salary"],
                "data": [
                    ["Alice", "Engineering", 95000],
                    ["Bob", "Sales", 65000],
                    ["Charlie", "Engineering", 88000]
                ]
            }
        },
        "question": "Show all employees in the Engineering department.",
        "topic": "filter_rows",
        "difficulty": "easy",
        "pandas_solution": "result = employees[employees['department'] == 'Engineering']",
        "sql_solution": "SELECT * FROM employees WHERE department = 'Engineering'"
    }

    # Mock the API call
    with patch('claude_client.get_client') as mock_client:
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=json.dumps(fake_response))]
        mock_client.return_value.messages.create.return_value = mock_response

        try:
            problem = generate_problem(difficulty="easy", use_cache=False)
            print("✓ Problem generated successfully")
            print(f"  Expected output shape: {problem.expected_output.shape}")
            print(f"  Expected output:\n{problem.expected_output}")
            print("✓ TEST PASSED: Solutions matched and problem was created")
            return True
        except Exception as e:
            print(f"✗ TEST FAILED: {e}")
            return False


def test_mismatching_solutions():
    """Test that problem generation fails when pandas and SQL solutions don't match."""
    print("\n" + "="*80)
    print("TEST 2: Mismatching Solutions (Should Fail)")
    print("="*80)

    fake_response = {
        "input_tables": {
            "employees": {
                "columns": ["name", "department", "salary"],
                "data": [
                    ["Alice", "Engineering", 95000],
                    ["Bob", "Sales", 65000],
                    ["Charlie", "Engineering", 88000]
                ]
            }
        },
        "question": "Show all employees in the Engineering department.",
        "topic": "filter_rows",
        "difficulty": "easy",
        # Pandas solution filters for Engineering
        "pandas_solution": "result = employees[employees['department'] == 'Engineering']",
        # SQL solution filters for Sales (INTENTIONALLY WRONG - should cause mismatch)
        "sql_solution": "SELECT * FROM employees WHERE department = 'Sales'"
    }

    # Mock the API call
    with patch('claude_client.get_client') as mock_client:
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=json.dumps(fake_response))]
        mock_client.return_value.messages.create.return_value = mock_response

        try:
            problem = generate_problem(difficulty="easy", use_cache=False)
            print(f"✗ TEST FAILED: Problem was generated despite solutions not matching")
            print(f"  This should have raised a ValueError")
            return False
        except ValueError as e:
            error_msg = str(e)
            if "different results" in error_msg.lower():
                print(f"✓ TEST PASSED: Correctly detected mismatch")
                print(f"  Error message: {error_msg[:200]}...")
                return True
            else:
                print(f"✗ TEST FAILED: Wrong error message: {error_msg}")
                return False
        except Exception as e:
            print(f"✗ TEST FAILED: Wrong exception type: {type(e).__name__}: {e}")
            return False


def test_pandas_solution_fails():
    """Test that problem generation fails when pandas solution fails to execute."""
    print("\n" + "="*80)
    print("TEST 3: Pandas Solution Fails (Should Fail)")
    print("="*80)

    fake_response = {
        "input_tables": {
            "employees": {
                "columns": ["name", "department", "salary"],
                "data": [
                    ["Alice", "Engineering", 95000],
                    ["Bob", "Sales", 65000],
                    ["Charlie", "Engineering", 88000]
                ]
            }
        },
        "question": "Show all employees in the Engineering department.",
        "topic": "filter_rows",
        "difficulty": "easy",
        # Pandas solution has a syntax error (INTENTIONALLY WRONG)
        "pandas_solution": "result = employees[employees['department'] == 'Engineering'",  # Missing closing bracket
        "sql_solution": "SELECT * FROM employees WHERE department = 'Engineering'"
    }

    # Mock the API call
    with patch('claude_client.get_client') as mock_client:
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=json.dumps(fake_response))]
        mock_client.return_value.messages.create.return_value = mock_response

        try:
            problem = generate_problem(difficulty="easy", use_cache=False)
            print(f"✗ TEST FAILED: Problem was generated despite pandas solution failing")
            return False
        except ValueError as e:
            error_msg = str(e)
            if "pandas solution failed" in error_msg.lower():
                print(f"✓ TEST PASSED: Correctly detected pandas failure")
                print(f"  Error message: {error_msg[:200]}...")
                return True
            else:
                print(f"✗ TEST FAILED: Wrong error message: {error_msg}")
                return False
        except Exception as e:
            print(f"✗ TEST FAILED: Wrong exception type: {type(e).__name__}: {e}")
            return False


def test_sql_solution_fails():
    """Test that problem generation fails when SQL solution fails to execute."""
    print("\n" + "="*80)
    print("TEST 4: SQL Solution Fails (Should Fail)")
    print("="*80)

    fake_response = {
        "input_tables": {
            "employees": {
                "columns": ["name", "department", "salary"],
                "data": [
                    ["Alice", "Engineering", 95000],
                    ["Bob", "Sales", 65000],
                    ["Charlie", "Engineering", 88000]
                ]
            }
        },
        "question": "Show all employees in the Engineering department.",
        "topic": "filter_rows",
        "difficulty": "easy",
        "pandas_solution": "result = employees[employees['department'] == 'Engineering']",
        # SQL solution has a syntax error (INTENTIONALLY WRONG)
        "sql_solution": "SELECT * FROM employees WHERE department = 'Engineering"  # Missing closing quote
    }

    # Mock the API call
    with patch('claude_client.get_client') as mock_client:
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=json.dumps(fake_response))]
        mock_client.return_value.messages.create.return_value = mock_response

        try:
            problem = generate_problem(difficulty="easy", use_cache=False)
            print(f"✗ TEST FAILED: Problem was generated despite SQL solution failing")
            return False
        except ValueError as e:
            error_msg = str(e)
            if "sql solution failed" in error_msg.lower():
                print(f"✓ TEST PASSED: Correctly detected SQL failure")
                print(f"  Error message: {error_msg[:200]}...")
                return True
            else:
                print(f"✗ TEST FAILED: Wrong error message: {error_msg}")
                return False
        except Exception as e:
            print(f"✗ TEST FAILED: Wrong exception type: {type(e).__name__}: {e}")
            return False


def test_empty_pandas_result():
    """Test that problem generation fails when pandas solution produces empty result."""
    print("\n" + "="*80)
    print("TEST 5: Empty Pandas Result (Should Fail)")
    print("="*80)

    fake_response = {
        "input_tables": {
            "employees": {
                "columns": ["name", "department", "salary"],
                "data": [
                    ["Alice", "Engineering", 95000],
                    ["Bob", "Sales", 65000],
                    ["Charlie", "Engineering", 88000]
                ]
            }
        },
        "question": "Show all employees in a department that doesn't exist.",
        "topic": "filter_rows",
        "difficulty": "easy",
        # Pandas solution filters for non-existent department (produces empty result)
        "pandas_solution": "result = employees[employees['department'] == 'NonExistentDept']",
        "sql_solution": "SELECT * FROM employees WHERE department = 'NonExistentDept'"
    }

    # Mock the API call
    with patch('claude_client.get_client') as mock_client:
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=json.dumps(fake_response))]
        mock_client.return_value.messages.create.return_value = mock_response

        try:
            problem = generate_problem(difficulty="easy", use_cache=False)
            print(f"✗ TEST FAILED: Problem was generated despite producing empty result")
            return False
        except ValueError as e:
            error_msg = str(e)
            if "no output" in error_msg.lower() or "empty" in error_msg.lower():
                print(f"✓ TEST PASSED: Correctly detected empty result")
                print(f"  Error message: {error_msg[:200]}...")
                return True
            else:
                print(f"✗ TEST FAILED: Wrong error message: {error_msg}")
                return False
        except Exception as e:
            print(f"✗ TEST FAILED: Wrong exception type: {type(e).__name__}: {e}")
            return False


def test_column_order_mismatch():
    """Test that problem generation fails when pandas and SQL return different column orders."""
    print("\n" + "="*80)
    print("TEST 6: Column Order Mismatch (Should Fail)")
    print("="*80)

    fake_response = {
        "input_tables": {
            "employees": {
                "columns": ["name", "department", "salary"],
                "data": [
                    ["Alice", "Engineering", 95000],
                    ["Bob", "Sales", 65000],
                    ["Charlie", "Engineering", 88000]
                ]
            }
        },
        "question": "Show name and salary of Engineering employees.",
        "topic": "filter_columns",
        "difficulty": "easy",
        # Pandas returns columns in order: name, salary
        "pandas_solution": "result = employees[employees['department'] == 'Engineering'][['name', 'salary']]",
        # SQL returns columns in DIFFERENT order: salary, name (INTENTIONALLY WRONG)
        "sql_solution": "SELECT salary, name FROM employees WHERE department = 'Engineering'"
    }

    # Mock the API call
    with patch('claude_client.get_client') as mock_client:
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=json.dumps(fake_response))]
        mock_client.return_value.messages.create.return_value = mock_response

        try:
            problem = generate_problem(difficulty="easy", use_cache=False)
            print(f"✗ TEST FAILED: Problem was generated despite column order mismatch")
            return False
        except ValueError as e:
            error_msg = str(e)
            if "different results" in error_msg.lower() or "mismatch" in error_msg.lower():
                print(f"✓ TEST PASSED: Correctly detected column order mismatch")
                print(f"  Error message: {error_msg[:200]}...")
                return True
            else:
                print(f"✗ TEST FAILED: Wrong error message: {error_msg}")
                return False
        except Exception as e:
            print(f"✗ TEST FAILED: Wrong exception type: {type(e).__name__}: {e}")
            return False


def test_row_order_mismatch():
    """Test that problem generation fails when pandas and SQL return different row orders."""
    print("\n" + "="*80)
    print("TEST 7: Row Order Mismatch (Should Fail)")
    print("="*80)

    fake_response = {
        "input_tables": {
            "employees": {
                "columns": ["name", "department", "salary"],
                "data": [
                    ["Alice", "Engineering", 95000],
                    ["Bob", "Sales", 65000],
                    ["Charlie", "Engineering", 88000]
                ]
            }
        },
        "question": "Show Engineering employees sorted by salary.",
        "topic": "order_by",
        "difficulty": "easy",
        # Pandas sorts ascending
        "pandas_solution": "result = employees[employees['department'] == 'Engineering'].sort_values('salary')",
        # SQL sorts DESCENDING (INTENTIONALLY WRONG)
        "sql_solution": "SELECT * FROM employees WHERE department = 'Engineering' ORDER BY salary DESC"
    }

    # Mock the API call
    with patch('claude_client.get_client') as mock_client:
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=json.dumps(fake_response))]
        mock_client.return_value.messages.create.return_value = mock_response

        try:
            problem = generate_problem(difficulty="easy", use_cache=False)
            print(f"✗ TEST FAILED: Problem was generated despite row order mismatch")
            return False
        except ValueError as e:
            error_msg = str(e)
            if "different results" in error_msg.lower() or "mismatch" in error_msg.lower():
                print(f"✓ TEST PASSED: Correctly detected row order mismatch")
                print(f"  Error message: {error_msg[:200]}...")
                return True
            else:
                print(f"✗ TEST FAILED: Wrong error message: {error_msg}")
                return False
        except Exception as e:
            print(f"✗ TEST FAILED: Wrong exception type: {type(e).__name__}: {e}")
            return False


if __name__ == "__main__":
    print("\n" + "#"*80)
    print("# COMPREHENSIVE SOLUTION MATCHING TESTS")
    print("#"*80)
    print("\nThese tests verify that pandas and SQL solutions are validated during problem generation.")
    print("Each test uses a fake Claude response to simulate different scenarios.\n")

    tests = [
        ("Matching Solutions", test_matching_solutions),
        ("Mismatching Solutions", test_mismatching_solutions),
        ("Pandas Solution Fails", test_pandas_solution_fails),
        ("SQL Solution Fails", test_sql_solution_fails),
        ("Empty Pandas Result", test_empty_pandas_result),
        ("Column Order Mismatch", test_column_order_mismatch),
        ("Row Order Mismatch", test_row_order_mismatch),
    ]

    results = []
    for name, test_func in tests:
        passed = test_func()
        results.append((name, passed))

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    total = len(results)
    passed = sum(1 for _, p in results if p)
    failed = total - passed

    for name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{status}: {name}")

    print("\n" + "-"*80)
    print(f"Total: {total} tests | Passed: {passed} | Failed: {failed}")

    if failed == 0:
        print("="*80)
        print("🎉 ALL TESTS PASSED! Solution matching verification is working correctly.")
        print("="*80)
    else:
        print("="*80)
        print("⚠️  SOME TESTS FAILED! Review the output above for details.")
        print("="*80)
