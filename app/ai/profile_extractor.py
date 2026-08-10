import json

from app.ai.gemini_client import client


def extract_profile(message: str):

    prompt = f"""
You are extracting financial profile information
from a user's message.

Return ONLY valid JSON.

Fields:

role:
A user's professional role if mentioned.

interests:
A list of financial sectors or topics mentioned.

watchlist:
A list of companies or stocks mentioned.

If information is not available, use null or [].

User message:
{message}
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
    )

    text = response.text.strip()

    if text.startswith("```"):
        text = text.replace("```json", "")
        text = text.replace("```", "")
        text = text.strip()

    return json.loads(text)