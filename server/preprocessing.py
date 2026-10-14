"""Shared, dependency-free text preprocessing for the NLP pipeline."""
import re
import unicodedata


STOP_WORDS = {
    "a", "an", "and", "are", "am", "as", "at", "be", "can", "do", "for",
    "from", "get", "i", "in", "is", "it", "me", "my", "of", "on", "or",
    "the", "to", "what", "with", "you",
}


def normalize_text(text: str) -> str:
    """Normalize Unicode, case, and whitespace while preserving word boundaries."""
    normalized = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", normalized.lower()).strip()


def tokenize(text: str) -> list[str]:
    """Tokenize normalized text into words and useful numeric values."""
    return re.findall(r"[a-z]+(?:[-'][a-z]+)?|\d+(?:\.\d+)?", normalize_text(text))


def preprocess(text: str) -> list[str]:
    """Return normalized, tokenized content with common stop words removed."""
    return [token for token in tokenize(text) if token not in STOP_WORDS]