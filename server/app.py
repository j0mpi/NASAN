# app.py
import os
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from router import route_intent
from entity_extractor import extract
from eligibility_matcher import SCHOLARSHIPS, find_matches

load_dotenv()

app = Flask(__name__)
CORS(app)

ROUTER_RESPONSES = {
    "greet": "Hi! I'm here to help you find a scholarship that fits your situation.",
    "goodbye": "Take care! Come back anytime you need help with scholarships.",
    "simple_affirm": "Great. What else can I help you with?",
}

USE_LLM = os.getenv("USE_LLM", "false").lower() == "true"


def _best_match(results: list[dict]) -> list[dict]:
    """Return one deterministic best option after the profile is complete."""
    def score(scholarship: dict) -> tuple[int, int]:
        minimum = scholarship["Minimum GWA"]
        numeric = 0.0
        match = re.search(r"(\d+(?:\.\d+)?)", minimum)
        if match:
            numeric = float(match.group(1))
        return (int(numeric * 100), -len(scholarship["Scholarship Name"]))

    return sorted(results, key=score, reverse=True)[:1]


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "Missing 'message' field"}), 400

    user_msg = data["message"].strip()
    if not user_msg:
        return jsonify({"error": "Message cannot be empty"}), 400

    previous_entities = data.get("context", {})
    if not isinstance(previous_entities, dict):
        previous_entities = {}

    # Step 1: lightweight router for greetings/farewells/simple affirmations
    simple_intent = route_intent(user_msg)
    if simple_intent:
        reply = ROUTER_RESPONSES.get(simple_intent, "I understand.")
        return jsonify({
            "intent": simple_intent,
            "entities": None,
            "reply": reply,
            "results": [],
            "source": "router",
        })

    # Step 2: intent and entity extraction. 
    source = "rules"
    if USE_LLM:
        from llm_client import call_llm
        try:
            parsed = call_llm(user_msg)
            source = "llm"
        except Exception as e:
            print(f"LLM call failed, falling back to rules: {e}")
            parsed = extract(user_msg)
    else:
        parsed = extract(user_msg)

    intent = parsed.get("intent")
    entities = dict(parsed.get("entities") or {})

    rule_entities = extract(user_msg)

    for key, value in rule_entities.get("entities", {}).items():
        if entities.get(key) is None and value is not None:
            entities[key] = value
    for key, value in previous_entities.items():
        if entities.get(key) is None and value is not None:
            entities[key] = value
    if rule_entities.get("intent") == "ask_list":
        intent = "ask_list"
    if intent == "out_of_scope" and any(
        entities.get(key) is not None
        for key in ("gwa", "year_level", "program", "student_type", "affiliation")
    ):
        intent = "ask_eligibility"

    # Step 3: route by intent
    options = []
    if intent == "ask_list":
        results = SCHOLARSHIPS
        reply = "Here are the scholarships currently available at NU."
    elif intent == "ask_eligibility":
        results = find_matches(entities)
        if not entities.get("student_type"):
            results = []
            reply = "To narrow this down, are you an incoming first-year student, an incoming Grade 11 student, or a continuing student?"
            options = ["Incoming First Year", "Incoming Grade 11", "Continuing Student"]
        elif not entities.get("gwa") and entities.get("affiliation") not in ("none",):
            results = []
            if entities.get("student_type") == "continuing":
                reply = "Thanks. What is your CGWA? For example, you can reply with 3.50 CGWA."
            else:
                reply = "Thanks. What is your GWA percentage? For example, you can reply with 90% GWA."
        elif (
            not entities.get("affiliation")
            and len(find_matches(entities, allow_missing_affiliation=True)) > len(results)
        ):
            results = []
            reply = "One last detail: does any of the following apply to you: PWD, NU alumnus family, sibling currently enrolled at NU, AFP/BFP/PCG/PNP/PMA dependent, or SM employee family? Choose one below, or select None."
            options = ["PWD", "NU Alumnus Family", "Sibling Currently Enrolled", "AFP/BFP/PCG/PNP/PMA Dependent", "SM Employee Family", "None"]
        elif results:
            results = _best_match(results)
            reply = f"Based on your answers, this is the most applicable scholarship: {results[0]['Scholarship Name']}."
        else:
            reply = "I couldn't find a scholarship that matches the details you provided. Please contact Student Developement Academic Office (SDAO) for help with the next steps."
    elif intent in ("ask_requirements", "ask_deadline"):
        results = find_matches(entities) if entities.get("scholarship_name") else []
        if not results:
            reply = "Which scholarship would you like to know more about? Share its name and I'll look up the exact details."
        elif intent == "ask_requirements":
            reply = f"Here are the documents listed for {results[0]['Scholarship Name']}."
        else:
            reply = f"The scholarship list shows this deadline for {results[0]['Scholarship Name']}: {results[0]['Deadline']}."
    elif intent == "ask_process":
        results = []
        reply = "The scholarship list does not include the current application or renewal steps. Please contact the Student Developement Academic Office (SDAO) for guidance."
    else:
        results = []
        reply = "I can help you check eligibility, required documents, deadlines, or application steps. Could you tell me a little more about what you need?"

    return jsonify({
        "intent": intent,
        "entities": entities,
        "reply": reply,
        "results": results,
        "options": options,
        "source": source,
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)