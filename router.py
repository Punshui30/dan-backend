import requests

ROUTES = {
    "default": "openai/gpt-4o",
    "fast_parse": "anthropic/claude-3-haiku",
    "creative": "mistralai/mistral-7b-instruct",
    "fallback": "meta-llama/llama-3-8b-chat"
}

def route_prompt(prompt: str, mode: str = "default") -> str:
    model = ROUTES.get(mode, ROUTES["fallback"])
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=60
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"LLM Error: {str(e)}"
