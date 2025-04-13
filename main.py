from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from router import route_prompt  # Handles OpenRouter calls

app = FastAPI()  # ✅ REQUIRED for Render to find your app

class PromptRequest(BaseModel):
    prompt: str
    mode: str = "default"

@app.post("/copilot/chat")
async def copilot_chat(req: PromptRequest):
    try:
        response = route_prompt(req.prompt, req.mode)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "OpenRouter backend is active"}
