"""
Common functions for the API
"""

import unicodedata

# Normalizes text (accents, case, etc.)
def normalize(text: str) -> str:
    text = text.lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return text