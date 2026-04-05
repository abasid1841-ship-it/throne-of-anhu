# semantic_retriever.py — Unified semantic search for the Throne
"""
Single embedding per query, used for both:
1. Intent classification (routing to court)
2. Verse retrieval (finding relevant scrolls)

This minimizes API calls while maximizing semantic understanding.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict, Any
from pathlib import Path
import json

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

BASE_DIR = Path(__file__).resolve().parent
VECTOR_INDEX_PATH = BASE_DIR / "vector_index.json"

@dataclass
class SemanticVerse:
    scroll_id: str
    book_title: str
    verse_index: int
    text: str
    score: float

@dataclass
class SemanticResult:
    query: str
    query_embedding: List[float]
    mode: str
    mode_confidence: float
    verses: List[SemanticVerse]

_vector_index: Optional[List[Dict[str, Any]]] = None

def _normalize(vec: List[float]) -> List[float]:
    n = math.sqrt(sum(x * x for x in vec))
    if n == 0.0:
        return vec
    return [x / n for x in vec]

def _cosine(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    return sum(x * y for x, y in zip(a, b))

def _embed_query(query: str) -> List[float]:
    query = (query or "").strip()
    if not query:
        return []
    resp = _client.embeddings.create(
        model=EMBED_MODEL,
        input=[query],
    )
    return _normalize(resp.data[0].embedding)

def _load_vector_index() -> List[Dict[str, Any]]:
    global _vector_index
    if _vector_index is not None:
        return _vector_index
    
    import sqlite3
    db_path = BASE_DIR / "third_mind.db"
    
    if db_path.exists():
        try:
            conn = sqlite3.connect(str(db_path))
            cur = conn.cursor()
            cur.execute('SELECT scroll_id, scroll_title, verse_index, verse_text, embedding FROM scroll_verses')
            rows = cur.fetchall()
            conn.close()
            
            _vector_index = []
            for scroll_id, scroll_title, verse_index, verse_text, embedding in rows:
                emb = json.loads(embedding) if embedding else []
                _vector_index.append({
                    'scroll_id': scroll_id,
                    'book_title': scroll_title,
                    'verse_index': verse_index,
                    'text': verse_text,
                    'embedding': emb
                })
            print(f"[semantic_retriever] Loaded {len(_vector_index)} verse embeddings from third_mind.db")
            return _vector_index
        except Exception as e:
            print(f"[semantic_retriever] Error loading from database: {e}")
    
    if VECTOR_INDEX_PATH.exists():
        with VECTOR_INDEX_PATH.open("r", encoding="utf-8") as f:
            _vector_index = json.load(f)
        print(f"[semantic_retriever] Loaded {len(_vector_index)} verse embeddings from vector_index.json")
        return _vector_index
    
    print(f"[semantic_retriever] No vector index found")
    _vector_index = []
    return _vector_index

def search_verses_semantic(
    query_embedding: List[float],
    top_k: int = 8,
    min_score: float = 0.30,
) -> List[SemanticVerse]:
    """
    Search for verses using a pre-computed query embedding.
    """
    if not query_embedding:
        return []
    
    index = _load_vector_index()
    if not index:
        return []
    
    scored: List[Tuple[float, Dict[str, Any]]] = []
    
    for rec in index:
        emb = rec.get("embedding") or []
        if not emb:
            continue
        score = _cosine(query_embedding, emb)
        if score >= min_score:
            scored.append((score, rec))
    
    scored.sort(key=lambda x: x[0], reverse=True)
    
    results = []
    for score, rec in scored[:top_k]:
        results.append(SemanticVerse(
            scroll_id=rec.get("scroll_id", ""),
            book_title=rec.get("book_title", ""),
            verse_index=rec.get("verse_index", 0),
            text=rec.get("text", ""),
            score=score,
        ))
    
    return results

def unified_semantic_search(
    query: str,
    top_k_verses: int = 8,
    min_verse_score: float = 0.30,
) -> SemanticResult:
    """
    Single-embedding semantic search that provides:
    1. Intent classification (mode routing)
    2. Relevant verse retrieval
    
    This is the main entry point for semantic understanding.
    """
    from semantic_router import semantic_route
    
    query_embedding = _embed_query(query)
    
    if not query_embedding:
        return SemanticResult(
            query=query,
            query_embedding=[],
            mode="outer_court",
            mode_confidence=0.0,
            verses=[],
        )
    
    mode, confidence, _ = semantic_route(query, query_embedding)
    
    verses = search_verses_semantic(
        query_embedding,
        top_k=top_k_verses,
        min_score=min_verse_score,
    )
    
    return SemanticResult(
        query=query,
        query_embedding=query_embedding,
        mode=mode,
        mode_confidence=confidence,
        verses=verses,
    )

def get_semantic_verses_for_mode(
    result: SemanticResult,
    mode_filter: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Format verses for use in court answer flows.
    """
    formatted = []
    for v in result.verses:
        formatted.append({
            "scroll_id": v.scroll_id,
            "book_title": v.book_title,
            "verse_index": v.verse_index,
            "verse_number": v.verse_index,
            "text": v.text,
            "score": v.score,
        })
    return formatted

