"""Test the compare_dataframes function with various scenarios."""

import pandas as pd
from app import compare_dataframes


def test_exact_match():
    """Test that exact matches pass."""
    print("Test 1: Exact match")
    df1 = pd.DataFrame({
        'name': ['Alice', 'Bob'],
        'age': [30, 25]
    })
    df2 = pd.DataFrame({
        'name': ['Alice', 'Bob'],
        'age': [30, 25]
    })
    is_correct, message = compare_dataframes(df1, df2)
    print(f"  Result: {is_correct}")
    print(f"  Message: {message}")
    assert is_correct == True
    print("  ✓ PASSED\n")


def test_different_values():
    """Test that different values fail with helpful message."""
    print("Test 2: Different values")
    df1 = pd.DataFrame({
        'name': ['Alice', 'Bob'],
        'age': [30, 99]  # Different value here
    })
    df2 = pd.DataFrame({
        'name': ['Alice', 'Bob'],
        'age': [30, 25]
    })
    is_correct, message = compare_dataframes(df1, df2)
    print(f"  Result: {is_correct}")
    print(f"  Message: {message}")
    assert is_correct == False
    assert "age" in message.lower() or "values" in message.lower()
    print("  ✓ PASSED\n")


def test_wrong_columns():
    """Test that wrong columns fail with helpful message."""
    print("Test 3: Wrong columns (missing column)")
    df1 = pd.DataFrame({
        'name': ['Alice', 'Bob']
        # Missing 'age' column
    })
    df2 = pd.DataFrame({
        'name': ['Alice', 'Bob'],
        'age': [30, 25]
    })
    is_correct, message = compare_dataframes(df1, df2)
    print(f"  Result: {is_correct}")
    print(f"  Message: {message}")
    assert is_correct == False
    assert "column" in message.lower()
    print("  ✓ PASSED\n")


def test_extra_columns():
    """Test that extra columns fail with helpful message."""
    print("Test 4: Wrong columns (extra column)")
    df1 = pd.DataFrame({
        'name': ['Alice', 'Bob'],
        'age': [30, 25],
        'city': ['NYC', 'LA']  # Extra column
    })
    df2 = pd.DataFrame({
        'name': ['Alice', 'Bob'],
        'age': [30, 25]
    })
    is_correct, message = compare_dataframes(df1, df2)
    print(f"  Result: {is_correct}")
    print(f"  Message: {message}")
    assert is_correct == False
    assert "column" in message.lower()
    print("  ✓ PASSED\n")


def test_different_order():
    """Test that same data in different row order fails."""
    print("Test 5: Same data, different row order (should fail)")
    df1 = pd.DataFrame({
        'name': ['Bob', 'Alice'],  # Reversed order
        'age': [25, 30]
    })
    df2 = pd.DataFrame({
        'name': ['Alice', 'Bob'],
        'age': [30, 25]
    })
    is_correct, message = compare_dataframes(df1, df2)
    print(f"  Result: {is_correct}")
    print(f"  Message: {message}")
    assert is_correct == False
    assert "values" in message.lower() or "don't match" in message.lower()
    print("  ✓ PASSED\n")


def test_different_column_order():
    """Test that same data with different column order fails."""
    print("Test 6: Same data, different column order (should fail)")
    df1 = pd.DataFrame({
        'age': [30, 25],  # Columns in different order
        'name': ['Alice', 'Bob']
    })
    df2 = pd.DataFrame({
        'name': ['Alice', 'Bob'],
        'age': [30, 25]
    })
    is_correct, message = compare_dataframes(df1, df2)
    print(f"  Result: {is_correct}")
    print(f"  Message: {message}")
    assert is_correct == False
    assert "column order" in message.lower()
    print("  ✓ PASSED\n")


def test_wrong_type():
    """Test that non-DataFrame input fails with helpful message."""
    print("Test 7: Non-DataFrame input")
    df1 = [1, 2, 3]  # Not a DataFrame
    df2 = pd.DataFrame({
        'name': ['Alice', 'Bob'],
        'age': [30, 25]
    })
    is_correct, message = compare_dataframes(df1, df2)
    print(f"  Result: {is_correct}")
    print(f"  Message: {message}")
    assert is_correct == False
    assert "list" in message.lower()
    print("  ✓ PASSED\n")


def test_wrong_shape():
    """Test that different shapes fail with helpful message."""
    print("Test 8: Different shape")
    df1 = pd.DataFrame({
        'name': ['Alice', 'Bob', 'Charlie'],  # 3 rows instead of 2
        'age': [30, 25, 35]
    })
    df2 = pd.DataFrame({
        'name': ['Alice', 'Bob'],
        'age': [30, 25]
    })
    is_correct, message = compare_dataframes(df1, df2)
    print(f"  Result: {is_correct}")
    print(f"  Message: {message}")
    assert is_correct == False
    assert "shape" in message.lower()
    print("  ✓ PASSED\n")


def test_float_comparison():
    """Test that close float values pass (within tolerance)."""
    print("Test 9: Close float values")
    df1 = pd.DataFrame({
        'value': [1.0000001, 2.0]  # Very close to 1.0
    })
    df2 = pd.DataFrame({
        'value': [1.0, 2.0]
    })
    is_correct, message = compare_dataframes(df1, df2)
    print(f"  Result: {is_correct}")
    print(f"  Message: {message}")
    assert is_correct == True
    print("  ✓ PASSED\n")


def test_int_float_equivalence():
    """Test that int and float with same values are treated as equivalent."""
    print("Test 10: Int vs Float equivalence")
    df1 = pd.DataFrame({
        'value': [1, 2, 3]  # int
    })
    df2 = pd.DataFrame({
        'value': [1.0, 2.0, 3.0]  # float
    })
    is_correct, message = compare_dataframes(df1, df2)
    print(f"  Result: {is_correct}")
    print(f"  Message: {message}")
    assert is_correct == True
    print("  ✓ PASSED\n")


if __name__ == "__main__":
    print("=" * 60)
    print("Testing compare_dataframes function")
    print("=" * 60 + "\n")

    try:
        test_exact_match()
        test_different_values()
        test_wrong_columns()
        test_extra_columns()
        test_different_order()
        test_different_column_order()
        test_wrong_type()
        test_wrong_shape()
        test_float_comparison()
        test_int_float_equivalence()

        print("=" * 60)
        print("All tests passed! ✓")
        print("=" * 60)
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
