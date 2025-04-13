from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import os
from uuid import uuid4
from typing import Dict, Any

app = FastAPI()

# Load OpenRouter API key from env
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Lock down in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === MODELS ===
class PromptRequest(BaseModel):
    prompt: str

class AdapterRegistration(BaseModel):
    adapter_id: str
    name: str
    config: Dict[str, Any] = {}

class ExecuteRequest(BaseModel):
    adapter_id: str
    action: str
    params: Dict[str, Any]

# === RUNTIME STATE ===
adapters: Dict[str, Dict[str, Any]] = {}

# === ROUTES ===

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

@app.post("/api/gate")
def gate_in(reg: AdapterRegistration):
    adapter_id = reg.adapter_id.lower().strip()
    adapter = {
        "id": adapter_id,
        "name": reg.name or adapter_id.title(),
        "description": f"{reg.name or adapter_id} adapter registered dynamically",
        "actions": ["run", "launch:" + adapter_id],
        "launchCommand": f"launch:{adapter_id}",
        "config": reg.config,
        "status": "ready"
    }
    adapters[adapter_id] = adapter
    return adapter

@app.get("/api/adapters")
def list_adapters():
    return {"adapters": list(adapters.values())}

@app.get("/api/adapters/{adapter_id}/status")
def adapter_status(adapter_id: str):
    adapter = adapters.get(adapter_id.lower())
    if not adapter:
        raise HTTPException(status_code=404, detail="Adapter not found")
    return {"adapter_id": adapter_id, "status": adapter.get("status", "unknown")}

@app.post("/api/execute")
def execute(req: ExecuteRequest):
    adapter = adapters.get(req.adapter_id.lower())
    if not adapter:
        raise HTTPException(status_code=404, detail="Adapter not found")
    return {
        "result": f"✅ Executed '{req.action}' on adapter '{req.adapter_id}' with params {req.params}"
    }

@app.get("/health")
def health():
    return {"status": "running", "adapters": list(adapters.keys())}
