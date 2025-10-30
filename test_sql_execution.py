"""Test the SQL execution functionality"""
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

print("=" * 60)
print("Test 1: Valid SQL query - Filter employees with salary > 70000")
print("=" * 60)
query1 = "SELECT * FROM employees WHERE salary > 70000"
result1, error1 = execute_sql(query1, input_tables)

if error1:
    print(f"❌ ERROR: {error1}")
else:
    print("✅ SUCCESS!")
    print(result1)
print()

print("=" * 60)
print("Test 2: Valid SQL query - Select specific columns")
print("=" * 60)
query2 = "SELECT name, salary FROM employees WHERE department = 'Engineering'"
result2, error2 = execute_sql(query2, input_tables)

if error2:
    print(f"❌ ERROR: {error2}")
else:
    print("✅ SUCCESS!")
    print(result2)
print()

print("=" * 60)
print("Test 3: Invalid SQL syntax (missing FROM)")
print("=" * 60)
query3 = "SELECT * WHERE salary > 70000"
result3, error3 = execute_sql(query3, input_tables)

if error3:
    print(f"✅ Error caught successfully: {error3}")
else:
    print(f"❌ Should have failed but got result: {result3}")
print()

print("=" * 60)
print("Test 4: Non-existent table")
print("=" * 60)
query4 = "SELECT * FROM departments"
result4, error4 = execute_sql(query4, input_tables)

if error4:
    print(f"✅ Error caught successfully: {error4}")
else:
    print(f"❌ Should have failed but got result: {result4}")
print()

print("=" * 60)
print("Test 5: Non-existent column")
print("=" * 60)
query5 = "SELECT nonexistent_column FROM employees"
result5, error5 = execute_sql(query5, input_tables)

if error5:
    print(f"✅ Error caught successfully: {error5}")
else:
    print(f"❌ Should have failed but got result: {result5}")
print()

print("=" * 60)
print("Test 6: Aggregation query")
print("=" * 60)
query6 = "SELECT department, COUNT(*) as count, AVG(salary) as avg_salary FROM employees GROUP BY department"
result6, error6 = execute_sql(query6, input_tables)

if error6:
    print(f"❌ ERROR: {error6}")
else:
    print("✅ SUCCESS!")
    print(result6)
print()

print("=" * 60)
print("All tests completed!")
print("=" * 60)
