from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any
from uuid import uuid4

router = APIRouter()

# In-memory adapter registry
adapters: Dict[str, Dict[str, Any]] = {}

@router.get("/adapters")
def list_adapters():
    return {"adapters": list(adapters.values())}

@router.get("/adapters/{adapter_id}")
def get_adapter_details(adapter_id: str):
    adapter = adapters.get(adapter_id.lower())
    if not adapter:
        raise HTTPException(status_code=404, detail="Adapter not found")
    return adapter

@router.get("/adapters/{adapter_id}/status")
def get_adapter_status(adapter_id: str):
    adapter = adapters.get(adapter_id.lower())
    if not adapter:
        return {"adapter_id": adapter_id, "status": "not gated"}
    return {"adapter_id": adapter_id, "status": adapter["status"]}

@router.put("/adapters/{adapter_id}")
def update_adapter_config(adapter_id: str, config: Dict[str, Any] = Body(...)):
    normalized_id = adapter_id.lower()
    adapter = adapters.get(normalized_id)
    if not adapter:
        raise HTTPException(status_code=404, detail="Adapter not found")

    adapter["config"] = config
    return adapter

@router.post("/gate")
def gate_in_adapter(
    adapter_id: str = Body(...),
    name: str = Body(...),
    config: Dict[str, Any] = Body(...)
):
    normalized_id = adapter_id.strip().lower()

    adapter = {
        "id": normalized_id,
        "name": name,
        "description": f"{name} adapter registered",
        "actions": list(config.get("routes", {}).keys()) or ["run"],
        "launchCommand": f"launch:{normalized_id}",
        "status": "ready",
        "config": config,
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

    # Simulated behavior — actual POST request optional here
    return {
        "result": f"✅ Executed '{action}' on '{adapter_id}' with params: {params}"
    }
