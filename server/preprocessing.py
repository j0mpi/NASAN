"""Shared, dependency-free text preprocessing for the NLP pipeline."""
import re
import unicodedata
from difflib import get_close_matches


STOP_WORDS = {
    "a", "an", "and", "are", "am", "as", "at", "be", "can", "do", "for",
    "from", "get", "i", "in", "is", "it", "me", "my", "of", "on", "or",
    "the", "to", "what", "with", "you",
}

DOMAIN_VOCABULARY = {
    "incoming", "freshman", "first", "year", "scholarship", "deadline",
    "requirements", "eligible", "sibling", "alumni", "graduate",
    "application", "apply", "submit", "cutoff", "enrolled", "currently",
}
KNOWN_WORDS = STOP_WORDS | DOMAIN_VOCABULARY | {
    "dad", "mom", "mother", "father", "parent", "brother", "sister",
    "student", "students", "gwa", "cgwa", "student", "nu",
}


def normalize_text(text: str) -> str:
    """Normalize Unicode, case, and whitespace while preserving word boundaries."""
    normalized = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", normalized.lower()).strip()


def correct_domain_typos(text: str) -> str:
    """Correct close domain-word typos without changing numbers or known words."""
    normalized = normalize_text(text)

    def replace(match: re.Match[str]) -> str:
        token = match.group(0)
        if token in KNOWN_WORDS or token.isdigit():
            return token
        matches = get_close_matches(token, DOMAIN_VOCABULARY, n=1, cutoff=0.8)
        return matches[0] if matches else token

    return re.sub(r"[a-z]+|\d+(?:\.\d+)?", replace, normalized)


def tokenize(text: str) -> list[str]:
    """Tokenize normalized text into words and useful numeric values."""
    return re.findall(r"[a-z]+(?:[-'][a-z]+)?|\d+(?:\.\d+)?", normalize_text(text))


def preprocess(text: str) -> list[str]:
    """Return normalized, tokenized content with common stop words removed."""
    return [token for token in tokenize(correct_domain_typos(text)) if token not in STOP_WORDS]