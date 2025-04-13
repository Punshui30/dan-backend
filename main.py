from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import os

app = FastAPI()

# ✅ CORS middleware for frontend connection (Netlify, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your Netlify domain for tighter security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔐 Load OpenRouter key from Render environment
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

class PromptRequest(BaseModel):
    prompt: str

@app.post("/copilot/chat")
async def copilot_chat(req: PromptRequest):
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "You are DAN, the OS."},
                    {"role": "user", "content": req.prompt}
                ]
            },
            timeout=30
        )
        data = response.json()
        return {"response": data["choices"][0]["message"]["content"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "DAN backend running"}
