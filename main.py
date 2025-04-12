from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

app = FastAPI()

# Load Falcon model (CPU-safe setup)
model_name = "tiiuae/falcon-7b-instruct"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float32,
    device_map={"": "cpu"}
)

class PromptRequest(BaseModel):
    prompt: str

@app.post("/copilot/chat")
async def copilot_chat(request: PromptRequest):
    try:
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

        full_prompt = DAN_PERSONALITY.strip() + "\n\n" + request.prompt
        inputs = tokenizer(full_prompt, return_tensors="pt", truncation=True, max_length=512)
        output = model.generate(
            **inputs,
            max_length=1024,
            num_return_sequences=1,
            pad_token_id=tokenizer.eos_token_id
        )
        response = tokenizer.decode(output[0], skip_special_tokens=True)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "Falcon 7B API is running on CPU"}
