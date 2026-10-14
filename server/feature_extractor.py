"""Small TF-IDF feature extractor used for uncertain intent classification."""
import math
from collections import Counter

from preprocessing import preprocess


INTENT_EXAMPLES = {
    "ask_eligibility": [
        "am i eligible for a scholarship",
        "can i qualify based on my grades",
        "is there a scholarship for me",
        "i am a PWD and need scholarship help",
    ],
    "ask_requirements": [
        "what documents do i need",
        "what are the requirements",
        "which papers should i submit",
    ],
    "ask_deadline": [
        "when is the deadline",
        "what is the due date",
        "when should i apply",
    ],
    "ask_process": [
        "how do i apply",
        "how can i renew my scholarship",
        "what are the application steps",
    ],
}


def _terms(tokens: list[str]) -> list[str]:
    bigrams = [f"{left}_{right}" for left, right in zip(tokens, tokens[1:])]
    return tokens + bigrams


def _vectorize(tokens: list[str], vocabulary: list[str], idf: dict[str, float]) -> dict[str, float]:
    counts = Counter(_terms(tokens))
    total = sum(counts.values()) or 1
    return {
        term: (counts[term] / total) * idf[term]
        for term in vocabulary
        if counts[term]
    }


def classify_intent(message: str, threshold: float = 0.18) -> str | None:
    """Classify an otherwise unmatched message using TF-IDF cosine similarity."""
    message_tokens = preprocess(message)
    documents = [preprocess(example) for examples in INTENT_EXAMPLES.values() for example in examples]
    vocabulary = sorted({term for tokens in documents + [message_tokens] for term in _terms(tokens)})
    document_frequency = {
        term: sum(term in _terms(tokens) for tokens in documents)
        for term in vocabulary
    }
    idf = {
        term: math.log((len(documents) + 1) / (frequency + 1)) + 1
        for term, frequency in document_frequency.items()
    }
    message_vector = _vectorize(message_tokens, vocabulary, idf)
    message_norm = math.sqrt(sum(value * value for value in message_vector.values()))
    if not message_norm:
        return None

    best_intent = None
    best_score = 0.0
    for intent, examples in INTENT_EXAMPLES.items():
        for example in examples:
            example_vector = _vectorize(preprocess(example), vocabulary, idf)
            example_norm = math.sqrt(sum(value * value for value in example_vector.values()))
            score = sum(message_vector.get(term, 0) * value for term, value in example_vector.items())
            score /= message_norm * example_norm or 1
            if score > best_score:
                best_intent, best_score = intent, score
    return best_intent if best_score >= threshold else None