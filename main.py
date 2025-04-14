from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from copilot import router as copilot_router
from tools import router as tools_router
from search import router as search_router
import os

app = FastAPI()

# CORS (open during dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(copilot_router, prefix="/copilot")
app.include_router(tools_router, prefix="/api")
app.include_router(search_router, prefix="/api")

@app.get("/health")
def health():
    return {"status": "online", "llm": os.getenv("OPENAI_API_KEY") is not None}
