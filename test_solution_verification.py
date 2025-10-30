#!/usr/bin/env python3
"""
Test solution verification functionality.
This test generates a problem and verifies that the reference solutions work correctly.
"""

import sys
from claude_client import generate_problem
from app import verify_problem_solutions


def test_verification():
    """Test that solution verification works for a generated problem."""
    print("=" * 60)
    print("Testing Solution Verification")
    print("=" * 60)

    # Generate a problem
    print("\n1. Generating a problem...")
    try:
        problem = generate_problem(
            topic="filter_rows",
            difficulty="easy",
            use_cache=True
        )
        print(f"✓ Problem generated successfully")
        print(f"  Topic: {problem.topic}")
        print(f"  Difficulty: {problem.difficulty}")
        print(f"  Question: {problem.question[:80]}...")
        print(f"  Has pandas solution: {problem.pandas_solution is not None}")
        print(f"  Has SQL solution: {problem.sql_solution is not None}")
    except Exception as e:
        print(f"✗ Failed to generate problem: {e}")
        return False

    # Verify the solutions
    print("\n2. Verifying reference solutions...")
    try:
        verification = verify_problem_solutions(problem)

        print("\n  Pandas Solution Verification:")
        print(f"    Valid: {verification['pandas_valid']}")
        if verification['pandas_error']:
            print(f"    Error: {verification['pandas_error'][:200]}")
        if verification['pandas_feedback']:
            print(f"    Feedback: {verification['pandas_feedback']}")

        print("\n  SQL Solution Verification:")
        print(f"    Valid: {verification['sql_valid']}")
        if verification['sql_error']:
            print(f"    Error: {verification['sql_error'][:200]}")
        if verification['sql_feedback']:
            print(f"    Feedback: {verification['sql_feedback']}")

        # Check results
        print("\n3. Results:")
        if verification['pandas_valid'] and verification['sql_valid']:
            print("✓ Both solutions verified successfully!")
            return True
        else:
            if not verification['pandas_valid']:
                print("✗ Pandas solution verification failed")
            if not verification['sql_valid']:
                print("✗ SQL solution verification failed")
            return False

    except Exception as e:
        print(f"✗ Verification failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multiple_problems():
    """Test verification on multiple problems to see overall success rate."""
    print("\n" + "=" * 60)
    print("Testing Multiple Problems")
    print("=" * 60)

    topics = ["filter_rows", "filter_columns", "aggregations", "distinct"]
    results = []

    for topic in topics:
        print(f"\nTesting topic: {topic}")
        try:
            problem = generate_problem(topic=topic, difficulty="easy", use_cache=False)
            verification = verify_problem_solutions(problem)

            pandas_ok = verification['pandas_valid']
            sql_ok = verification['sql_valid']

            print(f"  Pandas: {'✓' if pandas_ok else '✗'}")
            print(f"  SQL: {'✓' if sql_ok else '✗'}")

            results.append({
                'topic': topic,
                'pandas_valid': pandas_ok,
                'sql_valid': sql_ok
            })
        except Exception as e:
            print(f"  Failed to generate/verify: {e}")
            results.append({
                'topic': topic,
                'pandas_valid': False,
                'sql_valid': False
            })

    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    pandas_success = sum(1 for r in results if r['pandas_valid'])
    sql_success = sum(1 for r in results if r['sql_valid'])
    total = len(results)

    print(f"Pandas solutions verified: {pandas_success}/{total} ({100*pandas_success/total:.0f}%)")
    print(f"SQL solutions verified: {sql_success}/{total} ({100*sql_success/total:.0f}%)")

    return pandas_success == total and sql_success == total


if __name__ == "__main__":
    # Run basic test
    success = test_verification()

    # If basic test passes, run multiple problems test
    if success:
        print("\n" + "=" * 60)
        print("Basic test passed! Running extended tests...")
        print("=" * 60)
        all_success = test_multiple_problems()
        sys.exit(0 if all_success else 1)
    else:
        print("\nBasic test failed. Skipping extended tests.")
        sys.exit(1)
