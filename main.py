from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import os

app = FastAPI()

# === CORS (Allow all for now, lock down later) ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend domain later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === DAN Prompt Personality ===
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

# === Request model ===
class PromptRequest(BaseModel):
    prompt: str

# === OpenRouter call ===
async def query_openrouter(prompt: str) -> str:
    api_key = os.getenv("OPENROUTER_API_KEY")  # You must set this in Render as an env var
    if not api_key:
        raise RuntimeError("Missing OPENROUTER_API_KEY")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://yourfrontend.com",  # Optional but good etiquette
        "X-Title": "DAN-OS"
    }

    body = {
        "model": "mistral",  # Or try "openchat", "gpt-4", "gpt-3.5-turbo", etc.
        "messages": [
            {"role": "system", "content": DAN_PERSONALITY},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post("https://openrouter.ai/api/v1/chat/completions", json=body, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM call failed: {str(e)}")

# === Main Endpoint ===
@app.post("/copilot/chat")
async def copilot_chat(request: PromptRequest):
    result = await query_openrouter(request.prompt)
    return {"response": result}

# === Health Check ===
@app.get("/health")
def health_check():
    return {"status": "D.A.N. OS backend is up and using OpenRouter."}
