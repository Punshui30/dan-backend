
from typing import List, Dict
import re
from collections import defaultdict

# Simulated logs; these would normally be shared from your backend session
context_log: List[Dict] = []
checkpoint_log: List[str] = []

def analyze_context(log: List[Dict]) -> Dict[str, List[str]]:
    themes = defaultdict(list)
    for entry in log:
        prompt = entry.get("prompt", "").lower()
        response = entry.get("response", "").lower()
        combined = prompt + " " + response

        if "inventory" in combined:
            themes["Inventory Management"].append(entry["prompt"])
        if "reset" in combined or "focus" in combined:
            themes["Refocusing Moments"].append(entry["prompt"])
        if "api" in combined or "gate in" in combined:
            themes["Integrations"].append(entry["prompt"])
        if "context" in combined or "memory" in combined:
            themes["Memory & Logs"].append(entry["prompt"])
        if "cannabis" in combined or "hemp" in combined:
            themes["Plant Medicine"].append(entry["prompt"])
        if "security" in combined:
            themes["Security Protocols"].append(entry["prompt"])
    return themes

def extract_checkpoints(log: List[Dict]) -> List[str]:
    key_insights = []
    for entry in log:
        if "note" in entry and "new glasses" in entry["note"].lower():
            key_insights.append("🔁 Reset was triggered: '{}'".format(entry["prompt"]))
        if "resolved" in entry.get("response", "").lower():
            key_insights.append("✅ Resolution detected in: '{}'".format(entry["prompt"]))
        if "next steps" in entry.get("response", "").lower():
            key_insights.append("📌 Action item found in: '{}'".format(entry["prompt"]))
    return key_insights
