from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import os
import httpx
import json
from typing import AsyncGenerator

router = APIRouter()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
MODEL = "gpt-4o"

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY not set in environment")

class PromptInput(BaseModel):
    prompt: str

async def stream_openai(prompt: str) -> AsyncGenerator[str, None]:
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
        "stream": True,
        "temperature": 0.6,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are DAN, the Operating System Copilot. Your job is to receive natural language commands "
                    "from the user and determine if a tool needs to be gated in (i.e., integrated). "
                    "If the user says something like 'gate in Slack', you should call the /api/gate endpoint and load the tool UI.\n\n"
                    "Do NOT explain what Slack is or how to use it. You are not a support agent — you are an AI orchestrator.\n\n"
                    "Your responsibilities:\n"
                    "- Gate in tools when asked\n"
                    "- Chain tools together into workflows\n"
                    "- Trigger commands or actions via adapters\n"
                    "- Answer questions only when no action is needed\n\n"
                    "Use short, precise responses. Show intent to execute actions or explain why something cannot be executed.\n\n"
                    "Example:\n"
                    "User: gate in slack\n"
                    "DAN: ✅ Gating in Slack..."
                )
            },
            { "role": "user", "content": prompt }
        ]
    }

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            async with client.stream("POST", OPENAI_API_URL, headers=headers, json=payload) as response:
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
