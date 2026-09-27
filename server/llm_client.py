import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from prompts import SYSTEM_PROMPT

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

API_KEY = os.getenv("LLM_API_KEY")
BASE_URL = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1").rstrip("/")

MODEL = os.getenv("LLM_MODEL", "openai/gpt-oss-20b")


def call_llm(user_message: str) -> dict:
    """Call the LLM to parse the user message into intent and entities."""
    if not API_KEY:
        raise RuntimeError("LLM_API_KEY is not configured")

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.1,
        response_format={"type": "json_object"},
    )
    content = response.choices[0].message.content
    return json.loads(content)