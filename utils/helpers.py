"""
helpers.py
Helper functions for UI formatting, input validation, and Streamlit state management.
"""

def validate_inputs(topic: str) -> bool:
    """Check if mandatory inputs are present."""
    return bool(topic and topic.strip())
