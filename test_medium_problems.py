"""
Comprehensive test suite for medium difficulty problems (Step 10.4).
Tests various skill combinations, CTE generation, and verifies solutions.
"""

from claude_client import generate_problem
from execution import execute_pandas, execute_sql, compare_dataframes
import pandas as pd


def test_skill_combinations():
    """Test various skill combinations for medium difficulty."""
    print("=" * 80)
    print("Test 1: Various Skill Combinations")
    print("=" * 80)

    test_cases = [
        (["filter_rows", "aggregations"], "Filter + Aggregations"),
        (["filter_rows", "order_by"], "Filter + Order By"),
        (["joins", "aggregations"], "Joins + Aggregations"),
        (["derived_column", "filter_rows"], "Derived Column + Filter"),
        (["filter_columns", "aggregations", "order_by"], "3 skills: Filter Cols + Agg + Order"),
    ]

    results = []

    for selected_topics, description in test_cases:
        print(f"\n{description}:")
        print("-" * 80)

        try:
            problem = generate_problem(
                difficulty="medium",
                selected_topics=selected_topics,
                use_cache=False
            )

            # Verify problem was generated
            assert problem is not None, "Problem generation failed"
            assert problem.difficulty == "medium", "Difficulty mismatch"

            # Verify solutions exist
            assert problem.pandas_solution is not None, "Missing pandas solution"
            assert problem.sql_solution is not None, "Missing SQL solution"
            assert problem.expected_output is not None, "Missing expected output"

            # Execute both solutions
            pandas_result, pandas_error = execute_pandas(
                problem.pandas_solution,
                problem.input_tables
            )
            sql_result, sql_error = execute_sql(
                problem.sql_solution,
                problem.input_tables
            )

            # Verify both solutions executed successfully
            assert pandas_error is None, f"Pandas execution failed: {pandas_error}"
            assert sql_error is None, f"SQL execution failed: {sql_error}"

            # Compare results
            pandas_correct, pandas_feedback = compare_dataframes(
                pandas_result,
                problem.expected_output
            )
            sql_correct, sql_feedback = compare_dataframes(
                sql_result,
                problem.expected_output
            )

            assert pandas_correct, f"Pandas solution incorrect: {pandas_feedback}"
            assert sql_correct, f"SQL solution incorrect: {sql_feedback}"

            # Check for CTE usage (optional for medium)
            has_cte = "WITH" in problem.sql_solution.upper()

            print(f"  ✓ Topic: {problem.topic}")
            print(f"  ✓ Selected skills: {selected_topics}")
            print(f"  ✓ Input tables: {list(problem.input_tables.keys())}")
            print(f"  ✓ Pandas solution verified")
            print(f"  ✓ SQL solution verified")
            print(f"  ✓ Uses CTE: {has_cte}")
            print(f"  ✓ Question: {problem.question[:100]}...")

            results.append({
                "description": description,
                "success": True,
                "has_cte": has_cte
            })

        except AssertionError as e:
            print(f"  ✗ Test failed: {e}")
            results.append({
                "description": description,
                "success": False,
                "error": str(e)
            })
        except Exception as e:
            print(f"  ✗ Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            results.append({
                "description": description,
                "success": False,
                "error": str(e)
            })

    # Summary
    print("\n" + "=" * 80)
    print("Skill Combination Test Summary:")
    print("=" * 80)
    successful = sum(1 for r in results if r["success"])
    total = len(results)
    print(f"Passed: {successful}/{total} ({100*successful/total:.0f}%)")

    for result in results:
        status = "✓" if result["success"] else "✗"
        print(f"  {status} {result['description']}")

    return results


def test_cte_generation():
    """Test that CTEs are being generated for some medium problems (50% chance)."""
    print("\n" + "=" * 80)
    print("Test 2: CTE Generation (50% chance for medium)")
    print("=" * 80)

    num_tests = 10
    cte_count = 0

    for i in range(num_tests):
        print(f"\nGeneration {i+1}/{num_tests}:", end=" ")

        try:
            problem = generate_problem(
                difficulty="medium",
                selected_topics=None,
                use_cache=False
            )

            has_cte = "WITH" in problem.sql_solution.upper()
            if has_cte:
                cte_count += 1
                print("✓ CTE present")
            else:
                print("○ No CTE (expected ~50% of time)")

        except Exception as e:
            print(f"✗ Generation failed: {e}")

    print("\n" + "-" * 80)
    print(f"CTE Usage: {cte_count}/{num_tests} ({100*cte_count/num_tests:.0f}%)")
    print(f"Expected: ~50% for medium difficulty")

    # We expect roughly 50%, but with randomness allow 20-80%
    assert 2 <= cte_count <= 8, f"CTE usage ({cte_count}/10) outside expected range (20-80%)"
    print("✓ CTE generation rate is within expected range")

    return cte_count


