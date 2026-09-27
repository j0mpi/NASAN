import re


def route_intent(message: str) -> str | None:
    """
    Returns a simple intent string if the message matches a known pattern.
    Returns None if the query is complex and should be sent to the LLM.
    """
    msg = message.lower().strip()

    greeting_pattern = (
        r"\b(hi|hello|hey|good morning|good afternoon|"
        r"good evening|hola)\b"
    )
    if re.search(greeting_pattern, msg):
        return "greet"

    farewell_pattern = (
        r"\b(bye|goodbye|see you|later|thanks|"
        r"thank you|ty)\b"
    )
    if re.search(farewell_pattern, msg):
        return "goodbye"

    if msg in ["yes", "no", "ok", "okay"]:
        return "simple_affirm"

    return None
