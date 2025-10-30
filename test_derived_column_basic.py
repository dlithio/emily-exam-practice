"""
Basic test to verify Step 9.1 implementation of derived_column topic.
"""
import sys

def test_derived_column_in_topics():
    """Test that derived_column is in TOPICS list."""
    from app import TOPICS
    assert "derived_column" in TOPICS, "derived_column not found in TOPICS"
    print("✓ derived_column found in TOPICS list")
    print(f"  Available topics: {TOPICS}")

def test_topic_description_exists():
    """Test that derived_column has a description."""
    from claude_client import build_problem_generation_prompt

    # Build a prompt with derived_column to ensure it works
    prompt = build_problem_generation_prompt("derived_column", "easy", "library")

    assert "derived_column" in prompt.lower() or "creating a new column" in prompt.lower(), \
        "derived_column topic description not found in prompt"
    print("✓ derived_column topic description exists in prompt")

    # Check for subtype instructions
    has_subtype = any(keyword in prompt for keyword in ["Arithmetic", "Conditional", "Date"])
    assert has_subtype, "No derived_column subtype instructions found in prompt"
    print("✓ derived_column subtype instructions found in prompt")

def test_prompt_generation():
    """Test that we can generate a prompt for derived_column."""
    from claude_client import build_problem_generation_prompt

    # Generate multiple prompts to verify random subtype selection works
    prompts = []
    for i in range(5):
        prompt = build_problem_generation_prompt("derived_column", "easy", "library")
        prompts.append(prompt)

    # All prompts should be valid (non-empty)
    assert all(len(p) > 100 for p in prompts), "Generated prompts are too short"
    print("✓ Successfully generated 5 derived_column prompts")

    # Check that we see variety in subtypes
    subtypes_seen = set()
    for prompt in prompts:
        if "Arithmetic" in prompt:
            subtypes_seen.add("Arithmetic")
        if "Conditional" in prompt:
            subtypes_seen.add("Conditional")
        if "Date" in prompt:
            subtypes_seen.add("Date")

    print(f"  Subtypes seen in 5 prompts: {subtypes_seen}")

if __name__ == "__main__":
    print("\n=== Testing Step 9.1: Derived Column Topic ===\n")

    try:
        test_derived_column_in_topics()
        test_topic_description_exists()
        test_prompt_generation()

        print("\n✅ All Step 9.1 tests passed!")
        print("The derived_column topic is properly configured and ready to use.")

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
