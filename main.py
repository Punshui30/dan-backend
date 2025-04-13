from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from router import route_prompt  # This imports the OpenRouter logic

app = FastAPI()

# ✅ CORS fix: allow Netlify and local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://rad-quokka-8deadd.netlify.app",
        "http://localhost:5173",
        "https://zp1v56uxy8rdx5ypatb0ockcb9tr6a-oci3--5173--fb22cd3d.local-credentialless.webcontainer-api.io"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
