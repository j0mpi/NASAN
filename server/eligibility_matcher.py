# eligibility_matcher.py
"""
Matches extracted entities against scholarships.json.

Kept separate from the extractor so either the rule-based extractor or the
real DeepSeek call_llm can feed it, since both return the same entities shape.
"""
import json
import os
import re
import unicodedata

SCHOLARSHIPS_PATH = os.path.join(os.path.dirname(__file__), "scholarships.json")

with open(SCHOLARSHIPS_PATH, "r", encoding="utf-8") as f:
    SCHOLARSHIPS = json.load(f)


def _parse_min_gwa(value: str):
    """scholarships.json stores minimums either as a percentage ('97%') or
    as descriptive text ('3.00 CGWA and above'). Returns (scale, number)
    or None if there's no usable minimum."""
    if not value or value == "Not specified":
        return None
    pct_match = re.match(r"(\d{1,3}(?:\.\d+)?)\s*%", value)
    if pct_match:
        return ("percent", float(pct_match.group(1)))
    cgwa_match = re.search(r"(\d\.\d+)\s*CGWA", value)
    if cgwa_match:
        return ("gpa", float(cgwa_match.group(1)))
    return None


def _gwa_qualifies(entity_gwa, scholarship_min_gwa: str) -> bool:
    if entity_gwa is None:
        return True
    parsed = _parse_min_gwa(scholarship_min_gwa)
    if parsed is None:
        return True
    scale, minimum = parsed
    # Both of NU's scales run in the same direction: higher is better.
    # "percent" is the 0-100 high school scale (incoming first-year scholarships).
    # "gpa" is NU's own 0.0-4.0 CGWA scale (4.0 = Excellent), used for continuing students.
    if scale == "gpa" and entity_gwa > 4:
        return False
    if scale in ("percent", "gpa"):
        return entity_gwa >= minimum
    return True


def _normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def _name_tokens(value: str) -> set[str]:
    ignored = {
        "the", "program", "scholarship", "scholar", "discount", "benefit", "inc", "and",
        "what", "which", "where", "when", "how", "do", "does", "is", "are", "for",
        "my", "me", "i", "need", "documents", "document", "requirements", "requirement",
        "deadline", "about", "of", "the", "please", "tell", "give",
            "with", "student", "students", "continuing", "gwa", "eligible", "eligibility", "qualify", "qualified",
    }
    return {
        token
        for token in _normalize_text(value).split()
        if token not in ignored and len(token) > 1
    }


def find_scholarships(query: str) -> list[dict]:
    """Find catalog records whose names or distinctive terms match a query."""
    query_text = _normalize_text(query)
    query_tokens = _name_tokens(query)
    scored = []
    for scholarship in SCHOLARSHIPS:
        name = scholarship["Scholarship Name"]
        name_text = _normalize_text(name)
        name_tokens = _name_tokens(name)
        score = 0
        if name_text in query_text or query_text in name_text:
            score += 100
        score += len(query_tokens & name_tokens) * 10
        query_words = query_text.split()
        name_words = name_text.split()  # This line remains unchanged
        if any(
            len(query_words) >= 2
            and len(query_words[index]) > 1
            and len(query_words[index + 1]) > 1
            and " ".join(query_words[index:index + 2]) in name_text
            for index in range(len(query_words) - 1)
        ):
            score += 60
        if re.search(r"\buaeb\b", query_text) and "uaeb" in name_text:
            score += 100
        if re.search(r"\bpwd\b", query_text) and "people with disability" in name_text:
            score += 100
        if re.search(r"\bsm\b", query_text) and "sm" in name_text:
            score += 100
        if score:
            scored.append((score, scholarship))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [scored[0][1]] if scored else []


def _year_level_qualifies(entity_year_level, scholarship_restriction: str, student_type=None) -> bool:
    if not entity_year_level and not student_type:
        return True
    restriction = scholarship_restriction.lower()
    if "all levels" in restriction:
        return True
    if student_type and student_type.lower() in restriction:
        return True
    return bool(entity_year_level and entity_year_level.lower() in restriction)


def _program_qualifies(entity_program, scholarship_program: str) -> bool:
    if not entity_program:
        return True
    program = scholarship_program.lower()
    if "all" in program:
        return True
    return entity_program.lower() in program


def _affiliation_qualifies(entity_affiliation, scholarship_employment: str) -> bool:
    employment = scholarship_employment.lower()
    required_affiliation_terms = (
        "family member", "alumnus", "sibling", "person with a disability",
        "dependent", "employee of", "employee's", "employee",
    )
    if not entity_affiliation:
        return not any(term in employment for term in required_affiliation_terms)
    if entity_affiliation == "none":
        return not any(term in employment for term in required_affiliation_terms)
    affiliation_terms = {
        "PWD": ["pwd", "disability"],
        "family of alumni": ["alumni", "alumnus", "alumna"],
        "sibling of current student": ["sibling", "currently enrolled"],
        "AFP dependent": ["afp", "armed forces"],
        "BFP dependent": ["bfp", "fire protection"],
        "PCG dependent": ["pcg", "coast guard"],
        "PNP dependent": ["pnp", "police"],
        "PMA dependent": ["pma", "military academy"],
        "SM employee family": ["sm", "affiliate"],
    }
    return any(term in employment for term in affiliation_terms.get(entity_affiliation, [entity_affiliation.lower()]))


def find_matches(entities: dict, allow_missing_affiliation: bool = False) -> list:
    gwa = entities.get("gwa")
    year_level = entities.get("year_level")
    student_type = entities.get("student_type")
    program = entities.get("program")
    affiliation = entities.get("affiliation")
    scholarship_name = entities.get("scholarship_name")
    name_matches = find_scholarships(scholarship_name) if scholarship_name else SCHOLARSHIPS
    name_match_ids = {id(scholarship) for scholarship in name_matches}

    matches = []
    for scholarship in SCHOLARSHIPS:
        if id(scholarship) not in name_match_ids:
            continue
        if not _gwa_qualifies(gwa, scholarship["Minimum GWA"]):
            continue
        if not _year_level_qualifies(year_level, scholarship["Year Level restrictions"], student_type):
            continue
        if not _program_qualifies(program, scholarship["Specific Program"]):
            continue
        if (
            not scholarship_name
            and not allow_missing_affiliation
            and not _affiliation_qualifies(affiliation, scholarship["Employment status preference"])
        ) or (
            affiliation
            and not _affiliation_qualifies(affiliation, scholarship["Employment status preference"])
        ):
            continue
        matches.append(scholarship)
    return matches