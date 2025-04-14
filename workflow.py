from fastapi import APIRouter, HTTPException, Request
import os
import httpx

router = APIRouter()

@router.post("/workflow/chain")
async def chain_workflow(request: Request):
    try:
        data = await request.json()
        steps = data.get("steps")

        if not steps or not isinstance(steps, list):
            raise HTTPException(status_code=400, detail="A list of steps is required")

        logs = []

        for step in steps:
            if not all(k in step for k in ("adapter_id", "action", "params")):
                raise HTTPException(status_code=400, detail="Each step must include adapter_id, action, and params")

            url = f"/api/execute"
            async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
                response = await client.post(url, json=step)
                response.raise_for_status()
                result = response.json()
                logs.append({"step": step, "result": result})

        return {"workflow": "complete", "log": logs}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow chain failed: {str(e)}")

