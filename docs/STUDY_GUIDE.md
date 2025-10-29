# Exam Study Guide


# Reference Tables



<table>
<tr><td style="padding-right: 40px;">

**Employees**

| emp_id | name | dept_id | salary | city |
| --- | --- | --- | --- | --- |
| 1 | Alice | 10 | 70000 | NYC |
| 2 | Bob | 20 | 80000 | LA |
| 3 | Charlie | 10 | 75000 | NYC |
| 4 | David | 30 | 65000 | Chicago |
| 5 | Eve | 20 | 90000 | LA |
| 6 | Frank | 10 | 72000 | NYC |

</td><td>

**Departments**

| dept_id | dept_name |
| --- | --- |
| 10 | Sales |
| 20 | Engineering |
| 30 | HR |
| 40 | Marketing |

</td></tr>
</table>



**Managers**

| manager_id | manager_name |
| --- | --- |
| 1 | Alice |
| 2 | Bob |


# Foundational Content


## 1. Filter Columns


```python
# Pandas: Select specific columns
pandas_result = employees[['name', 'salary']]

# SQL: SELECT specific columns
sql_result = pd.read_sql("SELECT name, salary FROM employees", conn)
```


<table>
<tr><td style="padding-right: 40px;">

**Input: Employees**

| emp_id | name | dept_id | salary | city |
| --- | --- | --- | --- | --- |
| 1 | Alice | 10 | 70000 | NYC |
| 2 | Bob | 20 | 80000 | LA |
| 3 | Charlie | 10 | 75000 | NYC |
| 4 | David | 30 | 65000 | Chicago |
| 5 | Eve | 20 | 90000 | LA |
| 6 | Frank | 10 | 72000 | NYC |

</td><td>

**Output: Selected Columns**

| name | salary |
| --- | --- |
| Alice | 70000 |
| Bob | 80000 |
| Charlie | 75000 |
| David | 65000 |
| Eve | 90000 |
| Frank | 72000 |

</td></tr>
</table>


## 2. Filter Rows


```python
# Pandas: Filter rows with condition
pandas_result = employees[employees['salary'] > 70000]

# SQL: WHERE clause
sql_result = pd.read_sql("SELECT * FROM employees WHERE salary > 70000", conn)
```


<table>
<tr><td style="padding-right: 40px;">

**Input: Employees**

| emp_id | name | dept_id | salary | city |
| --- | --- | --- | --- | --- |
| 1 | Alice | 10 | 70000 | NYC |
| 2 | Bob | 20 | 80000 | LA |
| 3 | Charlie | 10 | 75000 | NYC |
| 4 | David | 30 | 65000 | Chicago |
| 5 | Eve | 20 | 90000 | LA |
| 6 | Frank | 10 | 72000 | NYC |

</td><td>

**Output: Filtered Rows (salary > 70000)**

| emp_id | name | dept_id | salary | city |
| --- | --- | --- | --- | --- |
| 2 | Bob | 20 | 80000 | LA |
| 3 | Charlie | 10 | 75000 | NYC |
| 5 | Eve | 20 | 90000 | LA |
| 6 | Frank | 10 | 72000 | NYC |

</td></tr>
</table>


## 3a. Summarize Rows (GROUP BY + Aggregation)


```python
# Pandas: Group by and aggregate
pandas_result = employees.groupby('dept_id')['salary'].agg(['mean', 'count']).reset_index()
pandas_result.columns = ['dept_id', 'avg_salary', 'count']

# SQL: GROUP BY with aggregations
sql_result = pd.read_sql("""
    SELECT dept_id, AVG(salary) as avg_salary, COUNT(*) as count
    FROM employees
    GROUP BY dept_id
""", conn)
```


<table>
<tr><td style="padding-right: 40px;">

**Input: Employees**

| emp_id | name | dept_id | salary | city |
| --- | --- | --- | --- | --- |
| 1 | Alice | 10 | 70000 | NYC |
| 2 | Bob | 20 | 80000 | LA |
| 3 | Charlie | 10 | 75000 | NYC |
| 4 | David | 30 | 65000 | Chicago |
| 5 | Eve | 20 | 90000 | LA |
| 6 | Frank | 10 | 72000 | NYC |

</td><td>

**Output: Grouped by dept_id**

| dept_id | avg_salary | count |
| --- | --- | --- |
| 10.0 | 72333.33333333333 | 3.0 |
| 20.0 | 85000.0 | 2.0 |
| 30.0 | 65000.0 | 1.0 |

</td></tr>
</table>


## 3b. Select Distinct


