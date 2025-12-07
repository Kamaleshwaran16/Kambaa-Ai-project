"""AI utilities: summarizer + priority predictor.

Design:
- If `sentence_transformers` is installed, use a model to embed + simple rules.
- Otherwise fallback to simple heuristic (keywords).
This file is safe to run offline; it will only use the heavy model if installed and available.
"""
from typing import Optional
import re

# Try to import sentence-transformers quietly
try:
    from sentence_transformers import SentenceTransformer
    st_model = SentenceTransformer('all-MiniLM-L6-v2')
except Exception as e:
    st_model = None

KEYWORD_PRIORITY = {
    "high": ["urgent", "immediately", "asap", "critical", "important", "deadline", "today"],
    "medium": ["soon", "this week", "priority", "next"],
    "low": ["whenever", "someday", "optional", "low"]
}

def summarize_text(text: str, max_words:int=15) -> str:
    # Simple heuristic summarizer: take first sentence, truncate to max_words
    if not text:
        return ""
    s = re.split(r'[\n\.\!\?]+', text.strip())[0]
    words = s.split()
    if len(words) <= max_words:
        return s.strip()
    return " ".join(words[:max_words]).strip() + "..."

def predict_priority(text: str) -> str:
    t = text.lower()
    # rule-based first
    for level, kwlist in KEYWORD_PRIORITY.items():
        for kw in kwlist:
            if kw in t:
                return level.capitalize()
    # fallback to model (if available) -- very simple distance to prototype embeddings
    if st_model:
        try:
            labels = ["High","Medium","Low"]
            prototypes = ["urgent deadline critical now asap", "important soon scheduled", "low optional whenever"] 
            emb_text = st_model.encode([text])
            emb_proto = st_model.encode(prototypes)
            import numpy as np
            sims = (emb_text @ emb_proto.T)[0]  # cosine-like if model normalized
            idx = int(sims.argmax())
            return labels[idx]
        except Exception:
            pass
    # default
    return "Medium"
