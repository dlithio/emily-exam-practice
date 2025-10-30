"""Test edge case with incomplete SQL query"""
import pandas as pd
from app import execute_sql

# Create test data
employees = pd.DataFrame({
    'name': ['Alice', 'Bob', 'Charlie', 'Diana'],
    'department': ['Engineering', 'Sales', 'Engineering', 'HR'],
    'salary': [95000, 65000, 88000, 72000],
    'years': [5, 3, 7, 4]
})

input_tables = {'employees': employees}

print("Testing incomplete WHERE clause: 'SELECT * FROM employees WHERE salary >'")
print("=" * 60)

query = "SELECT * FROM employees WHERE salary >"
result, error = execute_sql(query, input_tables)

print(f"Result: {result}")
print(f"Error: {error}")
print()

if error:
    print("✅ Error was caught and returned")
else:
    print("❌ No error returned - this is a bug!")
