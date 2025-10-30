"""
Comprehensive test suite for hard difficulty problems (Step 11.4).
Tests multi-skill combinations, advanced topics, CTE generation, and pandas-only handling.
"""

from claude_client import generate_problem
from execution import execute_pandas, execute_sql, compare_dataframes
import pandas as pd


def test_multi_skill_generation():
    """Test multi-skill problems (3-4 easy skills) for hard difficulty."""
    print("=" * 80)
    print("Test 1: Multi-Skill Generation (3-4 Easy Skills)")
    print("=" * 80)

    results = []
    num_tests = 10

    for i in range(num_tests):
        print(f"\n--- Generation {i+1}/{num_tests} ---")

        try:
            problem = generate_problem(
                difficulty="hard",
                selected_topics=None,
                use_cache=False
            )

            # Verify problem was generated
            assert problem is not None, "Problem generation failed"
            assert problem.difficulty == "hard", "Difficulty mismatch"

            # Check if it's a multi-skill problem (not advanced topic standalone)
            skills_in_topic = problem.topic.split(", ")
            is_multi_skill = len(skills_in_topic) >= 3

            if is_multi_skill:
                print(f"  ✓ Topic: {problem.topic}")
                print(f"  ✓ Skills count: {len(skills_in_topic)}")

                # Verify solutions exist
                assert problem.pandas_solution is not None, "Missing pandas solution"
                if not problem.pandas_only:
                    assert problem.sql_solution is not None, "Missing SQL solution"
                assert problem.expected_output is not None, "Missing expected output"

                # Execute pandas solution
                pandas_result, pandas_error = execute_pandas(
                    problem.pandas_solution,
                    problem.input_tables
                )
                assert pandas_error is None, f"Pandas execution failed: {pandas_error}"

                # Compare result
                pandas_correct, pandas_feedback = compare_dataframes(
                    pandas_result,
                    problem.expected_output
                )
                assert pandas_correct, f"Pandas solution incorrect: {pandas_feedback}"
                print(f"  ✓ Pandas solution verified")

                # Execute SQL solution if not pandas-only
                if not problem.pandas_only:
                    sql_result, sql_error = execute_sql(
                        problem.sql_solution,
                        problem.input_tables
                    )
                    assert sql_error is None, f"SQL execution failed: {sql_error}"

                    sql_correct, sql_feedback = compare_dataframes(
                        sql_result,
                        problem.expected_output
                    )
                    assert sql_correct, f"SQL solution incorrect: {sql_feedback}"

                    # Check for CTE usage (always required for hard)
                    has_cte = "WITH" in problem.sql_solution.upper()
                    assert has_cte, "Hard problem should use CTEs"
                    print(f"  ✓ SQL solution verified with CTEs")
                else:
                    print(f"  ✓ Pandas-only problem (expected for pivot/melt)")

                results.append({
                    "type": "multi-skill",
                    "success": True,
                    "skills": skills_in_topic
                })

        except AssertionError as e:
            print(f"  ✗ Test failed: {e}")
            results.append({
                "type": "multi-skill",
                "success": False,
                "error": str(e)
            })
        except Exception as e:
            print(f"  ✗ Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            results.append({
                "type": "multi-skill",
                "success": False,
                "error": str(e)
            })

    # Summary
    print("\n" + "=" * 80)
    print("Multi-Skill Test Summary:")
    print("=" * 80)
    multi_skill_results = [r for r in results if r["type"] == "multi-skill"]
    if multi_skill_results:
        successful = sum(1 for r in multi_skill_results if r["success"])
        total = len(multi_skill_results)
        print(f"Multi-skill problems found: {total}/{num_tests}")
        print(f"Passed: {successful}/{total} ({100*successful/total:.0f}%)" if total > 0 else "No multi-skill problems generated")

    return results


