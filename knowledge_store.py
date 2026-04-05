# knowledge_store.py — Verse-level semantic brain for the Throne of Anhu
from __future__ import annotations

import json
import math
from pathlib import Path
from functools import lru_cache
from typing import List, Dict, Any

from openai import OpenAI

from config import get_settings
from scroll_library import get_all_scrolls

settings = get_settings()

# -----------------------------
# Paths
# -----------------------------

BASE_DIR = Path(__file__).resolve().parent
VECTOR_INDEX_PATH = BASE_DIR / "vector_index.json"

# -----------------------------
# OpenAI client for embeddings
# -----------------------------

if settings.openai_base_url:
    _client = OpenAI(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
    )
else:
    _client = OpenAI(api_key=settings.openai_api_key)

# You can change this in config later if needed
EMBEDDING_MODEL = getattr(
    settings,
    "embedding_model_name",
    "text-embedding-3-small",
)


# -----------------------------
# Helpers
# -----------------------------

def _l2_norm(vec: List[float]) -> float:
    return math.sqrt(sum(x * x for x in vec))


def _normalize(vec: List[float]) -> List[float]:
    n = _l2_norm(vec)
    if n == 0.0:
        return vec
    return [x / n for x in vec]


# -----------------------------
# BUILD: create / refresh index
# -----------------------------

def build_vector_index(output_path: Path | None = None) -> None:
    """
    Build a verse-level embedding index from all scrolls and
    save it to vector_index.json.

    Run manually when you add or change scrolls:

        python knowledge_store.py

    Index structure:
    [
      {
        "book_title": "...",
        "scroll_id": "...",
        "verse_index": 1,
        "text": "full verse text...",
        "embedding": [ ... unit vector ... ]
      },
      ...
    ]
    """
    path = output_path or VECTOR_INDEX_PATH

    scrolls = get_all_scrolls()
    records: List[Dict[str, Any]] = []

    # 1) Collect all verses as a flat list of texts
    verse_payload: List[Dict[str, Any]] = []
    for s in scrolls:
        book_title = (s.get("book_title") or "").strip() or "Untitled Scroll"
        scroll_id = s.get("id") or s.get("scroll_id") or book_title
        verses = s.get("verses") or []
        if not isinstance(verses, list):
            continue

        for idx, verse in enumerate(verses, start=1):
            text = str(verse).strip()
            if not text:
                continue
            verse_payload.append(
                {
                    "book_title": book_title,
                    "scroll_id": scroll_id,
                    "verse_index": idx,
                    "text": text,
                }
            )

    if not verse_payload:
        raise RuntimeError("No verses found to index.")

    # 2) Embed in batches
    BATCH_SIZE = 64
    for i in range(0, len(verse_payload), BATCH_SIZE):
        batch = verse_payload[i : i + BATCH_SIZE]
        texts = [v["text"] for v in batch]

        resp = _client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=texts,
        )
        embeds = [e.embedding for e in resp.data]

        for meta, emb in zip(batch, embeds):
            norm_emb = _normalize(emb)
            records.append(
                {
                    "book_title": meta["book_title"],
                    "scroll_id": meta["scroll_id"],
                    "verse_index": meta["verse_index"],
                    "text": meta["text"],
                    "embedding": norm_emb,
                }
            )

    path.write_text(json.dumps(records), encoding="utf-8")
    print(f"[knowledge_store] Saved {len(records)} verse embeddings to {path}")


# -----------------------------
# LOAD: cached index
# -----------------------------

@lru_cache(maxsize=1)
def _load_vector_index() -> List[Dict[str, Any]]:
    if not VECTOR_INDEX_PATH.exists():
        # No index yet → semantic search will gracefully no-op
        return []

    with VECTOR_INDEX_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("vector_index.json must contain a list of records.")

    return data


# -----------------------------
# SEARCH: semantic verse search
# -----------------------------

def search_similar_verses(
    query: str,
    top_k: int = 16,
) -> List[Dict[str, Any]]:
    """
    Semantic search over all verses using cosine similarity.

    Returns a list of:
      {
        "book_title": ...,
        "scroll_id": ...,
        "verse_index": int,
        "text": "verse text",
        "score": float
      }
    """
    q = (query or "").strip()
    if not q:
        return []

    index = _load_vector_index()
    if not index:
        # No index yet – caller should fall back to keyword search
        return []

    # Embed query and normalize
    resp = _client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=[q],
    )
    q_emb = _normalize(resp.data[0].embedding)

    # Compute cosine via dot product (embeddings already normalized)
    scored: List[Dict[str, Any]] = []
    for rec in index:
        emb = rec.get("embedding") or []
        if not emb:
            continue
        # dot product
        score = sum(q_e * v_e for q_e, v_e in zip(q_emb, emb))
        scored.append(
            {
                "book_title": rec.get("book_title"),
                "scroll_id": rec.get("scroll_id"),
                "verse_index": rec.get("verse_index"),
                "text": rec.get("text"),
                "score": float(score),
            }
        )

    scored.sort(key=lambda r: r["score"], reverse=True)
    return scored[:top_k]


# -----------------------------
# CLI entrypoint
# -----------------------------

if __name__ == "__main__":
    # Simple CLI: rebuild the index
    build_vector_index()