def hybrid_verse_search(
    query: str,
    top_k: int = 8,
    semantic_weight: float = 0.7,
) -> List[Dict[str, Any]]:
    """
    Hybrid search combining semantic and keyword approaches.
    Falls back to keyword if semantic fails.
    """
    from scroll_engine import search_verses
    
    semantic_results = []
    keyword_results = []
    
    try:
        query_embedding = _embed_query(query)
        if query_embedding:
            semantic_verses = search_verses_semantic(query_embedding, top_k=top_k * 2)
            for v in semantic_verses:
                semantic_results.append({
                    "scroll_id": v.scroll_id,
                    "book_title": v.book_title,
                    "verse_index": v.verse_index,
                    "verse_number": v.verse_index,
                    "text": v.text,
                    "score": v.score,
                    "source": "semantic",
                })
    except Exception as e:
        print(f"[semantic_retriever] Semantic search failed: {e}")
    
    try:
        keyword_verses = search_verses(query, limit=top_k * 2)
        max_kw_score = max((v.get("score", 1) for v in keyword_verses), default=1) or 1
        for v in keyword_verses:
            keyword_results.append({
                "scroll_id": v.get("scroll_id", ""),
                "book_title": v.get("book_title", ""),
                "verse_index": v.get("verse_index", 0),
                "verse_number": v.get("verse_number", 0),
                "text": v.get("text", ""),
                "score": v.get("score", 0) / max_kw_score,
                "source": "keyword",
            })
    except Exception as e:
        print(f"[semantic_retriever] Keyword search failed: {e}")
    
    if not semantic_results:
        return keyword_results[:top_k]
    
    if not keyword_results:
        return [dict(v, source="semantic") for v in semantic_results[:top_k]]
    
    combined = {}
    
    for v in semantic_results:
        key = (v["scroll_id"], v["verse_index"])
        combined[key] = {
            **v,
            "final_score": v["score"] * semantic_weight,
        }
    
    keyword_weight = 1.0 - semantic_weight
    for v in keyword_results:
        key = (v["scroll_id"], v["verse_index"])
        if key in combined:
            combined[key]["final_score"] += v["score"] * keyword_weight
            combined[key]["source"] = "hybrid"
        else:
            combined[key] = {
                **v,
                "final_score": v["score"] * keyword_weight,
            }
    
    results = sorted(combined.values(), key=lambda x: x["final_score"], reverse=True)
    return results[:top_k]

if __name__ == "__main__":
    print("=== SEMANTIC RETRIEVER TEST ===")
    
    test_queries = [
        "What happens when I die?",
        "How do I pray?",
        "Tell me about the alphabet",
        "I am feeling hopeless",
    ]
    
    for q in test_queries:
        print(f"\n--- Query: {q} ---")
        result = unified_semantic_search(q, top_k_verses=3)
        print(f"Mode: {result.mode} (confidence: {result.mode_confidence:.3f})")
        print(f"Found {len(result.verses)} verses:")
        for v in result.verses:
            print(f"  [{v.score:.3f}] {v.book_title}: {v.text[:80]}...")