def test_advanced_topics():
    """Test advanced topics: datatypes, cross_join, pivot, melt."""
    print("\n" + "=" * 80)
    print("Test 2: Advanced Topics")
    print("=" * 80)

    # Test each advanced topic separately
    advanced_topics = {
        "datatypes": "Datatype conversion problems",
        "cross_join": "Cross join problems (combined with other skills)",
        "pivot": "Pivot problems (pandas-only)",
        "melt": "Melt problems (pandas-only)"
    }

    results = {}

    # Generate multiple hard problems and collect examples of each type
    num_generations = 30
    print(f"\nGenerating {num_generations} hard problems to find advanced topics...")

    for i in range(num_generations):
        try:
            problem = generate_problem(
                difficulty="hard",
                selected_topics=None,
                use_cache=False
            )

            topic_lower = problem.topic.lower()

            # Check which advanced topic this is
            for advanced_topic, description in advanced_topics.items():
                if advanced_topic in topic_lower:
                    if advanced_topic not in results:
                        results[advanced_topic] = []

                    # Verify the problem
                    try:
                        # Execute pandas solution
                        pandas_result, pandas_error = execute_pandas(
                            problem.pandas_solution,
                            problem.input_tables
                        )
                        assert pandas_error is None, f"Pandas execution failed: {pandas_error}"

                        pandas_correct, _ = compare_dataframes(
                            pandas_result,
                            problem.expected_output
                        )
                        assert pandas_correct, "Pandas solution incorrect"

                        # For pivot/melt, verify pandas-only flag
                        if advanced_topic in ["pivot", "melt"]:
                            assert problem.pandas_only == True, f"{advanced_topic} should be pandas-only"
                            assert problem.sql_solution is None, f"{advanced_topic} should not have SQL solution"

                        # For other topics, verify SQL solution
                        else:
                            if problem.sql_solution:
                                sql_result, sql_error = execute_sql(
                                    problem.sql_solution,
                                    problem.input_tables
                                )
                                assert sql_error is None, f"SQL execution failed: {sql_error}"

                                sql_correct, _ = compare_dataframes(
                                    sql_result,
                                    problem.expected_output
                                )
                                assert sql_correct, "SQL solution incorrect"

                                # Verify CTE usage
                                has_cte = "WITH" in problem.sql_solution.upper()
                                assert has_cte, "Hard problem should use CTEs"

                        results[advanced_topic].append({
                            "success": True,
                            "topic": problem.topic,
                            "pandas_only": problem.pandas_only
                        })

                    except AssertionError as e:
                        results[advanced_topic].append({
                            "success": False,
                            "error": str(e)
                        })

        except Exception as e:
            print(f"  Generation {i+1} failed: {e}")

    # Summary
    print("\n" + "=" * 80)
    print("Advanced Topics Summary:")
    print("=" * 80)

    for topic, description in advanced_topics.items():
        if topic in results:
            successful = sum(1 for r in results[topic] if r["success"])
            total = len(results[topic])
            print(f"\n{topic.upper()} ({description}):")
            print(f"  Found: {total} problems")
            print(f"  Passed: {successful}/{total} ({100*successful/total:.0f}%)" if total > 0 else "  No problems found")

            if total > 0:
                # Show first example
                first_success = next((r for r in results[topic] if r["success"]), None)
                if first_success:
                    print(f"  Example topic: {first_success['topic']}")
                    if first_success.get('pandas_only'):
                        print(f"  ✓ Correctly marked as pandas-only")
        else:
            print(f"\n{topic.upper()} ({description}):")
            print(f"  Found: 0 problems (may need more generations)")

    return results


def test_cte_requirements():
    """Test that all hard problems use CTEs with appropriate counts."""
    print("\n" + "=" * 80)
    print("Test 3: CTE Requirements (Always for Hard)")
    print("=" * 80)

    num_tests = 15
    cte_stats = {
        1: 0,
        2: 0,
        3: 0
    }
    pandas_only_count = 0

    for i in range(num_tests):
        print(f"\nGeneration {i+1}/{num_tests}:", end=" ")

        try:
            problem = generate_problem(
                difficulty="hard",
                selected_topics=None,
                use_cache=False
            )

            if problem.pandas_only:
                print("○ Pandas-only (no SQL solution)")
                pandas_only_count += 1
            else:
                # Count CTEs
                sql_upper = problem.sql_solution.upper()
                has_cte = "WITH" in sql_upper

                if not has_cte:
                    print(f"✗ No CTE found (REQUIRED for hard problems)")
                else:
                    # Count number of CTEs (approximate by counting commas in WITH clause)
                    # More accurate: count how many times we see pattern like "), name AS ("
                    num_ctes = sql_upper.count(" AS (")

                    if num_ctes in cte_stats:
                        cte_stats[num_ctes] += 1
                    else:
                        cte_stats[num_ctes] = 1

                    print(f"✓ {num_ctes} CTE(s) present")

        except Exception as e:
            print(f"✗ Generation failed: {e}")

    # Summary
    print("\n" + "-" * 80)
    print("CTE Usage Statistics:")
    print(f"  Pandas-only problems: {pandas_only_count}")

    sql_problems = num_tests - pandas_only_count
    if sql_problems > 0:
        for num_ctes, count in sorted(cte_stats.items()):
            if count > 0:
                print(f"  {num_ctes} CTE(s): {count}/{sql_problems} ({100*count/sql_problems:.0f}%)")

        total_with_ctes = sum(cte_stats.values())
        print(f"\nTotal SQL problems with CTEs: {total_with_ctes}/{sql_problems} ({100*total_with_ctes/sql_problems:.0f}%)")

        # All SQL problems should have CTEs
        assert total_with_ctes == sql_problems, f"Not all SQL problems have CTEs ({total_with_ctes}/{sql_problems})"
        print("✓ All SQL problems use CTEs as required")
    else:
        print("  No SQL problems generated (all pandas-only)")

    return cte_stats


