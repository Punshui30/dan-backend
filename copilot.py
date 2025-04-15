from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import os
import httpx
import json
from typing import AsyncGenerator

router = APIRouter()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = "openai/gpt-4o"
SEARCH_API = "http://localhost:8000/api/search"  # or use full Render URL if needed

class PromptInput(BaseModel):
    prompt: str

async def stream_openrouter(prompt: str) -> AsyncGenerator[str, None]:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
        "stream": True,
        "temperature": 0.6,
        "messages": [
            {"role": "system", "content": "You are DAN, the Operating System. If you detect a command like 'gate in X', but lack route/base_url info, call the /search endpoint with 'API docs for X' and return what you find."},
            {"role": "user", "content": prompt}
        ]
    }

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            async with client.stream("POST", "https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload) as response:
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

    # Detect "gate in" if we want to proactively call /search
    if payload.prompt.lower().startswith("gate in"):
        tool = payload.prompt.split("gate in", 1)[-1].strip().split()[0]
        if tool:
            try:
                async with httpx.AsyncClient(timeout=10) as client:
                    search = await client.get(SEARCH_API, params={"q": f"API docs for {tool}"})
                    hits = search.json().get("results", [])
                    if hits:
                        doc_url = hits[0].get("link", "No link")
                        return StreamingResponse(
                            iter([f"I found documentation for {tool}: {doc_url}. Would you like me to gate it in?"]),
                            media_type="text/plain"
                        )
            except Exception as e:
                print("Web search failed:", str(e))

    return StreamingResponse(stream_openrouter(payload.prompt), media_type="text/plain")
