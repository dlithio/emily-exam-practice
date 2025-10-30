"""
Test generation of actual derived_column problems using Claude API.
This is a manual test to verify Claude generates valid derived_column problems.
"""
from claude_client import generate_problem
from app import verify_problem_solutions


def test_generate_arithmetic():
    """Generate and test arithmetic derived column problem."""
    print("\n=== Generating Arithmetic Derived Column Problem ===")
    problem = generate_problem("derived_column", "easy", use_cache=False)

    print(f"\nTopic: {problem.topic}")
    print(f"Difficulty: {problem.difficulty}")
    print(f"\nQuestion: {problem.question}")
    print(f"\nInput Tables:")
    for name, df in problem.input_tables.items():
        print(f"  {name}:")
        print(df.to_string(index=False))

    print(f"\nExpected Output:")
    print(problem.expected_output.to_string(index=False))

    # Verify solutions
    verification = verify_problem_solutions(problem)
    print(f"\nVerification Results:")
    print(f"  Pandas valid: {verification['pandas_valid']}")
    print(f"  SQL valid: {verification['sql_valid']}")

    if not verification['pandas_valid']:
        print(f"  Pandas error: {verification['pandas_error']}")
        print(f"  Pandas feedback: {verification['pandas_feedback']}")

    if not verification['sql_valid']:
        print(f"  SQL error: {verification['sql_error']}")
        print(f"  SQL feedback: {verification['sql_feedback']}")

    return verification['pandas_valid'] and verification['sql_valid']


def test_generate_multiple():
    """Generate 5 derived_column problems to see variety."""
    print("\n=== Generating 5 Derived Column Problems ===")

    success_count = 0
    subtypes_seen = set()

    for i in range(5):
        print(f"\n--- Problem {i+1} ---")
        problem = generate_problem("derived_column", "easy", use_cache=False)

        # Try to infer subtype from pandas solution
        if problem.pandas_solution:
            if any(op in problem.pandas_solution for op in ['*', '/', '+', '-']):
                if 'dt.' not in problem.pandas_solution and 'to_datetime' not in problem.pandas_solution:
                    subtype = "Arithmetic"
                else:
                    subtype = "Date"
            elif 'dt.' in problem.pandas_solution or 'to_datetime' in problem.pandas_solution:
                subtype = "Date"
            else:
                subtype = "Conditional"

            subtypes_seen.add(subtype)
            print(f"Subtype: {subtype}")

        print(f"Question: {problem.question}")

        # Verify
        verification = verify_problem_solutions(problem)
        if verification['pandas_valid'] and verification['sql_valid']:
            print("✓ Both solutions verified")
            success_count += 1
        else:
            print("✗ Verification failed")
            if not verification['pandas_valid']:
                print(f"  Pandas: {verification['pandas_feedback']}")
            if not verification['sql_valid']:
                print(f"  SQL: {verification['sql_feedback']}")

    print(f"\n=== Summary ===")
    print(f"Success rate: {success_count}/5")
    print(f"Subtypes seen: {subtypes_seen}")

    return success_count >= 4  # Allow 1 failure


if __name__ == "__main__":
    print("\n" + "="*60)
    print("  Testing Derived Column Problem Generation")
    print("="*60)

    try:
        # Test single problem
        single_success = test_generate_arithmetic()

        # Test multiple problems for variety
        multiple_success = test_generate_multiple()

        if single_success and multiple_success:
            print("\n✅ Derived column problem generation works!")
            print("Claude successfully generates valid derived_column problems.")
        else:
            print("\n⚠ Some issues found - review verification results above")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
