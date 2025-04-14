from fastapi import APIRouter, HTTPException, Query
import os
import httpx

router = APIRouter()

SERPER_KEY = os.getenv("SERPER_KEY")
SERPER_URL = "https://google.serper.dev/search"

if not SERPER_KEY:
    raise RuntimeError("SERPER_KEY not set in .env or Render env")

@router.get("/search")
async def search_web(q: str = Query(..., description="Search query")):
    headers = {
        "X-API-KEY": SERPER_KEY,
        "Content-Type": "application/json"
    }
    payload = {"q": q}

    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(SERPER_URL, json=payload, headers=headers)
            res.raise_for_status()
            data = res.json()
            return {"results": data.get("organic", [])[:5]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

