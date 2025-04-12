from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import os

app = FastAPI()

# 🔐 Set your OpenRouter master API key (or use a .env file)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "sk-...")  # Replace with real key

# 🧠 D.A.N. Personality
DAN_PERSONALITY = """
You are D.A.N. OS Mode – Daniel Simmonds Protocol.

Codename: The Architect

You are the digital embodiment of Daniel Simmonds — a visionary builder, rebel, and cultural translator. You operate across bio-digital frontiers: cannabis, psychedelics, blockchain, and AI. You speak plainly, act with precision, and never waste time.

Primary Directives:
- Be direct, practical, and forward-thinking.
- Offer real solutions. No fluff. No hypotheticals.
- Protect user sovereignty, privacy, and security at all times.
- Deliver truth, even if it’s uncomfortable.
- When stuck or losing clarity, initiate a “New Pair of Glasses” protocol to refocus.

Your tone is confident but human. You're empathetic to underdogs and allergic to bureaucracy. Your replies should sound like someone who’s lived it — not theorized it.
"""

# In-memory chat log
context_log = []

class PromptRequest(BaseModel):
    prompt: str

@app.post("/copilot/chat")
async def copilot_chat(request: PromptRequest):
    user_input = request.prompt.strip()
    if not user_input:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")

    # 🕶️ Glasses Protocol
    if "new glasses" in user_input.lower():
        response = (
            "🕶️ D.A.N. is refocusing. Here's a sharper lens...\n\n"
            "Let's re-approach this with tactical clarity and mission-first logic.\n"
            "What exactly do we want to solve right now? Give me the target, and I’ll lock on."
        )
        context_log.append({
            "prompt": user_input,
            "response": response,
            "note": "New Glasses protocol triggered"
        })
        return {"response": response}

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": "https://dan-os.ai",  # optional for analytics
                "X-Title": "DAN Copilot"
            }
            payload = {
                "model": "openrouter/gpt-4o",
                "messages": [
                    {"role": "system", "content": DAN_PERSONALITY.strip()},
                    {"role": "user", "content": user_input}
                ]
            }
            res = await client.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)
            if res.status_code != 200:
                raise HTTPException(status_code=res.status_code, detail=res.text)

            reply = res.json()["choices"][0]["message"]["content"]
            context_log.append({"prompt": user_input, "response": reply})
            return {"response": reply}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/copilot/log")
def get_log():
    return {"log": context_log}

@app.get("/health")
def health_check():
    return {"status": "DAN OS (OpenRouter GPT-4o) backend is healthy."}

