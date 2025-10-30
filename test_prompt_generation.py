"""
Test script for Step 5.2: Verify problem generation prompt works correctly.

This script:
1. Builds the problem generation prompt
2. Sends it to Claude API
3. Parses the JSON response
4. Validates the structure
"""

import json
from claude_client import get_client, build_problem_generation_prompt, strip_markdown_code_blocks, DEFAULT_MODEL


def test_prompt_generation(topic: str = "filter_rows", difficulty: str = "easy"):
    """
    Test the problem generation prompt by calling Claude API.

    Args:
        topic: Topic to generate problem for
        difficulty: Difficulty level
    """
    print(f"\n{'='*60}")
    print(f"Testing Problem Generation Prompt")
    print(f"Topic: {topic}, Difficulty: {difficulty}")
    print(f"{'='*60}\n")

    # Step 1: Build the prompt
    print("Step 1: Building prompt...")
    prompt = build_problem_generation_prompt(topic, difficulty)
    print(f"Prompt length: {len(prompt)} characters")
    print(f"\nPrompt preview (first 200 chars):\n{prompt[:200]}...\n")

    # Step 2: Call Claude API
    print("Step 2: Calling Claude API...")
    try:
        client = get_client()
        response = client.messages.create(
            model=DEFAULT_MODEL,
            max_tokens=2000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Extract text response
        response_text = response.content[0].text
        print(f"✓ API call successful!")
        print(f"Response length: {len(response_text)} characters\n")

    except Exception as e:
        print(f"✗ API call failed: {e}")
        return False

    # Step 3: Parse JSON response
    print("Step 3: Parsing JSON response...")
    try:
        # Strip markdown code blocks if present
        cleaned_response = strip_markdown_code_blocks(response_text)
        problem_data = json.loads(cleaned_response)
        print("✓ Valid JSON received!")
    except json.JSONDecodeError as e:
        print(f"✗ JSON parsing failed: {e}")
        print(f"\nRaw response:\n{response_text}")
        print(f"\nCleaned response:\n{cleaned_response}")
        return False

    # Step 4: Validate structure
    print("\nStep 4: Validating structure...")
    required_fields = ["input_tables", "question", "expected_output", "topic", "difficulty"]

    for field in required_fields:
        if field not in problem_data:
            print(f"✗ Missing required field: {field}")
            return False
        print(f"✓ Has field: {field}")

    # Step 5: Display the generated problem
    print(f"\n{'='*60}")
    print("Generated Problem Details")
    print(f"{'='*60}\n")

    print(f"Topic: {problem_data['topic']}")
    print(f"Difficulty: {problem_data['difficulty']}")
    print(f"\nQuestion:\n{problem_data['question']}")

    print(f"\nInput Tables:")
    for table_name, table_data in problem_data['input_tables'].items():
        print(f"\n  Table: {table_name}")
        print(f"  Columns: {table_data['columns']}")
        print(f"  Rows: {len(table_data['data'])}")
        print(f"  Data preview:")
        for i, row in enumerate(table_data['data'][:3], 1):
            print(f"    Row {i}: {row}")
        if len(table_data['data']) > 3:
            print(f"    ... ({len(table_data['data']) - 3} more rows)")

    print(f"\nExpected Output:")
    print(f"  Columns: {problem_data['expected_output']['columns']}")
    print(f"  Rows: {len(problem_data['expected_output']['data'])}")
    print(f"  Data:")
    for i, row in enumerate(problem_data['expected_output']['data'], 1):
        print(f"    Row {i}: {row}")

    # Step 6: Verify format is parseable
    print(f"\n{'='*60}")
    print("Format Verification")
    print(f"{'='*60}\n")

    checks = [
        ("Input tables dict exists", isinstance(problem_data['input_tables'], dict)),
        ("At least one input table", len(problem_data['input_tables']) >= 1),
        ("Question is non-empty string", isinstance(problem_data['question'], str) and len(problem_data['question']) > 0),
        ("Expected output has columns", 'columns' in problem_data['expected_output']),
        ("Expected output has data", 'data' in problem_data['expected_output']),
        ("Topic matches request", problem_data['topic'] == topic),
        ("Difficulty matches request", problem_data['difficulty'] == difficulty),
    ]

    all_passed = True
    for check_name, check_result in checks:
        status = "✓" if check_result else "✗"
        print(f"{status} {check_name}")
        if not check_result:
            all_passed = False

    print(f"\n{'='*60}")
    if all_passed:
        print("✓✓✓ ALL CHECKS PASSED! Prompt is working correctly.")
    else:
        print("✗✗✗ Some checks failed. Prompt needs adjustment.")
    print(f"{'='*60}\n")

    return all_passed


if __name__ == "__main__":
    # Test with different topics
    test_cases = [
        ("filter_rows", "easy"),
        ("group_by", "easy"),
        ("joins", "medium"),
    ]

    print("\n" + "="*60)
    print("TESTING PROBLEM GENERATION PROMPT")
    print("="*60)

    results = []
    for topic, difficulty in test_cases:
        try:
            result = test_prompt_generation(topic, difficulty)
            results.append((topic, difficulty, result))
            print("\n" + "-"*60 + "\n")
        except Exception as e:
            print(f"\n✗ Test failed with exception: {e}\n")
            results.append((topic, difficulty, False))

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    for topic, difficulty, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {topic} ({difficulty})")

    all_passed = all(result for _, _, result in results)
    if all_passed:
        print("\n✓✓✓ All tests passed! Prompt is ready for Step 5.3.")
    else:
        print("\n✗ Some tests failed. Review prompt and try again.")
    print("="*60 + "\n")
