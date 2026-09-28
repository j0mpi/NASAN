# entity_extractor.py
import re

from eligibility_matcher import find_scholarships

INTENT_KEYWORDS = {
    "ask_deadline": ["deadline", "due date", "when is", "when's", "cutoff"],
    "ask_requirements": ["requirement", "document", "need to submit", "what do i need", "papers"],
    "ask_process": ["how do i apply", "how to apply", "renew", "renewal", "process", "steps", "procedure"],
    "ask_eligibility": ["qualify", "eligible", "eligibility", "am i", "can i get", "is there a scholarship"],
}

PROGRAM_KEYWORDS = {
    "bsit": "BSIT",
    "bscs": "BSCS",
    "bsba": "BSBA",
    "bsa": "BSA",
    "stem": "STEM",
    "abm": "ABM",
    "humss": "HUMSS",
    "information technology": "BSIT",
    "computer science": "BSCS",
    "business administration": "BSBA",
}

YEAR_LEVEL_KEYWORDS = {
    "incoming first-year": ["incoming first year", "incoming freshman", "graduating senior high", "graduating grade 12"],
    "incoming grade 11": ["incoming grade 11", "incoming grade eleven", "grade 11", "grade eleven", "graduating grade 10"],
    "continuing": ["continuing student", "currently enrolled"],
}

AFFILIATION_KEYWORDS = {
    "PWD": ["pwd", "person with disability", "disability"],
    "family of alumni": ["alumnus", "alumni", "alumna"],
    "sibling of current student": ["sibling", "brother is enrolled", "sister is enrolled"],
    "AFP dependent": ["afp", "armed forces"],
    "BFP dependent": ["bfp", "bureau of fire"],
    "PCG dependent": ["pcg", "coast guard"],
    "PNP dependent": ["pnp", "police"],
    "PMA dependent": ["pma", "philippine military academy"],
    "SM employee family": ["sm employee", "sm affiliate", "works at sm"],
}

YEAR_NUM_PATTERN = re.compile(r"\b([1-4])(?:st|nd|rd|th)\s*year\b")
ORDINALS = {"1": "1st", "2": "2nd", "3": "3rd", "4": "4th"}


def _match_intent(msg: str) -> str:
    for intent, keywords in INTENT_KEYWORDS.items():
        if any(kw in msg for kw in keywords):
            return intent
    if any(re.search(rf"\b{re.escape(g)}\b", msg) for g in ["hi", "hello", "hey", "thanks", "thank you"]):
        return "greet"
    return "out_of_scope"


def _extract_gwa(msg: str):
    match = re.search(r"(?:gwa|cgwa|average)\D{0,10}(\d{1,3}(?:\.\d+)?)", msg)
    if match:
        return float(match.group(1))
    percentage_match = re.search(r"\b(\d{2,3}(?:\.\d+)?)\s*%", msg)
    if percentage_match:
        return float(percentage_match.group(1))
    return None


def _extract_program(msg: str):
    for keyword, label in PROGRAM_KEYWORDS.items():
        if keyword in msg:
            return label
    return None


def _extract_year_level(msg: str):
    num_match = YEAR_NUM_PATTERN.search(msg)
    if num_match:
        return ORDINALS[num_match.group(1)]
    for label, keywords in YEAR_LEVEL_KEYWORDS.items():
        if any(kw in msg for kw in keywords):
            return label
    return None


def _extract_student_type(msg: str):
    if "incoming" in msg and ("first year" in msg or "first-year" in msg or "freshman" in msg):
        return "incoming first-year"
    if "incoming" in msg and ("grade 11" in msg or "grade eleven" in msg):
        return "incoming grade 11"
    if "grade 11" in msg or "grade eleven" in msg:
        return "incoming grade 11"
    if "continuing" in msg or "currently enrolled" in msg:
        return "continuing"
    if YEAR_NUM_PATTERN.search(msg):
        return "continuing"
    if "nu shs" in msg or "nu senior high" in msg:
        return "NU SHS graduate"
    return None


def _extract_affiliation(msg: str):
    for label, keywords in AFFILIATION_KEYWORDS.items():
        if any(kw in msg for kw in keywords):
            return label
    if any(phrase in msg for phrase in ["no affiliation", "none of these", "none"]):
        return "none"
    return None


def _extract_scholarship_name(msg: str):
    if not any(
        marker in msg
        for marker in ["scholarship", "requirement", "document", "deadline", "about", "details"]
    ):
        return None
    matches = find_scholarships(msg)
    return matches[0]["Scholarship Name"] if matches else None


def extract(user_message: str) -> dict:
    msg = user_message.lower().strip()
    entities = {
        "gwa": _extract_gwa(msg),
        "year_level": _extract_year_level(msg),
        "program": _extract_program(msg),
        "student_type": _extract_student_type(msg),
        "affiliation": _extract_affiliation(msg),
        "scholarship_name": _extract_scholarship_name(msg),
    }
    intent = _match_intent(msg)

    if intent == "out_of_scope" and any(v is not None for v in entities.values()):
        intent = "ask_eligibility"
    return {
        "intent": intent,
        "entities": entities,
    }