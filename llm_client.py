# llm_client.py
import os
import json
from openai import AsyncOpenAI
from prompts import SYSTEM_PROMPT

# Initialize async client
# For DeepSeek: set base_url="https://api.deepseek.com/v1"
# For OpenAI: use default or set explicitly
client = AsyncOpenAI(
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
)


async def call_llm(user_message: str) -> dict:
    """
    Sends the user message to the LLM asynchronously.
    Returns the parsed JSON as a Python dictionary.
    """
    response = await client.chat.completions.create(
        model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        temperature=0.1,
        response_format={"type": "json_object"}  # Works with OpenAI & DeepSeek
    )

    content = response.choices[0].message.content
    return json.loads(content)