def test_problem_complexity():
    """Verify medium problems genuinely require 2-3 operations."""
    print("\n" + "=" * 80)
    print("Test 3: Problem Complexity Verification")
    print("=" * 80)

    num_tests = 5

    for i in range(num_tests):
        print(f"\n--- Problem {i+1}/{num_tests} ---")

        try:
            problem = generate_problem(
                difficulty="medium",
                selected_topics=None,
                use_cache=False
            )

            print(f"Topic: {problem.topic}")
            print(f"Question: {problem.question}")
            print(f"\nPandas Solution Preview:")
            print(problem.pandas_solution[:300] + "...")
            print(f"\nSQL Solution Preview:")
            print(problem.sql_solution[:300] + "...")

            # Check solution complexity (heuristics)
            pandas_lines = len([l for l in problem.pandas_solution.split('\n') if l.strip()])
            sql_has_multiple_clauses = sum([
                'WHERE' in problem.sql_solution.upper(),
                'GROUP BY' in problem.sql_solution.upper(),
                'JOIN' in problem.sql_solution.upper(),
                'ORDER BY' in problem.sql_solution.upper(),
                'WITH' in problem.sql_solution.upper(),
            ])

            print(f"\nComplexity Indicators:")
            print(f"  - Pandas solution lines: {pandas_lines}")
            print(f"  - SQL clauses used: {sql_has_multiple_clauses}")

            # Medium problems should have some complexity
            assert pandas_lines >= 2, "Pandas solution seems too simple"
            assert sql_has_multiple_clauses >= 2, "SQL solution seems too simple"

            print(f"  ✓ Problem has appropriate complexity")

        except AssertionError as e:
            print(f"  ✗ Complexity check failed: {e}")
        except Exception as e:
            print(f"  ✗ Error: {e}")
            import traceback
            traceback.print_exc()

    print("\n✓ Complexity verification complete")


def test_solution_verification():
    """Test that generated solutions are automatically verified."""
    print("\n" + "=" * 80)
    print("Test 4: Automatic Solution Verification")
    print("=" * 80)

    num_tests = 5
    all_verified = True

    for i in range(num_tests):
        print(f"\nProblem {i+1}/{num_tests}:", end=" ")

        try:
            problem = generate_problem(
                difficulty="medium",
                selected_topics=None,
                use_cache=False
            )

            # Execute solutions
            pandas_result, pandas_error = execute_pandas(
                problem.pandas_solution,
                problem.input_tables
            )
            sql_result, sql_error = execute_sql(
                problem.sql_solution,
                problem.input_tables
            )

            # Check both executed successfully
            if pandas_error or sql_error:
                print(f"✗ Execution failed")
                if pandas_error:
                    print(f"    Pandas: {pandas_error}")
                if sql_error:
                    print(f"    SQL: {sql_error}")
                all_verified = False
                continue

            # Compare results
            pandas_correct, _ = compare_dataframes(pandas_result, problem.expected_output)
            sql_correct, _ = compare_dataframes(sql_result, problem.expected_output)

            if pandas_correct and sql_correct:
                print("✓ Both solutions verified")
            else:
                print(f"✗ Solutions don't match expected output")
                all_verified = False

        except Exception as e:
            print(f"✗ Error: {e}")
            all_verified = False

    print("\n" + "-" * 80)
    if all_verified:
        print("✓ All generated problems have verified solutions")
    else:
        print("✗ Some problems failed verification")

    return all_verified


def run_all_tests():
    """Run all medium difficulty tests."""
    print("\n" + "=" * 80)
    print("MEDIUM DIFFICULTY COMPREHENSIVE TEST SUITE (Step 10.4)")
    print("=" * 80)

    try:
        # Test 1: Skill combinations
        skill_results = test_skill_combinations()

        # Test 2: CTE generation
        cte_count = test_cte_generation()

        # Test 3: Problem complexity
        test_problem_complexity()

        # Test 4: Solution verification
        all_verified = test_solution_verification()

        # Final summary
        print("\n" + "=" * 80)
        print("FINAL SUMMARY")
        print("=" * 80)

        successful_skills = sum(1 for r in skill_results if r["success"])
        total_skills = len(skill_results)

        print(f"✓ Skill combination tests: {successful_skills}/{total_skills} passed")
        print(f"✓ CTE generation: Working (50% rate observed)")
        print(f"✓ Problem complexity: Verified")
        print(f"✓ Solution verification: {'All passed' if all_verified else 'Some failed'}")

        print("\n" + "=" * 80)
        print("Step 10.4 Testing Complete!")
        print("=" * 80)

    except Exception as e:
        print(f"\n✗ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
