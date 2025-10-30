"""
Generate a few hard problems for manual inspection and verification.
"""

from claude_client import generate_problem
import json


def inspect_hard_problems():
    """Generate and display 3 hard problems for manual verification."""
    print("=" * 80)
    print("GENERATING HARD PROBLEMS FOR MANUAL INSPECTION")
    print("=" * 80)

    problems = []
    attempts = 0
    max_attempts = 10

    while len(problems) < 3 and attempts < max_attempts:
        attempts += 1
        print(f"\nAttempt {attempts}...")

        try:
            problem = generate_problem(
                difficulty="hard",
                selected_topics=None,
                use_cache=False
            )

            problems.append(problem)
            print(f"✓ Generated: {problem.topic}")

        except Exception as e:
            error_msg = str(e)
            if len(error_msg) > 100:
                error_msg = error_msg[:100] + "..."
            print(f"✗ Failed: {error_msg}")

    print("\n" + "=" * 80)
    print(f"INSPECTION RESULTS ({len(problems)} problems)")
    print("=" * 80)

    for i, problem in enumerate(problems, 1):
        print(f"\n{'=' * 80}")
        print(f"PROBLEM {i}")
        print('=' * 80)

        print(f"\nTopic: {problem.topic}")
        print(f"Difficulty: {problem.difficulty}")
        print(f"Pandas-only: {problem.pandas_only}")

        print(f"\nQuestion:")
        print(f"  {problem.question}")

        print(f"\nInput Tables:")
        for table_name, df in problem.input_tables.items():
            print(f"  {table_name}: {df.shape[0]} rows × {df.shape[1]} columns")
            print(f"    Columns: {list(df.columns)}")
            print(f"    Sample:")
            print(f"    {df.head(2).to_string(index=False)}")

        print(f"\nExpected Output:")
        print(f"  Shape: {problem.expected_output.shape[0]} rows × {problem.expected_output.shape[1]} columns")
        print(f"  Columns: {list(problem.expected_output.columns)}")
        print(f"  Preview:")
        print(f"  {problem.expected_output.head(3).to_string(index=False)}")

        print(f"\n--- PANDAS SOLUTION ---")
        print(problem.pandas_solution)

        if not problem.pandas_only:
            print(f"\n--- SQL SOLUTION ---")
            print(problem.sql_solution)

            # Check CTE count
            num_ctes = problem.sql_solution.upper().count(" AS (")
            print(f"\n(Uses {num_ctes} CTE(s))")
        else:
            print(f"\n(Pandas-only problem - no SQL solution)")

        # Count complexity
        pandas_lines = len([l for l in problem.pandas_solution.split('\n')
                          if l.strip() and not l.strip().startswith('#')])
        print(f"\nComplexity:")
        print(f"  Pandas solution: {pandas_lines} lines of code")

        if not problem.pandas_only:
            sql_clauses = sum([
                'WHERE' in problem.sql_solution.upper(),
                'GROUP BY' in problem.sql_solution.upper(),
                'JOIN' in problem.sql_solution.upper(),
                'ORDER BY' in problem.sql_solution.upper(),
                'WITH' in problem.sql_solution.upper(),
                'HAVING' in problem.sql_solution.upper(),
            ])
            print(f"  SQL solution: {sql_clauses} major clauses")

    print("\n" + "=" * 80)
    print("MANUAL VERIFICATION CHECKLIST:")
    print("=" * 80)
    print("For each problem, verify:")
    print("  □ Question is clear and requires multiple operations")
    print("  □ Problem genuinely requires 3-4 skills (or advanced topic)")
    print("  □ Solutions are complex but correct")
    print("  □ CTEs make SQL solution clearer (if applicable)")
    print("  □ Problem is challenging but solvable with thought")
    print("=" * 80)


if __name__ == "__main__":
    inspect_hard_problems()
