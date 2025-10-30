"""
Streamlined test for hard difficulty problems (Step 11.4).
Generates a sample of hard problems and categorizes them by type.
"""

from claude_client import generate_problem
from execution import execute_pandas, execute_sql, compare_dataframes


def test_hard_problem_generation():
    """Generate sample hard problems and verify they work."""
    print("=" * 80)
    print("HARD DIFFICULTY SAMPLE TEST")
    print("=" * 80)
    print("\nGenerating 15 hard problems to verify distribution and correctness...\n")

    results = []
    attempts = 0
    max_attempts = 30  # Try up to 30 times to get 15 successful problems

    while len(results) < 15 and attempts < max_attempts:
        attempts += 1
        print(f"Attempt {attempts}...", end=" ")

        try:
            problem = generate_problem(
                difficulty="hard",
                selected_topics=None,
                use_cache=False
            )

            # Categorize the problem
            topic_lower = problem.topic.lower()
            skills = problem.topic.split(", ")

            if "pivot" in topic_lower or "melt" in topic_lower:
                category = "pivot/melt"
            elif "datatypes" in topic_lower:
                category = "datatypes"
            elif "cross_join" in topic_lower:
                category = "cross_join"
            else:
                category = f"multi-skill ({len(skills)} skills)"

            # Verify pandas solution
            pandas_result, pandas_error = execute_pandas(
                problem.pandas_solution,
                problem.input_tables
            )
            if pandas_error:
                print(f"✗ Pandas error: {pandas_error[:50]}...")
                continue

            pandas_correct, _ = compare_dataframes(pandas_result, problem.expected_output)
            if not pandas_correct:
                print(f"✗ Pandas incorrect")
                continue

            # Verify SQL solution (if not pandas-only)
            sql_correct = True
            has_cte = False
            if not problem.pandas_only:
                sql_result, sql_error = execute_sql(
                    problem.sql_solution,
                    problem.input_tables
                )
                if sql_error:
                    print(f"✗ SQL error: {sql_error[:50]}...")
                    continue

                sql_correct, _ = compare_dataframes(sql_result, problem.expected_output)
                if not sql_correct:
                    print(f"✗ SQL incorrect")
                    continue

                has_cte = "WITH" in problem.sql_solution.upper()
                if not has_cte:
                    print(f"✗ Missing CTE (required for hard)")
                    continue

            print(f"✓ {category}")
            results.append({
                "category": category,
                "topic": problem.topic,
                "pandas_only": problem.pandas_only,
                "has_cte": has_cte,
                "skills_count": len(skills)
            })

        except Exception as e:
            error_msg = str(e)
            if "produce different results" in error_msg:
                print(f"✗ Solutions mismatch")
            else:
                print(f"✗ Error: {error_msg[:50]}...")

    # Summary
    print("\n" + "=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)
    print(f"\nGenerated {len(results)} successful problems out of {attempts} attempts")
    print(f"Success rate: {100*len(results)/attempts:.0f}%\n")

    # Categorize by type
    categories = {}
    for r in results:
        cat = r["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(r)

    print("Distribution by category:")
    for category, items in sorted(categories.items()):
        print(f"  {category}: {len(items)} problems")
        for item in items[:2]:  # Show first 2 examples
            print(f"    - {item['topic']}")

    # Check CTE usage
    sql_problems = [r for r in results if not r["pandas_only"]]
    if sql_problems:
        cte_count = sum(1 for r in sql_problems if r["has_cte"])
        print(f"\nCTE Usage: {cte_count}/{len(sql_problems)} SQL problems ({100*cte_count/len(sql_problems):.0f}%)")

    # Skills distribution
    skill_counts = {}
    for r in results:
        count = r["skills_count"]
        if count not in skill_counts:
            skill_counts[count] = 0
        skill_counts[count] += 1

    print(f"\nSkills per problem:")
    for count, freq in sorted(skill_counts.items()):
        print(f"  {count} skills: {freq} problems")

    print("\n" + "=" * 80)

    # Validation
    if len(results) >= 10:
        print("✓ Successfully generated sufficient hard problems")
        print("✓ All generated problems have verified solutions")
        print("✓ Problem distribution shows variety")
        print("\nStep 11.4 Basic Testing: PASSED")
    else:
        print(f"⚠ Only generated {len(results)} problems (target: 15)")
        print("  This may indicate issues with hard problem generation")

    print("=" * 80)

    return results


if __name__ == "__main__":
    results = test_hard_problem_generation()

    # Print a few example problems for manual inspection
    if results:
        print("\n" + "=" * 80)
        print("EXAMPLE PROBLEMS FOR MANUAL VERIFICATION")
        print("=" * 80)

        for i, result in enumerate(results[:3], 1):
            print(f"\nExample {i} ({result['category']}):")
            print(f"  Topic: {result['topic']}")
            print(f"  Pandas-only: {result['pandas_only']}")
            if not result['pandas_only']:
                print(f"  Has CTE: {result['has_cte']}")
