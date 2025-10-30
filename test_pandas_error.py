"""Test pandas error handling with full traceback"""
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

print("Testing KeyError (wrong column name)")
print("=" * 60)
code = "result = employees[employees['nonexistent_column'] > 70000]"
result, error = execute_pandas(code, input_tables)
print(f"Error:\n{error}\n")

print("Testing NameError (wrong table name)")
print("=" * 60)
code = "result = wrong_table[wrong_table['salary'] > 70000]"
result, error = execute_pandas(code, input_tables)
print(f"Error:\n{error}\n")