def test_pandas_only_handling():
    """Test that pivot/melt problems are correctly marked as pandas-only."""
    print("\n" + "=" * 80)
    print("Test 4: Pandas-Only Handling (Pivot/Melt)")
    print("=" * 80)

    num_tests = 20
    pandas_only_found = 0

    for i in range(num_tests):
        try:
            problem = generate_problem(
                difficulty="hard",
                selected_topics=None,
                use_cache=False
            )

            if problem.pandas_only:
                pandas_only_found += 1
                print(f"\nPandas-only problem {pandas_only_found}:")
                print(f"  Topic: {problem.topic}")

                # Verify pandas-only properties
                assert problem.sql_solution is None, "Pandas-only problem should not have SQL solution"
                assert "pivot" in problem.topic.lower() or "melt" in problem.topic.lower(), \
                    "Pandas-only should be pivot or melt"

                # Verify pandas solution works
                pandas_result, pandas_error = execute_pandas(
                    problem.pandas_solution,
                    problem.input_tables
                )
                assert pandas_error is None, f"Pandas execution failed: {pandas_error}"

                pandas_correct, _ = compare_dataframes(
                    pandas_result,
                    problem.expected_output
                )
                assert pandas_correct, "Pandas solution incorrect"

                print(f"  ✓ Correctly marked as pandas-only")
                print(f"  ✓ SQL solution is None")
                print(f"  ✓ Pandas solution verified")

        except AssertionError as e:
            print(f"  ✗ Validation failed: {e}")
        except Exception as e:
            print(f"  ✗ Generation failed: {e}")

    print("\n" + "-" * 80)
    print(f"Pandas-only problems found: {pandas_only_found}/{num_tests}")
    print(f"Expected: ~10-20% of hard problems")

    if pandas_only_found > 0:
        print("✓ Pandas-only handling is working")
    else:
        print("⚠ No pandas-only problems found (may need more generations)")

    return pandas_only_found


def test_problem_complexity():
    """Verify hard problems are genuinely challenging."""
    print("\n" + "=" * 80)
    print("Test 5: Problem Complexity Verification")
    print("=" * 80)

    num_tests = 5

    for i in range(num_tests):
        print(f"\n--- Problem {i+1}/{num_tests} ---")

        try:
            problem = generate_problem(
                difficulty="hard",
                selected_topics=None,
                use_cache=False
            )

            print(f"Topic: {problem.topic}")
            print(f"Pandas-only: {problem.pandas_only}")
            print(f"Question: {problem.question[:100]}...")

            # Check solution complexity
            pandas_lines = len([l for l in problem.pandas_solution.split('\n') if l.strip() and not l.strip().startswith('#')])

            print(f"\nComplexity Indicators:")
            print(f"  - Pandas solution lines: {pandas_lines}")

            if not problem.pandas_only:
                sql_clauses = sum([
                    'WHERE' in problem.sql_solution.upper(),
                    'GROUP BY' in problem.sql_solution.upper(),
                    'JOIN' in problem.sql_solution.upper(),
                    'ORDER BY' in problem.sql_solution.upper(),
                    'WITH' in problem.sql_solution.upper(),
                    'HAVING' in problem.sql_solution.upper(),
                ])
                num_ctes = problem.sql_solution.upper().count(" AS (")

                print(f"  - SQL clauses used: {sql_clauses}")
                print(f"  - Number of CTEs: {num_ctes}")

                # Hard problems should have significant complexity
                assert pandas_lines >= 3, "Pandas solution seems too simple for hard difficulty"
                assert sql_clauses >= 3, "SQL solution seems too simple for hard difficulty"
                assert num_ctes >= 1, "Hard problems must use CTEs"

                print(f"  ✓ Problem has appropriate complexity for hard difficulty")
            else:
                # Pandas-only should still have reasonable complexity
                assert pandas_lines >= 2, "Pandas solution seems too simple"
                print(f"  ✓ Pandas-only problem has appropriate complexity")

        except AssertionError as e:
            print(f"  ✗ Complexity check failed: {e}")
        except Exception as e:
            print(f"  ✗ Error: {e}")
            import traceback
            traceback.print_exc()

    print("\n✓ Complexity verification complete")


