"""
Test script for medium difficulty problem generation.
This tests the integration of difficulty_manager with claude_client.
"""

from claude_client import generate_problem

def test_medium_problem():
    """Test generating a medium difficulty problem."""
    print("=" * 60)
    print("Testing Medium Difficulty Problem Generation")
    print("=" * 60)

    # Test 1: Generate medium problem without topic selection
    print("\nTest 1: Medium problem with all topics available")
    print("-" * 60)
    try:
        problem = generate_problem(
            difficulty="medium",
            selected_topics=None,
            use_cache=False
        )

        print(f"✓ Problem generated successfully!")
        print(f"  - Topic: {problem.topic}")
        print(f"  - Difficulty: {problem.difficulty}")
        print(f"  - Input tables: {list(problem.input_tables.keys())}")
        print(f"  - Question: {problem.question[:100]}...")
        print(f"  - Expected output shape: {problem.expected_output.shape}")
        print(f"  - Has pandas solution: {problem.pandas_solution is not None}")
        print(f"  - Has SQL solution: {problem.sql_solution is not None}")

        # Check for CTEs in SQL solution
        if problem.sql_solution and "WITH" in problem.sql_solution:
            print(f"  - SQL uses CTEs: Yes ✓")
        else:
            print(f"  - SQL uses CTEs: No (this is okay for medium - 50% chance)")

        print(f"\nGenerated SQL Solution:")
        print(problem.sql_solution)

    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()

    # Test 2: Generate medium problem with specific topics
    print("\n\nTest 2: Medium problem with selected topics")
    print("-" * 60)
    try:
        problem = generate_problem(
            difficulty="medium",
            selected_topics=["filter_rows", "aggregations", "order_by"],
            use_cache=False
        )

        print(f"✓ Problem generated successfully!")
        print(f"  - Topic: {problem.topic}")
        print(f"  - Difficulty: {problem.difficulty}")
        print(f"  - Question: {problem.question[:100]}...")

        # Check for CTEs in SQL solution
        if problem.sql_solution and "WITH" in problem.sql_solution:
            print(f"  - SQL uses CTEs: Yes ✓")
        else:
            print(f"  - SQL uses CTEs: No (this is okay for medium - 50% chance)")

    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()

    # Test 3: Generate easy problem to verify backward compatibility
    print("\n\nTest 3: Easy problem (backward compatibility)")
    print("-" * 60)
    try:
        problem = generate_problem(
            difficulty="easy",
            selected_topics=None,
            use_cache=False
        )

        print(f"✓ Problem generated successfully!")
        print(f"  - Topic: {problem.topic}")
        print(f"  - Difficulty: {problem.difficulty}")

        # Easy problems should never have CTEs
        if problem.sql_solution and "WITH" in problem.sql_solution:
            print(f"  - SQL uses CTEs: Yes ✗ (UNEXPECTED for easy!)")
        else:
            print(f"  - SQL uses CTEs: No ✓ (correct for easy)")

    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("Testing complete!")
    print("=" * 60)

if __name__ == "__main__":
    test_medium_problem()
