from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
from uuid import uuid4
import os
import requests

app = FastAPI()

# Load OpenRouter key
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise RuntimeError("OPENROUTER_API_KEY not set in environment")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Lock down in production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory registry
adapters: Dict[str, Dict[str, Any]] = {}

# === Models ===
class PromptRequest(BaseModel):
    prompt: str

class AdapterRegistration(BaseModel):
    adapter_id: str
    name: str
    config: Dict[str, Any] = {}

class ExecuteRequest(BaseModel):
    adapter_id: str
    action: str
    params: Dict[str, Any] = {}

# === Routes ===

@app.get("/health")
def health_check():
    return {"status": "online", "adapters": list(adapters.keys())}

@app.post("/copilot/chat")
def chat_with_dan(req: PromptRequest):
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
        raise HTTPException(status_code=500, detail=f"Copilot error: {str(e)}")

@app.post("/api/gate")
def gate_in_adapter(reg: AdapterRegistration):
    adapter_id = reg.adapter_id.strip().lower()
    if not adapter_id:
        raise HTTPException(status_code=400, detail="Adapter ID is required")

    adapter = {
        "id": adapter_id,
        "name": reg.name or adapter_id.title(),
        "description": f"{reg.name or adapter_id} adapter registered dynamically",
        "actions": list(reg.config.get("routes", {}).keys()) or ["run"],
        "launchCommand": f"launch:{adapter_id}",
        "status": "ready",
        "config": reg.config,
        "registeredAt": str(uuid4())
    }

    adapters[adapter_id] = adapter
    return adapter

@app.get("/api/adapters")
def list_adapters():
    return {"adapters": list(adapters.values())}

@app.get("/api/adapters/{adapter_id}/status")
def get_adapter_status(adapter_id: str):
    adapter = adapters.get(adapter_id.lower())
    if not adapter:
        raise HTTPException(status_code=404, detail="Adapter not found")
    return {"adapter_id": adapter_id, "status": adapter["status"]}

@app.post("/api/execute")
def execute_command(req: ExecuteRequest):
    adapter = adapters.get(req.adapter_id.lower())
    if not adapter:
        raise HTTPException(status_code=404, detail="Adapter not found")

    base_url = adapter["config"].get("base_url")
    routes = adapter["config"].get("routes", {})
    route = routes.get(req.action)

    if not base_url or not route:
        raise HTTPException(status_code=400, detail="Adapter missing base_url or route for action")

    try:
        url = f"{base_url.rstrip('/')}/{route.lstrip('/')}"
        resp = requests.post(url, json=req.params, timeout=15)
        resp.raise_for_status()
        return {"result": resp.json()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Adapter execution failed: {str(e)}")
