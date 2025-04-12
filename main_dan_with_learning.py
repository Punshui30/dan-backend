from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

app = FastAPI()

# Enable CORS for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can replace with exact Netlify URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lazy model loader
model = None
tokenizer = None
model_name = "tiiuae/falcon-7b-instruct"

def load_model():
    global model, tokenizer
    if model is None or tokenizer is None:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float32,
            device_map={"": "cpu"}
        )

# D.A.N. personality
DAN_PERSONALITY = """
You are D.A.N. – digital OS of Daniel Simmonds.
Tactical. Honest. Practical. You cut through noise and deliver truth with speed.
"""

# Prompt structure
class PromptRequest(BaseModel):
    prompt: str

@app.post("/copilot/chat")
async def copilot_chat(request: PromptRequest):
    try:
        load_model()
        user_input = request.prompt.strip()

        # New Glasses trigger
        if "new glasses" in user_input.lower():
            return {"response": "🕶️ D.A.N. is refocusing. Tactical lens engaged. What’s the mission?"}

        full_prompt = f"{DAN_PERSONALITY.strip()}\n\n{user_input}"
        inputs = tokenizer(full_prompt, return_tensors="pt", truncation=True, max_length=512)
        output = model.generate(
            **inputs,
            max_length=1024,
            pad_token_id=tokenizer.eos_token_id
        )
        response = tokenizer.decode(output[0], skip_special_tokens=True)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "Falcon 7B backend running with D.A.N. personality"}
