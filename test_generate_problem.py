"""
Test script for Step 5.3: Verify generate_problem() function works correctly.

This script tests that generate_problem():
- Returns a valid Problem object
- DataFrames look reasonable
- Question is clear
- Expected output is correct
"""

from claude_client import generate_problem


def test_generate_problem():
    """
    Test the generate_problem function as specified in Step 5.3.
    """
    print("="*70)
    print("Testing generate_problem() - Step 5.3 Verification")
    print("="*70)
    print()

    # Test case from Step 5.3
    topic = "filter_rows"
    difficulty = "easy"

    print(f"Generating problem: topic='{topic}', difficulty='{difficulty}'")
    print("Calling generate_problem()...\n")

    try:
        problem = generate_problem(topic, difficulty)
        print("✓ generate_problem() returned successfully!")
        print()

    except Exception as e:
        print(f"✗ generate_problem() failed: {e}")
        return False

    # Verification 1: Returns valid Problem object
    print("-" * 70)
    print("Verification 1: Returns valid Problem object")
    print("-" * 70)

    from models import Problem
    if isinstance(problem, Problem):
        print("✓ Returned object is a Problem instance")
    else:
        print(f"✗ Returned object is {type(problem)}, not Problem")
        return False

    # Check all required attributes
    checks = [
        ("Has input_tables", hasattr(problem, "input_tables")),
        ("Has question", hasattr(problem, "question")),
        ("Has expected_output", hasattr(problem, "expected_output")),
        ("Has topic", hasattr(problem, "topic")),
        ("Has difficulty", hasattr(problem, "difficulty")),
    ]

    all_passed = True
    for check_name, result in checks:
        status = "✓" if result else "✗"
        print(f"{status} {check_name}")
        if not result:
            all_passed = False

    if not all_passed:
        return False

    print()

    # Verification 2: DataFrames look reasonable
    print("-" * 70)
    print("Verification 2: DataFrames look reasonable")
    print("-" * 70)

    import pandas as pd

    # Check input_tables
    if not isinstance(problem.input_tables, dict):
        print(f"✗ input_tables is {type(problem.input_tables)}, not dict")
        return False

    if len(problem.input_tables) == 0:
        print("✗ input_tables is empty")
        return False

    print(f"✓ Has {len(problem.input_tables)} input table(s)")

    for table_name, df in problem.input_tables.items():
        if not isinstance(df, pd.DataFrame):
            print(f"✗ Table '{table_name}' is {type(df)}, not DataFrame")
            return False

        if df.empty:
            print(f"✗ Table '{table_name}' is empty")
            return False

        print(f"✓ Table '{table_name}': {df.shape[0]} rows, {df.shape[1]} columns")

        # Display the table
        print(f"\n  Table: {table_name}")
        print(f"  Columns: {list(df.columns)}")
        print(f"  Data:\n{df.to_string(index=False)}")
        print()

    # Check expected_output
    if not isinstance(problem.expected_output, pd.DataFrame):
        print(f"✗ expected_output is {type(problem.expected_output)}, not DataFrame")
        return False

    print(f"✓ Expected output: {problem.expected_output.shape[0]} rows, {problem.expected_output.shape[1]} columns")
    print(f"\n  Expected Output:")
    print(f"  Columns: {list(problem.expected_output.columns)}")
    print(f"  Data:\n{problem.expected_output.to_string(index=False)}")
    print()

    # Verification 3: Question is clear
    print("-" * 70)
    print("Verification 3: Question is clear")
    print("-" * 70)

    if not isinstance(problem.question, str):
        print(f"✗ Question is {type(problem.question)}, not str")
        return False

    if len(problem.question.strip()) == 0:
        print("✗ Question is empty")
        return False

    if len(problem.question) < 10:
        print(f"✗ Question is too short ({len(problem.question)} chars)")
        return False

    print(f"✓ Question is a non-empty string ({len(problem.question)} characters)")
    print(f"\nQuestion:\n  {problem.question}")
    print()

    # Verification 4: Expected output is correct (manual review)
    print("-" * 70)
    print("Verification 4: Expected output correctness (manual review)")
    print("-" * 70)

    print("Topic:", problem.topic)
    print("Difficulty:", problem.difficulty)
    print()
    print("Please manually verify that the expected output is correct for the question.")
    print("This requires human judgment to ensure the problem makes sense.")
    print()

    # Summary
    print("=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    print()
    print("✓ Returns valid Problem object")
    print("✓ DataFrames look reasonable")
    print("✓ Question is clear")
    print("⚠  Expected output correctness requires manual review")
    print()
    print("✓✓✓ generate_problem() function is working correctly!")
    print()
    print("Step 5.3 complete!")
    print("=" * 70)

    return True


def test_multiple_topics():
    """
    Test generate_problem with different topics to ensure it's robust.
    """
    print("\n\n")
    print("=" * 70)
    print("Additional Testing: Multiple Topics and Difficulties")
    print("=" * 70)
    print()

    test_cases = [
        ("filter_rows", "easy"),
        ("filter_columns", "easy"),
        ("group_by", "medium"),
        ("joins", "medium"),
    ]

    results = []
    for topic, difficulty in test_cases:
        print(f"\nTesting: topic='{topic}', difficulty='{difficulty}'")
        try:
            problem = generate_problem(topic, difficulty)
            print(f"  ✓ Generated successfully")
            print(f"  - Question: {problem.question[:60]}...")
            print(f"  - Input tables: {list(problem.input_tables.keys())}")
            print(f"  - Expected output shape: {problem.expected_output.shape}")
            results.append((topic, difficulty, True))
        except Exception as e:
            print(f"  ✗ Failed: {e}")
            results.append((topic, difficulty, False))

    print("\n" + "=" * 70)
    print("MULTIPLE TOPICS TEST SUMMARY")
    print("=" * 70)
    for topic, difficulty, passed in results:
        status = "✓" if passed else "✗"
        print(f"{status} {topic} ({difficulty})")

    all_passed = all(result for _, _, result in results)
    if all_passed:
        print("\n✓✓✓ All topics tested successfully!")
    else:
        print("\n⚠ Some topics failed - review above")
    print("=" * 70)


if __name__ == "__main__":
    # Run main verification test
    success = test_generate_problem()

    if success:
        # Run additional tests with multiple topics
        test_multiple_topics()
    else:
        print("\n✗ Main test failed. Fix issues before testing additional topics.")
