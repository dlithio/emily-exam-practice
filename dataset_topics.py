"""
Dataset Topics Library

This module contains 100 diverse dataset topics for problem generation.
Each topic is a domain-only suggestion (1-2 words), giving Claude flexibility
to create appropriate table structures based on the problem requirements.

Topics are organized by category for reference, but Claude can interpret them
freely when generating problems.
"""

DATASET_TOPICS = [
    # Business (10 topics)
    "sales",
    "customers",
    "products",
    "orders",
    "employees",
    "departments",
    "retail",
    "wholesale",
    "consulting",
    "suppliers",

    # Education (8 topics)
    "school",
    "university",
    "courses",
    "tutoring",
    "training",
    "academy",
    "library",
    "workshop",

    # Technology (10 topics)
    "social-media",
    "gaming",
    "software",
    "cloud",
    "cybersecurity",
    "analytics",
    "database",
    "networking",
    "app-store",
    "tech-support",

    # Healthcare (7 topics)
    "hospital",
    "clinic",
    "pharmacy",
    "lab",
    "telemedicine",
    "dentist",
    "veterinary",

    # Entertainment (8 topics)
    "movies",
    "music",
    "streaming",
    "theater",
    "concerts",
    "festivals",
    "gallery",
    "museum",

    # Finance (8 topics)
    "banking",
    "investments",
    "insurance",
    "budgeting",
    "trading",
    "loans",
    "accounting",
    "credit-cards",

    # Sports (8 topics)
    "basketball",
    "soccer",
    "tennis",
    "olympics",
    "fitness",
    "marathon",
    "gym",
    "swimming",

    # E-commerce (6 topics)
    "marketplace",
    "shopping",
    "auctions",
    "subscriptions",
    "reviews",
    "wishlist",

    # Transportation (7 topics)
    "flights",
    "trains",
    "rideshare",
    "logistics",
    "delivery",
    "parking",
    "shipping",

    # Food & Beverage (7 topics)
    "restaurant",
    "cafe",
    "catering",
    "food-truck",
    "bakery",
    "grocery",
    "meal-kit",

    # Real Estate (5 topics)
    "properties",
    "rentals",
    "mortgages",
    "listings",
    "property-management",

    # Travel (6 topics)
    "hotels",
    "tours",
    "bookings",
    "cruises",
    "travel-agency",
    "vacation-rentals",

    # Manufacturing (5 topics)
    "factory",
    "supply-chain",
    "inventory",
    "production",
    "warehouse",

    # Media (5 topics)
    "news",
    "publishing",
    "podcasts",
    "journalism",
    "advertising",
]

# Verify we have exactly 100 topics
assert len(DATASET_TOPICS) == 100, f"Expected 100 topics, got {len(DATASET_TOPICS)}"

# Verify no duplicates
assert len(DATASET_TOPICS) == len(set(DATASET_TOPICS)), "Duplicate topics found"


def get_random_topic():
    """
    Returns a random dataset topic from the library.

    Returns:
        str: A random domain topic
    """
    import random
    return random.choice(DATASET_TOPICS)


if __name__ == "__main__":
    # Verification test
    print(f"Total topics: {len(DATASET_TOPICS)}")
    print(f"Unique topics: {len(set(DATASET_TOPICS))}")
    print("\nSample topics:")
    import random
    sample = random.sample(DATASET_TOPICS, 10)
    for topic in sample:
        print(f"  - {topic}")
    print("\nAll topics are valid!")
