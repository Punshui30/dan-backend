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
BACKEND_URL = os.getenv("BACKEND_URL", "https://dan-backend-1.onrender.com")

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
            {"role": "system", "content": "You are DAN, the OS. Respond with clarity and precision. You have access to live web search via /api/search and can return useful tool documentation links."},
            {"role": "user", "content": prompt}
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

    # ✅ Fallback: If prompt includes "gate in" but DAN has no config, search API docs
    if "gate in" in payload.prompt.lower():
        try:
            tool_name = payload.prompt.lower().split("gate in", 1)[1].strip().split()[0]
            async with httpx.AsyncClient(timeout=10) as client:
                res = await client.get(
                    f"{BACKEND_URL}/api/search",
                    params={"q": f"{tool_name} API documentation"}
                )
                if res.status_code == 200:
                    docs = res.json().get("results", [])
                    if docs:
                        top_link = docs[0].get("link", "")
                        return {"response": f"I found documentation for {tool_name}: {top_link}"}
        except Exception as e:
            print(f"[DAN Search fallback error]: {e}")

    return StreamingResponse(stream_openai(payload.prompt), media_type="text/plain")

   
