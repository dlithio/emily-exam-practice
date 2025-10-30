"""Test script for execute_pandas function - Step 3.2 verification."""

import pandas as pd
from app import execute_pandas

# Create test data
employees = pd.DataFrame({
    'name': ['Alice', 'Bob', 'Charlie', 'Diana'],
    'department': ['Engineering', 'Sales', 'Engineering', 'HR'],
    'salary': [95000, 65000, 88000, 72000],
    'years': [5, 3, 7, 4]
})

input_tables = {'employees': employees}

print("="*60)
print("Testing execute_pandas() function")
print("="*60)

# Test 1: Valid code - filter by salary
print("\nTest 1: Valid code - filter employees with salary > 70000")
code1 = "result = employees[employees['salary'] > 70000]"
result_df, error = execute_pandas(code1, input_tables)

if error:
    print(f"❌ FAILED: {error}")
else:
    print("✓ SUCCESS!")
    print("Result:")
    print(result_df)

# Test 2: Valid code - filter by department
print("\n" + "="*60)
print("Test 2: Valid code - filter Engineering department")
code2 = "result = employees[employees['department'] == 'Engineering']"
result_df, error = execute_pandas(code2, input_tables)

if error:
    print(f"❌ FAILED: {error}")
else:
    print("✓ SUCCESS!")
    print("Result:")
    print(result_df)

# Test 3: Valid code - select specific columns
print("\n" + "="*60)
print("Test 3: Valid code - select name and salary columns")
code3 = "result = employees[['name', 'salary']]"
result_df, error = execute_pandas(code3, input_tables)

if error:
    print(f"❌ FAILED: {error}")
else:
    print("✓ SUCCESS!")
    print("Result:")
    print(result_df)

# Test 4: Error handling - forgot to assign to 'result'
print("\n" + "="*60)
print("Test 4: Error handling - no 'result' variable")
code4 = "output = employees[employees['salary'] > 70000]"
result_df, error = execute_pandas(code4, input_tables)

if error:
    print(f"✓ ERROR CAUGHT: {error}")
else:
    print("❌ FAILED: Should have caught missing 'result' variable")

# Test 5: Error handling - syntax error
print("\n" + "="*60)
print("Test 5: Error handling - syntax error")
code5 = "result = employees[employees['salary'] > 70000"  # Missing closing bracket
result_df, error = execute_pandas(code5, input_tables)

if error:
    print(f"✓ ERROR CAUGHT: {error}")
else:
    print("❌ FAILED: Should have caught syntax error")

# Test 6: Error handling - wrong column name
print("\n" + "="*60)
print("Test 6: Error handling - wrong column name")
code6 = "result = employees[employees['wage'] > 70000]"  # 'wage' doesn't exist
result_df, error = execute_pandas(code6, input_tables)

if error:
    print(f"✓ ERROR CAUGHT: {error}")
else:
    print("❌ FAILED: Should have caught KeyError")

# Test 7: Error handling - result is not a DataFrame
print("\n" + "="*60)
print("Test 7: Error handling - result is not a DataFrame")
code7 = "result = 42"
result_df, error = execute_pandas(code7, input_tables)

if error:
    print(f"✓ ERROR CAUGHT: {error}")
else:
    print("❌ FAILED: Should have caught non-DataFrame result")

# Test 8: Valid code - using pandas functions
print("\n" + "="*60)
print("Test 8: Valid code - using pandas groupby")
code8 = "result = employees.groupby('department')['salary'].mean().reset_index()"
result_df, error = execute_pandas(code8, input_tables)

if error:
    print(f"❌ FAILED: {error}")
else:
    print("✓ SUCCESS!")
    print("Result:")
    print(result_df)

print("\n" + "="*60)
print("All tests completed!")
print("="*60)