```python
# Pandas: Get unique values
pandas_result = employees[['city']].drop_duplicates().reset_index(drop=True)

# SQL: DISTINCT
sql_result = pd.read_sql("SELECT DISTINCT city FROM employees", conn)
```


<table>
<tr><td style="padding-right: 40px;">

**Input: Employees**

| emp_id | name | dept_id | salary | city |
| --- | --- | --- | --- | --- |
| 1 | Alice | 10 | 70000 | NYC |
| 2 | Bob | 20 | 80000 | LA |
| 3 | Charlie | 10 | 75000 | NYC |
| 4 | David | 30 | 65000 | Chicago |
| 5 | Eve | 20 | 90000 | LA |
| 6 | Frank | 10 | 72000 | NYC |

</td><td>

**Output: Distinct Cities**

| city |
| --- |
| NYC |
| LA |
| Chicago |

</td></tr>
</table>


## 4. Join (Inner, Left, Outer)



### Join Input Tables


<table>
<tr><td style="padding-right: 40px;">

**Employees**

| emp_id | name | dept_id | salary | city |
| --- | --- | --- | --- | --- |
| 1 | Alice | 10 | 70000 | NYC |
| 2 | Bob | 20 | 80000 | LA |
| 3 | Charlie | 10 | 75000 | NYC |
| 4 | David | 30 | 65000 | Chicago |
| 5 | Eve | 20 | 90000 | LA |
| 6 | Frank | 10 | 72000 | NYC |

</td><td>

**Departments**

| dept_id | dept_name |
| --- | --- |
| 10 | Sales |
| 20 | Engineering |
| 30 | HR |
| 40 | Marketing |

</td></tr>
</table>


```python
# Pandas: Inner join
pandas_inner = employees.merge(departments, on='dept_id', how='inner')[['name', 'dept_name', 'salary']]

# SQL: Inner join
sql_inner = pd.read_sql("""
    SELECT e.name, d.dept_name, e.salary
    FROM employees e
    INNER JOIN departments d ON e.dept_id = d.dept_id
""", conn)
```


### INNER JOIN


**Result**

| name | dept_name | salary |
| --- | --- | --- |
| Alice | Sales | 70000 |
| Bob | Engineering | 80000 |
| Charlie | Sales | 75000 |
| David | HR | 65000 |
| Eve | Engineering | 90000 |
| Frank | Sales | 72000 |


```python
# Pandas: Left join
pandas_left = employees.merge(departments, on='dept_id', how='left')[['name', 'dept_name', 'salary']]

# SQL: Left join
sql_left = pd.read_sql("""
    SELECT e.name, d.dept_name, e.salary
    FROM employees e
    LEFT JOIN departments d ON e.dept_id = d.dept_id
""", conn)
```


### LEFT JOIN


**Result**

| name | dept_name | salary |
| --- | --- | --- |
| Alice | Sales | 70000 |
| Bob | Engineering | 80000 |
| Charlie | Sales | 75000 |
| David | HR | 65000 |
| Eve | Engineering | 90000 |
| Frank | Sales | 72000 |


```python
# Pandas: Outer join
pandas_outer = departments.merge(employees, on='dept_id', how='outer')[['dept_name', 'name', 'salary']]

# SQL: Outer join (FULL OUTER JOIN via UNION)
sql_outer = pd.read_sql("""
    SELECT d.dept_name, e.name, e.salary
    FROM employees e
    LEFT JOIN departments d ON e.dept_id = d.dept_id
    UNION
    SELECT d.dept_name, e.name, e.salary
    FROM departments d
    LEFT JOIN employees e ON e.dept_id = d.dept_id
""", conn)
```


### OUTER JOIN


**Result**

| dept_name | name | salary |
| --- | --- | --- |
| Sales | Alice | 70000.0 |
| Sales | Charlie | 75000.0 |
| Sales | Frank | 72000.0 |
| Engineering | Bob | 80000.0 |
| Engineering | Eve | 90000.0 |
| HR | David | 65000.0 |
| Marketing | nan | nan |


## 5. Order By


```python
# Pandas: Sort values
pandas_result = employees.sort_values('salary', ascending=False)[['name', 'salary']]

# SQL: ORDER BY
sql_result = pd.read_sql("""
    SELECT name, salary
    FROM employees
    ORDER BY salary DESC
""", conn)
```


<table>
<tr><td style="padding-right: 40px;">

**Input: Employees**

| emp_id | name | dept_id | salary | city |
| --- | --- | --- | --- | --- |
| 1 | Alice | 10 | 70000 | NYC |
| 2 | Bob | 20 | 80000 | LA |
| 3 | Charlie | 10 | 75000 | NYC |
| 4 | David | 30 | 65000 | Chicago |
| 5 | Eve | 20 | 90000 | LA |
| 6 | Frank | 10 | 72000 | NYC |

