"""
Difficulty Manager - Skill Composition Logic

This module handles skill selection and composition for different difficulty levels.
It determines which skills to combine and whether to require CTEs in SQL solutions.
"""

import random
from typing import List, Tuple


# All easy-level topics (foundational skills)
EASY_SKILLS = [
    "filter_columns",
    "filter_rows",
    "aggregations",
    "distinct",
    "joins",
    "order_by",
    "limit",
    "derived_column"
]


def select_skills_for_difficulty(difficulty: str, selected_topics: List[str]) -> List[str]:
    """
    Selects skills to combine based on difficulty level.

    Args:
        difficulty: "easy", "medium", or "hard"
        selected_topics: List of topics user selected (empty = all)

    Returns:
        List of skill names to combine

    Examples:
        >>> select_skills_for_difficulty("easy", [])
        ['filter_rows']  # One random skill

        >>> select_skills_for_difficulty("medium", [])
        ['filter_rows', 'aggregations']  # 2-3 skills

        >>> select_skills_for_difficulty("hard", ["filter_rows", "joins"])
        ['filter_rows', 'joins']  # 2-4 skills from available
    """
    # Use selected topics if provided, otherwise use all easy skills
    available_skills = selected_topics if selected_topics else EASY_SKILLS

    # Ensure we have at least one skill available
    if not available_skills:
        available_skills = EASY_SKILLS

    if difficulty == "easy":
        # Easy: Single skill
        return [random.choice(available_skills)]

    elif difficulty == "medium":
        # Medium: 2-3 skills
        num_skills = random.choice([2, 3])
        # Ensure we don't try to sample more skills than available
        num_skills = min(num_skills, len(available_skills))
        return random.sample(available_skills, num_skills)

    elif difficulty == "hard":
        # Hard: 3-4 skills
        num_skills = random.choice([3, 4])
        # Ensure we don't try to sample more skills than available
        num_skills = min(num_skills, len(available_skills))
        return random.sample(available_skills, num_skills)

    else:
        # Default to easy if unknown difficulty
        return [random.choice(available_skills)]


def should_use_cte(difficulty: str, skills: List[str]) -> Tuple[bool, int]:
    """
    Determines whether to use CTEs (Common Table Expressions) in SQL solutions.

    Args:
        difficulty: "easy", "medium", or "hard"
        skills: List of skills being tested (used for hard difficulty logic)

    Returns:
        Tuple of (use_cte: bool, num_ctes: int)
        - use_cte: Whether to require CTEs in SQL solution
        - num_ctes: Number of CTEs to require (0 if use_cte is False)

    Logic:
        - Easy: Never use CTEs
        - Medium: 50% chance of using 1 CTE
        - Hard: Always use CTEs (1-3 depending on number of skills)

    Examples:
        >>> should_use_cte("easy", ["filter_rows"])
        (False, 0)

        >>> should_use_cte("medium", ["filter_rows", "aggregations"])
        (True, 1)  # or (False, 0) - 50% random

        >>> should_use_cte("hard", ["filter_rows", "aggregations", "joins", "order_by"])
        (True, 2)  # or (True, 3) - depends on number of skills
    """
    if difficulty == "easy":
        # Easy problems never use CTEs
        return False, 0

    elif difficulty == "medium":
        # Medium problems: 50% chance of using 1 CTE
        use_cte = random.random() < 0.5
        return use_cte, 1 if use_cte else 0

    elif difficulty == "hard":
        # Hard problems always use CTEs
        # More skills = more likely to need more CTEs
        num_skills = len(skills)

        if num_skills >= 4:
            # 4+ skills: Use 2-3 CTEs
            num_ctes = random.choice([2, 3])
        elif num_skills >= 3:
            # 3 skills: Use 1-3 CTEs
            num_ctes = random.choice([1, 2, 3])
        else:
            # 2 or fewer skills: Use 1-2 CTEs
            num_ctes = random.choice([1, 2])

        return True, num_ctes

    else:
        # Default to no CTEs for unknown difficulty
        return False, 0


if __name__ == "__main__":
    # Simple test to demonstrate functionality
    print("=== Difficulty Manager Test ===\n")

    # Test easy difficulty
    print("Easy difficulty (10 samples):")
    for i in range(10):
        skills = select_skills_for_difficulty("easy", [])
        use_cte, num_ctes = should_use_cte("easy", skills)
        print(f"  {i+1}. Skills: {skills} | CTE: {use_cte} ({num_ctes})")

    print("\nMedium difficulty (10 samples):")
    for i in range(10):
        skills = select_skills_for_difficulty("medium", [])
        use_cte, num_ctes = should_use_cte("medium", skills)
        print(f"  {i+1}. Skills: {skills} | CTE: {use_cte} ({num_ctes})")

    print("\nHard difficulty (10 samples):")
    for i in range(10):
        skills = select_skills_for_difficulty("hard", [])
        use_cte, num_ctes = should_use_cte("hard", skills)
        print(f"  {i+1}. Skills: {skills} | CTE: {use_cte} ({num_ctes})")

    print("\nWith selected topics (medium difficulty):")
    selected = ["filter_rows", "aggregations", "joins"]
    for i in range(5):
        skills = select_skills_for_difficulty("medium", selected)
        use_cte, num_ctes = should_use_cte("medium", skills)
        print(f"  {i+1}. Skills: {skills} | CTE: {use_cte} ({num_ctes})")
