# app.py
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from router import route_intent
from llm_client import call_llm

app = Flask(__name__)
CORS(app)  # Allow frontend to call this API

# Simple canned responses for the lightweight router
ROUTER_RESPONSES = {
    "greet": "Hello! How can I help you with your scholarship questions today?",
    "goodbye": "Goodbye! Feel free to come back if you have more questions.",
    "simple_affirm": "Great! Let me know if you need more help."
}


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "Missing 'message' field"}), 400

    user_msg = data["message"].strip()
    if not user_msg:
        return jsonify({"error": "Message cannot be empty"}), 400

    # Step 1: Check lightweight router
    simple_intent = route_intent(user_msg)
    if simple_intent:
        reply = ROUTER_RESPONSES.get(simple_intent, "I understand.")
        return jsonify({
            "intent": simple_intent,
            "entities": None,
            "reply": reply,
            "source": "router"  # Indicates no LLM call
        })

    # Step 2: Complex query -> send to LLM
    try:
        llm_output = call_llm(user_msg)

        # You might want to add basic validation here
        # (e.g., ensure 'intent' and 'entities' keys exist)

        # For now, we also generate a default reply so the frontend has something to show.
        # On Day 4-5, we will replace this with the actual Eligibility Matcher logic.
        reply = "I received your query. Let me check your eligibility..."

        return jsonify({
            "intent": llm_output.get("intent"),
            "entities": llm_output.get("entities"),
            "reply": reply,
            "source": "llm"
        })

    except Exception as e:
        return jsonify({"error": f"LLM processing failed: {str(e)}"}), 500


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