</td><td>

**Output: Ordered by Salary DESC**

| name | salary |
| --- | --- |
| Eve | 90000 |
| Bob | 80000 |
| Charlie | 75000 |
| Frank | 72000 |
| Alice | 70000 |
| David | 65000 |

</td></tr>
</table>


## 6. Limit


```python
# Pandas: Limit rows with head()
pandas_result = employees.sort_values('salary', ascending=False).head(3)[['name', 'salary']]

# SQL: LIMIT
sql_result = pd.read_sql("""
    SELECT name, salary
    FROM employees
    ORDER BY salary DESC
    LIMIT 3
""", conn)
```


<table>
<tr><td style="padding-right: 40px;">

**Input: Employees**

| emp_id | name | dept_id | salary | city |
| --- | --- | --- | --- | --- |
| 1 | Alice | 10 | 70000 | NYC |
| 2 | Bob | 20 | 80000 | LA |
| 3 | Charlie | 10 | 75000 | NYC |
| 4 | David | 30 | 65000 | Chicago |
| 5 | Eve | 20 | 90000 | LA |
| 6 | Frank | 10 | 72000 | NYC |

</td><td>

**Output: Top 3 by Salary**

| name | salary |
| --- | --- |
| Eve | 90000 |
| Bob | 80000 |
| Charlie | 75000 |

</td></tr>
</table>


# Advanced Content


## 7. Identifying and Changing Datatypes


```python
# Pandas: Check and change dtypes
print("Original dtypes:")
print(employees.dtypes)
print()

# Convert salary to float and emp_id to string
employees_converted = employees.copy()
employees_converted['salary'] = employees_converted['salary'].astype(float)
employees_converted['emp_id'] = employees_converted['emp_id'].astype(str)

print("After Pandas conversion:")
print(employees_converted.dtypes)
print()

# SQL: Convert datatypes using CAST
sql_result = pd.read_sql("""
    SELECT
        CAST(emp_id AS TEXT) as emp_id,
        name,
        dept_id,
        CAST(salary AS REAL) as salary,
        city
    FROM employees
""", conn)

print("After SQL CAST:")
print(sql_result.dtypes)
```

    Original dtypes:
    emp_id      int64
    name       object
    dept_id     int64
    salary      int64
    city       object
    dtype: object
    
    After Pandas conversion:
    emp_id      object
    name        object
    dept_id      int64
    salary     float64
    city        object
    dtype: object
    
    After SQL CAST:
    emp_id      object
    name        object
    dept_id      int64
    salary     float64
    city        object
    dtype: object


## 8. CTEs (SQL Only)


```python
# SQL: Common Table Expression
sql_result = pd.read_sql("""
    WITH high_earners AS (
        SELECT * FROM employees WHERE salary > 70000
    )
    SELECT name, salary, city
    FROM high_earners
    ORDER BY salary DESC
""", conn)
```


<table>
<tr><td style="padding-right: 40px;">

**Input: Employees**

| emp_id | name | dept_id | salary | city |
| --- | --- | --- | --- | --- |
| 1 | Alice | 10 | 70000 | NYC |
| 2 | Bob | 20 | 80000 | LA |
| 3 | Charlie | 10 | 75000 | NYC |
| 4 | David | 30 | 65000 | Chicago |
| 5 | Eve | 20 | 90000 | LA |
| 6 | Frank | 10 | 72000 | NYC |

</td><td>

**Output: High Earners (salary > 70000)**

| name | salary | city |
| --- | --- | --- |
| Eve | 90000 | LA |
| Bob | 80000 | LA |
| Charlie | 75000 | NYC |
| Frank | 72000 | NYC |

</td></tr>
</table>


## 9. Cross Joins



### Cross Join Input Tables


<table>
<tr><td style="padding-right: 40px;">

**Managers**

| manager_id | manager_name |
| --- | --- |
| 1 | Alice |
| 2 | Bob |

</td><td>

**Departments**

| dept_id | dept_name |
| --- | --- |
| 10 | Sales |
| 20 | Engineering |
| 30 | HR |
| 40 | Marketing |

</td></tr>
</table>


```python
# Pandas: Cross join using merge with how='cross'
pandas_result = managers[['manager_name']].merge(departments[['dept_name']], how='cross')

# SQL: Cross join
sql_result = pd.read_sql("""
    SELECT m.manager_name, d.dept_name
    FROM managers m
    CROSS JOIN departments d
""", conn)
```


**Result**

