# router.py (or inline in main.py)
import requests
import os

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def route_prompt(prompt: str, mode: str = "default") -> str:
    if not OPENROUTER_API_KEY:
        raise Exception("Missing OpenRouter API key")

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "openai/gpt-4",  # or whatever model you want
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload
    )

    if response.status_code != 200:
        raise Exception(f"OpenRouter Error: {response.status_code} - {response.text}")

    data = response.json()
    return data["choices"][0]["message"]["content"]
