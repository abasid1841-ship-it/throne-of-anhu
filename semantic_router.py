# semantic_router.py — Embedding-based intent classification for the Throne
"""
Uses semantic similarity with labeled exemplars to determine which court
should handle a question, understanding meaning rather than just keywords.
"""

from __future__ import annotations

import math
from typing import List, Tuple, Optional
from dataclasses import dataclass

from openai import OpenAI
from config import get_settings

settings = get_settings()

EMBED_MODEL = getattr(settings, "embedding_model_name", None) or "text-embedding-3-small"

if getattr(settings, "openai_base_url", None):
    _client = OpenAI(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
    )
else:
    _client = OpenAI(api_key=settings.openai_api_key)

INTENT_EXEMPLARS = {
    "holy_of_holies": [
        "What is the law about stealing?",
        "Judge my situation - I lied to my parents",
        "Am I cursed because of what I did?",
        "What punishment awaits those who betray?",
        "Is divorce a sin in the eyes of the Throne?",
        "What happens when I break a vow?",
        "Pronounce judgment on my enemy",
        "What is the verdict for adultery?",
        "I need a blessing for my family",
        "How do I remove a curse from my lineage?",
        "I am depressed and want to end my life",
        "My heart is broken, I feel like dying",
        "I am anxious about everything",
        "My marriage is falling apart",
        "I feel so alone and hopeless",
        "What happens to my soul when I die?",
        "Will I be punished in the afterlife?",
        "Is there karma for my actions?",
    ],
    "inner_court": [
        "Teach me about the 22 letters",
        "Explain the meaning of the calendar",
        "How do I understand the gates of the year?",
        "What is the Shona alphabet?",
        "Tell me about Great Zimbabwe",
        "Who was Baba Johani Masowe?",
        "Explain the four elements to me",
        "What does the spiral nation mean?",
        "How do I learn about the seals?",
        "What are the 44 gates?",
        "Teach me the cosmology of Anhu",
        "Explain the meaning of memory in the scrolls",
        "What is the significance of breath?",
        "How do bones relate to ancestors?",
        "What does seed mean spiritually?",
        "How do I understand the eclipse cycle?",
        "Explain the Great Year to me",
        "What are the ages of mankind?",
    ],
    "outer_court": [
        "Hello, how are you?",
        "What is your name?",
        "Tell me something wise",
        "Good morning",
        "I want to chat",
        "Who are you?",
        "What can you help me with?",
        "Give me a word of encouragement",
        "I'm just curious about this app",
        "Say something inspiring",
        "What is truth?",
        "How should I live my life?",
        "What is the meaning of life?",
        "Tell me about yourself",
        "I need guidance",
        "Speak wisdom to me",
    ],
}

_exemplar_embeddings: Optional[dict] = None

def _normalize(vec: List[float]) -> List[float]:
    n = math.sqrt(sum(x * x for x in vec))
    if n == 0.0:
        return vec
    return [x / n for x in vec]

def _cosine(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    return sum(x * y for x, y in zip(a, b))

def _embed_text(text: str) -> List[float]:
    text = (text or "").strip()
    if not text:
        return []
    resp = _client.embeddings.create(
        model=EMBED_MODEL,
        input=[text],
    )
    return _normalize(resp.data[0].embedding)

def _embed_batch(texts: List[str]) -> List[List[float]]:
    if not texts:
        return []
    resp = _client.embeddings.create(
        model=EMBED_MODEL,
        input=texts,
    )
    return [_normalize(e.embedding) for e in resp.data]

def _load_exemplar_embeddings() -> dict:
    global _exemplar_embeddings
    if _exemplar_embeddings is not None:
        return _exemplar_embeddings
    
    _exemplar_embeddings = {}
    
    for intent, examples in INTENT_EXEMPLARS.items():
        embeddings = _embed_batch(examples)
        _exemplar_embeddings[intent] = embeddings
        print(f"[semantic_router] Loaded {len(embeddings)} exemplars for {intent}")
    
    return _exemplar_embeddings

def _compute_intent_scores(query_embedding: List[float]) -> List[Tuple[str, float]]:
    exemplars = _load_exemplar_embeddings()
    
    scores = []
    for intent, embeddings in exemplars.items():
        if not embeddings:
            scores.append((intent, 0.0))
            continue
        
        similarities = [_cosine(query_embedding, emb) for emb in embeddings]
        top_k = sorted(similarities, reverse=True)[:3]
        avg_score = sum(top_k) / len(top_k) if top_k else 0.0
        scores.append((intent, avg_score))
    
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores

def semantic_route(query: str, query_embedding: Optional[List[float]] = None) -> Tuple[str, float, List[float]]:
    """
    Route a query to the appropriate court using semantic understanding.
    
    Returns:
        (mode, confidence, query_embedding)
        - mode: "outer_court", "inner_court", or "holy_of_holies"
        - confidence: similarity score (0.0 to 1.0)
        - query_embedding: the embedding of the query (for reuse)
    """
    if query_embedding is None:
        query_embedding = _embed_text(query)
    
    if not query_embedding:
        return "outer_court", 0.0, []
    
    scores = _compute_intent_scores(query_embedding)
    
    if not scores:
        return "outer_court", 0.0, query_embedding
    
    best_intent, best_score = scores[0]
    
    MIN_CONFIDENCE = 0.45
    if best_score < MIN_CONFIDENCE:
        return "outer_court", best_score, query_embedding
    
    return best_intent, best_score, query_embedding

def route_with_fallback(message: str) -> str:
    """
    Try semantic routing first, fall back to keyword routing if needed.
    """
    from router import route_mode as keyword_route
    
    try:
        mode, confidence, _ = semantic_route(message)
        
        if confidence >= 0.50:
            return mode
        
        keyword_mode = keyword_route(message)
        if keyword_mode != "outer_court":
            return keyword_mode
        
        return mode
        
    except Exception as e:
        print(f"[semantic_router] Error: {e}, falling back to keyword routing")
        return keyword_route(message)

if __name__ == "__main__":
    print("=== SEMANTIC ROUTER TEST ===")
    
    test_queries = [
        "What happens when I die?",
        "Teach me about the alphabet",
        "I feel so alone and depressed",
        "Hello, who are you?",
        "Judge my actions",
        "How do the elements work?",
        "What is the meaning of life?",
        "Am I cursed?",
    ]
    
    for q in test_queries:
        mode, score, _ = semantic_route(q)
        print(f"[{score:.3f}] {mode}: {q}")
