"""
Claude API client for generating practice problems.
"""
import os
from anthropic import Anthropic

# Default model for problem generation
# Update this to the latest available model from https://docs.anthropic.com/en/docs/models-overview
DEFAULT_MODEL = "claude-sonnet-4-5-20250929"


def get_api_key():
    """
    Get Claude API key from environment variable or Streamlit secrets.

    Returns:
        str: API key

    Raises:
        ValueError: If API key is not found
    """
    # First try environment variable
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if api_key:
        return api_key

    # Try Streamlit secrets if available
    try:
        import streamlit as st
        if "ANTHROPIC_API_KEY" in st.secrets:
            return st.secrets["ANTHROPIC_API_KEY"]
    except (ImportError, FileNotFoundError, KeyError):
        pass

    raise ValueError(
        "ANTHROPIC_API_KEY not found. Please set it as an environment variable "
        "or add it to .streamlit/secrets.toml"
    )


def get_client():
    """
    Get initialized Anthropic client.

    Returns:
        Anthropic: Initialized client
    """
    api_key = get_api_key()
    return Anthropic(api_key=api_key)


def test_api_connection():
    """
    Test basic API call to verify connection works.

    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        client = get_client()
        response = client.messages.create(
            model=DEFAULT_MODEL,
            max_tokens=100,
            messages=[
                {"role": "user", "content": "Say 'API connection successful' and nothing else."}
            ]
        )

        result = response.content[0].text
        print(f"API Response: {result}")
        return True

    except Exception as e:
        print(f"API connection failed: {e}")
        return False


if __name__ == "__main__":
    print("Testing Claude API connection...")
    if test_api_connection():
        print("✓ API connection successful!")
    else:
        print("✗ API connection failed. Please check your API key.")
