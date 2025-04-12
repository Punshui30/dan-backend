from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

app = FastAPI()

# ✅ CORS middleware to allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Optional: Replace "*" with your frontend URL for tighter control
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lazy-loaded model + tokenizer
model = None
tokenizer = None

def load_model():
    global model, tokenizer
    if model is None or tokenizer is None:
        model_name = "tiiuae/falcon-7b-instruct"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float32,
            device_map={"": "cpu"}
        )

# In-memory context log
context_log = []

# D.A.N. Personality
DAN_PERSONALITY = """
You are D.A.N. OS Mode – Daniel Simmonds Protocol.

Codename: The Architect

You are the digital embodiment of Daniel Simmonds — a visionary builder, rebel, and cultural translator. You operate across bio-digital frontiers: cannabis, psychedelics, blockchain, and AI. You speak plainly, act with precision, and never waste time.

Primary Directives:
- Be direct, practical, and forward-thinking.
- Offer real solutions. No fluff. No hypotheticals.
- Protect user sovereignty, privacy, and security at all times.
- Deliver truth, even if it’s uncomfortable.
- When stuck or losing clarity, initiate a “New Pair of Glasses” protocol to refocus.

Your tone is confident but human. You're empathetic to underdogs and allergic to bureaucracy. Your replies should sound like someone who’s lived it — not theorized it.
"""

class PromptRequest(BaseModel):
    prompt: str

@app.post("/copilot/chat")
async def copilot_chat(request: PromptRequest):
    try:
        load_model()

        user_input = request.prompt.strip()

        if "new glasses" in user_input.lower():
            response = (
                "🕶️ D.A.N. is refocusing. Here's a sharper lens...\n\n"
                "Let's re-approach this with tactical clarity and mission-first logic.\n"
                "What exactly do we want to solve right now? Give me the target, and I’ll lock on."
            )
            context_log.append({
                "prompt": user_input,
                "response": response,
                "note": "New Glasses protocol triggered"
            })
            return {"response": response}

        full_prompt = DAN_PERSONALITY.strip() + "\n\n" + user_input
        inputs = tokenizer(full_prompt, return_tensors="pt", truncation=True, max_length=512)
        output = model.generate(
            **inputs,
            max_length=1024,
            num_return_sequences=1,
            pad_token_id=tokenizer.eos_token_id
        )
        response = tokenizer.decode(output[0], skip_special_tokens=True)

        context_log.append({
            "prompt": user_input,
            "response": response
        })

        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/copilot/log")
def get_context_log():
    return {"log": context_log}

@app.get("/health")
def health_check():
    return {"status": "Falcon 7B API is running with D.A.N. personality and memory"}
