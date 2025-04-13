from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from router import route_prompt  # This imports the OpenRouter logic

app = FastAPI()

class PromptRequest(BaseModel):
    prompt: str
    mode: str = "default"  # optional LLM mode (e.g., "creative", "fast_parse")

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
