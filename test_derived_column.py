"""
Comprehensive test suite for derived_column topic (Step 9.3).
Tests all three subtypes: Arithmetic, Conditional, and Date.
"""
import sys
import pandas as pd
from app import execute_pandas, execute_sql, compare_dataframes


def test_arithmetic_derivation():
    """Test arithmetic derivation in both pandas and SQL."""
    print("\n--- Testing Arithmetic Derivation ---")

    # Create test data
    input_tables = {
        "products": pd.DataFrame({
            "name": ["Widget", "Gadget", "Gizmo"],
            "price": [10.0, 25.0, 15.0],
            "quantity": [5, 3, 10]
        })
    }

    # Expected output with derived column (total = price * quantity)
    expected_output = pd.DataFrame({
        "name": ["Widget", "Gadget", "Gizmo"],
        "total": [50.0, 75.0, 150.0]
    })

    # Test pandas solution
    pandas_code = """
result = products.copy()
result['total'] = result['price'] * result['quantity']
result = result[['name', 'total']]
"""
    user_df, error = execute_pandas(pandas_code, input_tables)
    assert error is None, f"Pandas execution failed: {error}"
    is_correct, feedback = compare_dataframes(user_df, expected_output)
    assert is_correct, f"Pandas result incorrect: {feedback}"
    print("✓ Pandas arithmetic derivation works")

    # Test SQL solution
    sql_query = "SELECT name, price * quantity AS total FROM products"
    user_df, error = execute_sql(sql_query, input_tables)
    assert error is None, f"SQL execution failed: {error}"
    is_correct, feedback = compare_dataframes(user_df, expected_output)
    assert is_correct, f"SQL result incorrect: {feedback}"
    print("✓ SQL arithmetic derivation works")

    print("✅ Arithmetic derivation test passed")


def test_conditional_derivation():
    """Test conditional derivation in both pandas and SQL."""
    print("\n--- Testing Conditional Derivation ---")

    # Create test data
    input_tables = {
        "students": pd.DataFrame({
            "name": ["Alice", "Bob", "Charlie", "Diana"],
            "score": [85, 55, 92, 48]
        })
    }

    # Expected output with derived column (is_passing = score >= 60)
    expected_output = pd.DataFrame({
        "name": ["Alice", "Bob", "Charlie", "Diana"],
        "is_passing": [True, False, True, False]
    })

    # Test pandas solution
    pandas_code = """
result = students.copy()
result['is_passing'] = result['score'] >= 60
result = result[['name', 'is_passing']]
"""
    user_df, error = execute_pandas(pandas_code, input_tables)
    assert error is None, f"Pandas execution failed: {error}"
    is_correct, feedback = compare_dataframes(user_df, expected_output)
    assert is_correct, f"Pandas result incorrect: {feedback}"
    print("✓ Pandas conditional derivation works")

    # Test SQL solution (SQL uses 1/0 for boolean, need to handle comparison)
    sql_query = "SELECT name, CASE WHEN score >= 60 THEN 1 ELSE 0 END AS is_passing FROM students"
    user_df, error = execute_sql(sql_query, input_tables)
    assert error is None, f"SQL execution failed: {error}"

    # Convert SQL's 1/0 to boolean for comparison
    expected_sql = expected_output.copy()
    expected_sql['is_passing'] = expected_sql['is_passing'].astype(int)
    user_df['is_passing'] = user_df['is_passing'].astype(int)

    is_correct, feedback = compare_dataframes(user_df, expected_sql)
    assert is_correct, f"SQL result incorrect: {feedback}"
    print("✓ SQL conditional derivation works")

    print("✅ Conditional derivation test passed")


def test_conditional_categorical():
    """Test conditional derivation with categorical values."""
    print("\n--- Testing Conditional Derivation (Categorical) ---")

    # Create test data
    input_tables = {
        "employees": pd.DataFrame({
            "name": ["Alice", "Bob", "Charlie"],
            "tier": ["Gold", "Silver", "Platinum"]
        })
    }

    # Expected output with derived column (is_premium for Gold/Platinum)
    expected_output = pd.DataFrame({
        "name": ["Alice", "Bob", "Charlie"],
        "is_premium": [True, False, True]
    })

    # Test pandas solution
    pandas_code = """
result = employees.copy()
result['is_premium'] = result['tier'].isin(['Gold', 'Platinum'])
result = result[['name', 'is_premium']]
"""
    user_df, error = execute_pandas(pandas_code, input_tables)
    assert error is None, f"Pandas execution failed: {error}"
    is_correct, feedback = compare_dataframes(user_df, expected_output)
    assert is_correct, f"Pandas result incorrect: {feedback}"
    print("✓ Pandas categorical conditional works")

    # Test SQL solution
    sql_query = """
SELECT name,
    CASE WHEN tier IN ('Gold', 'Platinum') THEN 1 ELSE 0 END AS is_premium
FROM employees
"""
    user_df, error = execute_sql(sql_query, input_tables)
    assert error is None, f"SQL execution failed: {error}"

    # Convert SQL's 1/0 to boolean for comparison
    expected_sql = expected_output.copy()
    expected_sql['is_premium'] = expected_sql['is_premium'].astype(int)
    user_df['is_premium'] = user_df['is_premium'].astype(int)

    is_correct, feedback = compare_dataframes(user_df, expected_sql)
    assert is_correct, f"SQL result incorrect: {feedback}"
    print("✓ SQL categorical conditional works")

    print("✅ Categorical conditional derivation test passed")


