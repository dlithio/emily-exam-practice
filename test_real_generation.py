"""Test real problem generation with the new solution verification approach."""
from claude_client import generate_problem
from execution import execute_pandas, execute_sql, compare_dataframes

def test_real_generation():
    """Generate a few real problems and verify the solutions match."""
    print("\n" + "="*80)
    print("TESTING REAL PROBLEM GENERATION")
    print("="*80)

    difficulties = ["easy", "medium", "hard"]
    problems_per_difficulty = 2

    all_passed = True
    total_generated = 0

    for difficulty in difficulties:
        print(f"\n{'='*80}")
        print(f"Testing {difficulty.upper()} difficulty problems")
        print(f"{'='*80}")

        for i in range(problems_per_difficulty):
            print(f"\nGenerating {difficulty} problem {i+1}/{problems_per_difficulty}...")

            try:
                # Generate problem without cache to get fresh problems
                problem = generate_problem(
                    difficulty=difficulty,
                    selected_topics=[],
                    use_cache=False
                )

                print(f"✓ Problem generated successfully")
                print(f"  Topic: {problem.topic}")
                print(f"  Difficulty: {problem.difficulty}")
                print(f"  Question: {problem.question[:100]}...")
                print(f"  Expected output shape: {problem.expected_output.shape}")

                # Verify that pandas solution still produces expected output
                pandas_result, pandas_error = execute_pandas(
                    problem.pandas_solution,
                    problem.input_tables
                )

                if pandas_error:
                    print(f"✗ Pandas solution failed: {pandas_error[:100]}...")
                    all_passed = False
                    continue

                is_match, feedback = compare_dataframes(pandas_result, problem.expected_output)
                if not is_match:
                    print(f"✗ Pandas result doesn't match expected output: {feedback}")
                    all_passed = False
                    continue

                print(f"✓ Pandas solution verified")

                # Verify that SQL solution still produces expected output
                sql_result, sql_error = execute_sql(
                    problem.sql_solution,
                    problem.input_tables
                )

                if sql_error:
                    print(f"✗ SQL solution failed: {sql_error[:100]}...")
                    all_passed = False
                    continue

                is_match, feedback = compare_dataframes(sql_result, problem.expected_output)
                if not is_match:
                    print(f"✗ SQL result doesn't match expected output: {feedback}")
                    all_passed = False
                    continue

                print(f"✓ SQL solution verified")

                # Verify pandas and SQL match each other
                is_match, feedback = compare_dataframes(pandas_result, sql_result)
                if not is_match:
                    print(f"✗ Pandas and SQL results don't match: {feedback}")
                    all_passed = False
                    continue

                print(f"✓ Pandas and SQL solutions match each other")
                print(f"✓ ALL CHECKS PASSED for this problem")

                total_generated += 1

            except Exception as e:
                print(f"✗ Problem generation failed: {str(e)[:200]}...")
                all_passed = False

    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total problems successfully generated: {total_generated}/{len(difficulties) * problems_per_difficulty}")

    if all_passed and total_generated == len(difficulties) * problems_per_difficulty:
        print("="*80)
        print("🎉 ALL REAL PROBLEM GENERATION TESTS PASSED!")
        print("="*80)
    else:
        print("="*80)
        print("⚠️  SOME TESTS FAILED! Review the output above.")
        print("="*80)

if __name__ == "__main__":
    test_real_generation()
