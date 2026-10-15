"""Reproducible evaluation for NASAN's intent and entity extraction pipeline.

Run from the repository root with: python server/evaluate.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from entity_extractor import extract


CASES = [
    ("ask_eligibility", "I am a 3rd year BSIT student with a GWA of 1.75"),
    ("ask_eligibility", "Can I qualify if I am a continuing student with 3.25 CGWA?"),
    ("ask_eligibility", "I am an incoming freshman with 92% GWA"),
    ("ask_eligibility", "I am a PWD and need scholarship help"),
    ("ask_requirements", "What documents do I need for the Gold Scholar?"),
    ("ask_requirements", "Which papers should I submit for this scholarship?"),
    ("ask_deadline", "When is the application due date?"),
    ("ask_deadline", "Tell me the scholarship cutoff"),
    ("ask_deadline", "Until what date can I send in my application"),
    ("ask_deadline", "What is the last day to apply"),
    ("ask_deadline", "When should I submit"),
    ("ask_deadline", "Cutoff for applications"),
    ("ask_process", "How can I renew my scholarship?"),
    ("ask_process", "What are the application steps?"),
    ("out_of_scope", "Can you help me write a chemistry essay?"),
    ("out_of_scope", "What is the weather today?"),
]


def _metrics(expected: list[str], predicted: list[str]) -> dict:
    labels = sorted(set(expected) | set(predicted))
    matrix = {label: {other: 0 for other in labels} for label in labels}
    for actual, guess in zip(expected, predicted):
        matrix[actual][guess] += 1

    per_class = {}
    for label in labels:
        true_positive = matrix[label][label]
        false_positive = sum(matrix[other][label] for other in labels if other != label)
        false_negative = sum(matrix[label][other] for other in labels if other != label)
        precision = true_positive / (true_positive + false_positive) if true_positive + false_positive else 0
        recall = true_positive / (true_positive + false_negative) if true_positive + false_negative else 0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0
        per_class[label] = {"precision": precision, "recall": recall, "f1": f1}

    accuracy = sum(actual == guess for actual, guess in zip(expected, predicted)) / len(expected)
    return {"accuracy": accuracy, "per_class": per_class, "confusion_matrix": matrix}


def main() -> None:
    expected = [label for label, _ in CASES]
    predictions = [extract(message)["intent"] for _, message in CASES]
    report = _metrics(expected, predictions)
    report["sample_conversations"] = [
        {"user": message, "intent": prediction}
        for (_, message), prediction in zip(CASES, predictions)
    ]
    report["errors"] = [
        {"user": message, "expected": actual, "predicted": prediction}
        for (actual, message), prediction in zip(CASES, predictions)
        if actual != prediction
    ]
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()