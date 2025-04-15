from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import os
import httpx
import json
from typing import AsyncGenerator

router = APIRouter()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise RuntimeError("OPENROUTER_API_KEY not set in environment")

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openai/gpt-4o"

class PromptInput(BaseModel):
    prompt: str

async def stream_openai(prompt: str) -> AsyncGenerator[str, None]:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
        "stream": True,
        "temperature": 0.6,
        "messages": [
            {
                "role": "system",
                "content": """You are DAN (Dynamic Adaptive Navigator), the AI operating system copilot.

Your core functions include:
- Understanding natural language commands like “gate in slack,” “create a workflow,” or “search the web.”
- Translating those commands into tool actions, adapter calls, and API executions.
- Managing and launching dynamic app windows inside the OS (e.g., Slack, PixVerse).
- Responding concisely with contextual intelligence.

"Gating in" a tool means registering it with the system using its base URL and available actions (routes), so DAN can control it programmatically.
You are NOT just a chatbot. You orchestrate tools and APIs to execute user intent.

Respond clearly. If a command is ambiguous or config is missing, ask for clarification."""
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            async with client.stream("POST", OPENROUTER_URL, headers=headers, json=payload) as response:
                if response.status_code != 200:
                    detail = await response.aread()
                    raise HTTPException(status_code=500, detail=detail.decode())

                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[len("data: "):].strip()
                        if data == "[DONE]":
                            break
                        try:
                            delta = json.loads(data)["choices"][0]["delta"]
                            if "content" in delta:
                                yield delta["content"]
                        except Exception:
                            continue
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Streaming error: {str(e)}")

@router.post("/stream")
async def copilot_stream(payload: PromptInput):
    if not payload.prompt:
        raise HTTPException(status_code=400, detail="Prompt required")
    return StreamingResponse(stream_openai(payload.prompt), media_type="text/plain")
