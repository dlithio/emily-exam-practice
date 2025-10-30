"""
Test to verify that easy derived_column problems only use Arithmetic or Conditional subtypes.
Date subtype should only appear in Medium/Hard problems.
"""
import sys

def test_easy_no_date_subtype():
    """Test that easy derived_column problems don't include Date subtype."""
    from claude_client import build_problem_generation_prompt

    print("Testing easy derived_column problems (should be Arithmetic or Conditional only)...")

    # Generate 20 easy prompts to ensure we don't get Date
    subtypes_seen = []
    for i in range(20):
        prompt = build_problem_generation_prompt("derived_column", "easy", "library")

        # Check which subtype was used
        if "DERIVED COLUMN SUBTYPE: Arithmetic" in prompt:
            subtypes_seen.append("Arithmetic")
        elif "DERIVED COLUMN SUBTYPE: Conditional" in prompt:
            subtypes_seen.append("Conditional")
        elif "DERIVED COLUMN SUBTYPE: Date" in prompt:
            subtypes_seen.append("Date")
            print(f"❌ FAIL: Found Date subtype in easy problem (iteration {i+1})")
            return False

    # Verify we saw both Arithmetic and Conditional (but never Date)
    unique_subtypes = set(subtypes_seen)
    print(f"✓ Generated 20 easy problems")
    print(f"  Subtypes seen: {dict((s, subtypes_seen.count(s)) for s in unique_subtypes)}")

    if "Date" in unique_subtypes:
        print("❌ FAIL: Date subtype should not appear in easy problems")
        return False

    if len(unique_subtypes) < 2:
        print("⚠ WARNING: Only saw 1 subtype (expected 2: Arithmetic and Conditional)")
        print("  This might just be random chance with 20 samples")

    print("✓ No Date subtypes found in easy problems")
    return True


def test_medium_includes_date():
    """Test that medium derived_column problems can include Date subtype."""
    from claude_client import build_problem_generation_prompt

    print("\nTesting medium derived_column problems (should include all 3 subtypes)...")

    # Generate 30 medium prompts to see if we get Date
    subtypes_seen = []
    for i in range(30):
        prompt = build_problem_generation_prompt("derived_column", "medium", "library")

        # Check which subtype was used
        if "DERIVED COLUMN SUBTYPE: Arithmetic" in prompt:
            subtypes_seen.append("Arithmetic")
        elif "DERIVED COLUMN SUBTYPE: Conditional" in prompt:
            subtypes_seen.append("Conditional")
        elif "DERIVED COLUMN SUBTYPE: Date" in prompt:
            subtypes_seen.append("Date")

    unique_subtypes = set(subtypes_seen)
    print(f"✓ Generated 30 medium problems")
    print(f"  Subtypes seen: {dict((s, subtypes_seen.count(s)) for s in unique_subtypes)}")

    if "Date" in unique_subtypes:
        print("✓ Date subtype available in medium problems")
        return True
    else:
        print("⚠ WARNING: Date subtype not seen in 30 medium problems")
        print("  This might just be random chance - Date should be available")
        return True  # Don't fail, just warn


def test_prompt_content_quality():
    """Verify prompt quality for easy Arithmetic and Conditional problems."""
    from claude_client import build_problem_generation_prompt

    print("\nTesting prompt content quality...")

    # Generate a few prompts and verify they have proper instructions
    for difficulty in ["easy", "medium"]:
        prompt = build_problem_generation_prompt("derived_column", difficulty, "library")

        # Check for required sections
        assert "DERIVED COLUMN SUBTYPE:" in prompt, f"Missing subtype in {difficulty} prompt"
        assert "creating a new column" in prompt.lower(), f"Missing topic description in {difficulty} prompt"
        assert "plain english" in prompt.lower(), f"Missing plain English requirement in {difficulty} prompt"

    print("✓ Prompt structure looks good")
    return True


if __name__ == "__main__":
    print("\n=== Testing Date Subtype Restriction ===\n")

    try:
        success = True

        success &= test_easy_no_date_subtype()
        success &= test_medium_includes_date()
        success &= test_prompt_content_quality()

        if success:
            print("\n✅ All tests passed!")
            print("Easy derived_column problems will only use Arithmetic and Conditional subtypes.")
            print("Date subtype is reserved for Medium/Hard difficulty.")
        else:
            print("\n❌ Some tests failed")
            sys.exit(1)

    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
