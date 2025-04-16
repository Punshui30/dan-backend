from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import Dict, Any
from uuid import uuid4

router = APIRouter()

# In-memory adapter registry
adapters: Dict[str, Dict[str, Any]] = {}

class AdapterRegistration(BaseModel):
    adapter_id: str
    name: str
    config: Dict[str, Any]

@router.get("/adapters")
def list_adapters():
    return {"adapters": list(adapters.values())}

@router.get("/adapters/{adapter_id}/status")
def get_adapter_status(adapter_id: str):
    adapter = adapters.get(adapter_id.lower())
    if not adapter:
        return {"adapter_id": adapter_id, "status": "not gated"}
    return {"adapter_id": adapter_id, "status": adapter["status"]}

@router.post("/gate")
def gate_in_adapter(reg: AdapterRegistration):
    normalized_id = reg.adapter_id.strip().lower()

    adapter = {
        "id": normalized_id,
        "name": reg.name,
        "description": f"{reg.name} adapter registered",
        "actions": list(reg.config.get("routes", {}).keys()) or ["run"],
        "launchCommand": f"launch:{normalized_id}",
        "status": "ready",
        "config": reg.config,
        "registeredAt": str(uuid4())
    }

    adapters[normalized_id] = adapter
    return adapter

@router.post("/execute")
def execute_command(
    adapter_id: str = Body(...),
    action: str = Body(...),
    params: Dict[str, Any] = Body(default={})
):
    adapter = adapters.get(adapter_id.lower())
    if not adapter:
        raise HTTPException(status_code=404, detail="Adapter not found")

    base_url = adapter["config"].get("base_url")
    route = adapter["config"].get("routes", {}).get(action)

    if not base_url or not route:
        raise HTTPException(
            status_code=400,
            detail=f"Missing base_url or route for action '{action}'"
        )

    return {
        "result": f"✅ Executed '{action}' on '{adapter_id}' with params: {params}"
    }