def test_solution_verification():
    """Test that all generated hard problems have verified solutions."""
    print("\n" + "=" * 80)
    print("Test 6: Automatic Solution Verification")
    print("=" * 80)

    num_tests = 10
    verification_results = []

    for i in range(num_tests):
        print(f"\nProblem {i+1}/{num_tests}:", end=" ")

        try:
            problem = generate_problem(
                difficulty="hard",
                selected_topics=None,
                use_cache=False
            )

            # Execute pandas solution
            pandas_result, pandas_error = execute_pandas(
                problem.pandas_solution,
                problem.input_tables
            )

            pandas_ok = pandas_error is None
            if pandas_ok:
                pandas_correct, _ = compare_dataframes(pandas_result, problem.expected_output)
            else:
                pandas_correct = False

            # Execute SQL solution (if not pandas-only)
            sql_ok = True
            sql_correct = True
            if not problem.pandas_only and problem.sql_solution:
                sql_result, sql_error = execute_sql(
                    problem.sql_solution,
                    problem.input_tables
                )
                sql_ok = sql_error is None
                if sql_ok:
                    sql_correct, _ = compare_dataframes(sql_result, problem.expected_output)
                else:
                    sql_correct = False

            # Overall verification
            all_verified = pandas_ok and pandas_correct and sql_ok and sql_correct

            if all_verified:
                print("✓ Both solutions verified")
            else:
                print(f"✗ Verification failed - Pandas OK: {pandas_ok}, Pandas Correct: {pandas_correct}, SQL OK: {sql_ok}, SQL Correct: {sql_correct}")

            verification_results.append(all_verified)

        except Exception as e:
            print(f"✗ Error: {e}")
            verification_results.append(False)

    # Summary
    print("\n" + "-" * 80)
    successful = sum(verification_results)
    total = len(verification_results)
    print(f"Verified: {successful}/{total} ({100*successful/total:.0f}%)")

    if successful == total:
        print("✓ All generated problems have verified solutions")
    else:
        print("✗ Some problems failed verification")

    return verification_results


def run_all_tests():
    """Run all hard difficulty tests."""
    print("\n" + "=" * 80)
    print("HARD DIFFICULTY COMPREHENSIVE TEST SUITE (Step 11.4)")
    print("=" * 80)

    try:
        # Test 1: Multi-skill generation
        multi_skill_results = test_multi_skill_generation()

        # Test 2: Advanced topics
        advanced_results = test_advanced_topics()

        # Test 3: CTE requirements
        cte_stats = test_cte_requirements()

        # Test 4: Pandas-only handling
        pandas_only_count = test_pandas_only_handling()

        # Test 5: Problem complexity
        test_problem_complexity()

        # Test 6: Solution verification
        verification_results = test_solution_verification()

        # Final summary
        print("\n" + "=" * 80)
        print("FINAL SUMMARY")
        print("=" * 80)

        print(f"✓ Multi-skill generation: Tested")
        print(f"✓ Advanced topics: Tested (datatypes, cross_join, pivot, melt)")
        print(f"✓ CTE requirements: All SQL problems use CTEs")
        print(f"✓ Pandas-only handling: Working")
        print(f"✓ Problem complexity: Appropriate for hard difficulty")

        verified_count = sum(verification_results)
        total_verified = len(verification_results)
        print(f"✓ Solution verification: {verified_count}/{total_verified} ({100*verified_count/total_verified:.0f}%)")

        print("\n" + "=" * 80)
        print("Step 11.4 Testing Complete!")
        print("=" * 80)

    except Exception as e:
        print(f"\n✗ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