| manager_name | dept_name |
| --- | --- |
| Alice | Sales |
| Alice | Engineering |
| Alice | HR |
| Alice | Marketing |
| Bob | Sales |
| Bob | Engineering |
| Bob | HR |
| Bob | Marketing |


## 10a. Create Pandas DataFrame from List of Dicts


```python
# List of dictionaries to DataFrame
data = [
    {'name': 'Alice', 'age': 25, 'city': 'NYC'},
    {'name': 'Bob', 'age': 30, 'city': 'LA'},
    {'name': 'Charlie', 'age': 35}  # Missing 'city'
]
result_list_of_dicts = pd.DataFrame(data)
```


**Result**

| name | age | city |
| --- | --- | --- |
| Alice | 25 | NYC |
| Bob | 30 | LA |
| Charlie | 35 | nan |


## 10b. Create Pandas DataFrame from Dict of Lists


```python
# Dictionary of lists to DataFrame
data = {
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 30, 35],
    'city': ['NYC', 'LA', 'Chicago']
}
result_dict_of_lists = pd.DataFrame(data)
```


**Result**

| name | age | city |
| --- | --- | --- |
| Alice | 25 | NYC |
| Bob | 30 | LA |
| Charlie | 35 | Chicago |


## 11. Wide vs. Long Tables


```python
# Wide table: Multiple columns for related data (one row per subject)
wide_table = pd.DataFrame({
    'student': ['Alice', 'Bob', 'Charlie'],
    'math_score': [85, 92, 78],
    'english_score': [88, 85, 90],
    'science_score': [92, 88, 85]
})

# Long table: Single column for values, repeated rows per subject
long_table = pd.DataFrame({
    'student': ['Alice', 'Alice', 'Alice', 'Bob', 'Bob', 'Bob', 'Charlie', 'Charlie', 'Charlie'],
    'subject': ['math', 'english', 'science', 'math', 'english', 'science', 'math', 'english', 'science'],
    'score': [85, 88, 92, 92, 85, 88, 78, 90, 85]
})
```


<table>
<tr><td style="padding-right: 40px;">

**Wide Table (one row per student)**

| student | math_score | english_score | science_score |
| --- | --- | --- | --- |
| Alice | 85 | 88 | 92 |
| Bob | 92 | 85 | 88 |
| Charlie | 78 | 90 | 85 |

</td><td>

**Long Table (one row per score)**

| student | subject | score |
| --- | --- | --- |
| Alice | math | 85 |
| Alice | english | 88 |
| Alice | science | 92 |
| Bob | math | 92 |
| Bob | english | 85 |
| Bob | science | 88 |
| Charlie | math | 78 |
| Charlie | english | 90 |
| Charlie | science | 85 |

</td></tr>
</table>


## 12. Pivot (Pandas Only)


```python
# Pandas: Pivot from long to wide format
pivoted = long_table.pivot(index='student', columns='subject', values='score')
pivoted = pivoted.reset_index()  # Make student a regular column
```


<table>
<tr><td style="padding-right: 40px;">

**Input: Long Table**

| student | subject | score |
| --- | --- | --- |
| Alice | math | 85 |
| Alice | english | 88 |
| Alice | science | 92 |
| Bob | math | 92 |
| Bob | english | 85 |
| Bob | science | 88 |
| Charlie | math | 78 |
| Charlie | english | 90 |
| Charlie | science | 85 |

</td><td>

**Output: Wide Table**

| student | english | math | science |
| --- | --- | --- | --- |
| Alice | 88 | 85 | 92 |
| Bob | 85 | 92 | 88 |
| Charlie | 90 | 78 | 85 |

</td></tr>
</table>


## 13. Melt (Pandas Only)


```python
# Pandas: Melt from wide to long format
melted = wide_table.melt(id_vars=['student'], var_name='subject', value_name='score')
# Clean up the subject names (remove '_score' suffix)
melted['subject'] = melted['subject'].str.replace('_score', '')
melted = melted.sort_values(['student', 'subject']).reset_index(drop=True)
```


<table>
<tr><td style="padding-right: 40px;">

**Input: Wide Table**

| student | math_score | english_score | science_score |
| --- | --- | --- | --- |
| Alice | 85 | 88 | 92 |
| Bob | 92 | 85 | 88 |
| Charlie | 78 | 90 | 85 |

</td><td>

**Output: Long Table**

| student | subject | score |
| --- | --- | --- |
| Alice | english | 88 |
| Alice | math | 85 |
| Alice | science | 92 |
| Bob | english | 85 |
| Bob | math | 92 |
| Bob | science | 88 |
| Charlie | english | 90 |
| Charlie | math | 78 |
| Charlie | science | 85 |

</td></tr>
</table>