def test_date_derivation():
    """Test date derivation in both pandas and SQL."""
    print("\n--- Testing Date Derivation ---")

    # Create test data with dates
    input_tables = {
        "events": pd.DataFrame({
            "event_name": ["Conference", "Workshop", "Seminar"],
            "event_date": ["2024-03-15", "2024-07-22", "2023-11-08"]
        })
    }

    # Expected output with derived column (year extracted from date)
    expected_output = pd.DataFrame({
        "event_name": ["Conference", "Workshop", "Seminar"],
        "year": [2024, 2024, 2023]
    })

    # Test pandas solution
    pandas_code = """
result = events.copy()
result['event_date'] = pd.to_datetime(result['event_date'])
result['year'] = result['event_date'].dt.year
result = result[['event_name', 'year']]
"""
    user_df, error = execute_pandas(pandas_code, input_tables)
    assert error is None, f"Pandas execution failed: {error}"
    is_correct, feedback = compare_dataframes(user_df, expected_output)
    assert is_correct, f"Pandas result incorrect: {feedback}"
    print("✓ Pandas date derivation works")

    # Test SQL solution using strftime
    sql_query = "SELECT event_name, CAST(strftime('%Y', event_date) AS INTEGER) AS year FROM events"
    user_df, error = execute_sql(sql_query, input_tables)
    assert error is None, f"SQL execution failed: {error}"
    is_correct, feedback = compare_dataframes(user_df, expected_output)
    assert is_correct, f"SQL result incorrect: {feedback}"
    print("✓ SQL date derivation works")

    print("✅ Date derivation test passed")


def test_date_month_derivation():
    """Test extracting month from date."""
    print("\n--- Testing Date Month Derivation ---")

    # Create test data with dates
    input_tables = {
        "orders": pd.DataFrame({
            "order_id": [1, 2, 3],
            "order_date": ["2024-01-15", "2024-03-22", "2024-12-08"]
        })
    }

    # Expected output with derived column (month extracted from date)
    expected_output = pd.DataFrame({
        "order_id": [1, 2, 3],
        "month": [1, 3, 12]
    })

    # Test pandas solution
    pandas_code = """
result = orders.copy()
result['order_date'] = pd.to_datetime(result['order_date'])
result['month'] = result['order_date'].dt.month
result = result[['order_id', 'month']]
"""
    user_df, error = execute_pandas(pandas_code, input_tables)
    assert error is None, f"Pandas execution failed: {error}"
    is_correct, feedback = compare_dataframes(user_df, expected_output)
    assert is_correct, f"Pandas result incorrect: {feedback}"
    print("✓ Pandas month extraction works")

    # Test SQL solution
    sql_query = "SELECT order_id, CAST(strftime('%m', order_date) AS INTEGER) AS month FROM orders"
    user_df, error = execute_sql(sql_query, input_tables)
    assert error is None, f"SQL execution failed: {error}"
    is_correct, feedback = compare_dataframes(user_df, expected_output)
    assert is_correct, f"SQL result incorrect: {feedback}"
    print("✓ SQL month extraction works")

    print("✅ Month derivation test passed")


def test_multiple_arithmetic_columns():
    """Test deriving from multiple columns."""
    print("\n--- Testing Multiple Column Arithmetic ---")

    # Create test data
    input_tables = {
        "scores": pd.DataFrame({
            "student": ["Alice", "Bob", "Charlie"],
            "math": [85, 90, 78],
            "english": [92, 85, 88]
        })
    }

    # Expected output with derived column (total_score = math + english)
    expected_output = pd.DataFrame({
        "student": ["Alice", "Bob", "Charlie"],
        "total_score": [177, 175, 166]
    })

    # Test pandas solution
    pandas_code = """
result = scores.copy()
result['total_score'] = result['math'] + result['english']
result = result[['student', 'total_score']]
"""
    user_df, error = execute_pandas(pandas_code, input_tables)
    assert error is None, f"Pandas execution failed: {error}"
    is_correct, feedback = compare_dataframes(user_df, expected_output)
    assert is_correct, f"Pandas result incorrect: {feedback}"
    print("✓ Pandas multi-column arithmetic works")

    # Test SQL solution
    sql_query = "SELECT student, math + english AS total_score FROM scores"
    user_df, error = execute_sql(sql_query, input_tables)
    assert error is None, f"SQL execution failed: {error}"
    is_correct, feedback = compare_dataframes(user_df, expected_output)
    assert is_correct, f"SQL result incorrect: {feedback}"
    print("✓ SQL multi-column arithmetic works")

    print("✅ Multi-column arithmetic test passed")


def run_all_tests():
    """Run all derived column tests."""
    print("\n" + "="*60)
    print("  Testing Step 9.3: Derived Column End-to-End")
    print("="*60)

    try:
        test_arithmetic_derivation()
        test_conditional_derivation()
        test_conditional_categorical()
        test_date_derivation()
        test_date_month_derivation()
        test_multiple_arithmetic_columns()

        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        print("\nDerived column functionality verified for:")
        print("  ✓ Arithmetic operations (single and multi-column)")
        print("  ✓ Conditional operations (boolean and categorical)")
        print("  ✓ Date operations (year and month extraction)")
        print("  ✓ Both pandas and SQL implementations")
        print("  ✓ DataFrame comparison works correctly")
        print("\nStep 9.3 is complete!")
        return True

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
