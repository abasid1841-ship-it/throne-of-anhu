# third_mind.py
"""
THIRD MIND · The Retriever for the Throne of Anhu.

Reads verse embeddings from third_mind.db (table: scroll_verses)
Reads ANI Vault embeddings from third_mind.db (table: ani_vault)

Embeds a query
Finds similar verses / vault notes with cosine similarity
Returns structured results
"""

from __future__ import annotations

import json
import math
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Optional

from openai import OpenAI
from config import get_settings


# ---------------- PATHS & SETTINGS ----------------

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "third_mind.db"

settings = get_settings()

# Use a dedicated embedding model name, consistent with knowledge_store.py
# Falls back to a sane default if not provided.
EMBED_MODEL = getattr(settings, "embedding_model_name", None) or "text-embedding-3-small"

# OpenAI client
if getattr(settings, "openai_base_url", None):
    client = OpenAI(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
    )
else:
    client = OpenAI(api_key=settings.openai_api_key)


# ---------------- DATA MODELS ----------------

@dataclass
class RetrievedVerse:
    source: str           # "scroll"
    scroll_id: str
    scroll_title: str
    verse_index: int
    verse_text: str
    score: float


@dataclass
class RetrievedVaultNote:
    source: str           # "vault"
    id: int
    question: str
    answer: str
    persona: str
    tags: List[str]
    score: float


# ---------------- DB HELPERS ----------------

def _get_conn() -> sqlite3.Connection:
    return sqlite3.connect(str(DB_PATH))


def _load_all_verses() -> List[dict]:
    """
    Load all verses + embeddings from DB into memory.

    Each item:
      {
        "scroll_id": ...,
        "scroll_title": ...,
        "verse_index": int,
        "verse_text": str,
        "embedding": List[float]
      }
    """
    if not DB_PATH.exists():
        print(f"[THIRD MIND] WARNING: DB not found at {DB_PATH}")
        return []

    conn = _get_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT scroll_id, scroll_title, verse_index, verse_text, embedding
            FROM scroll_verses;
            """
        )
    except sqlite3.Error as e:
        print(f"[THIRD MIND] WARNING: could not read scroll_verses: {e}")
        conn.close()
        return []

    rows = cur.fetchall()
    conn.close()

    verses: List[dict] = []
    for scroll_id, title, idx, text, emb_json in rows:
        try:
            emb = json.loads(emb_json) if emb_json else []
        except Exception:
            emb = []
        verses.append(
            {
                "scroll_id": str(scroll_id or ""),
                "scroll_title": str(title or ""),
                "verse_index": int(idx or 0),
                "verse_text": str(text or ""),
                "embedding": emb,
            }
        )

    print(f"[THIRD MIND] Loaded {len(verses)} embedded verses from DB.")
    return verses


def _load_all_vault_notes() -> List[dict]:
    """
    Load all ANI Vault notes + embeddings from DB into memory.

    Each item:
      {
        "id": int,
        "question": str,
        "answer": str,
        "persona": str,
        "tags": List[str],
        "embedding": List[float],
      }
    """
    if not DB_PATH.exists():
        print(f"[THIRD MIND] WARNING: DB not found at {DB_PATH}")
        return []

    conn = _get_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT id, question, answer, persona, tags_json, embedding
            FROM ani_vault;
            """
        )
    except sqlite3.Error as e:
        print(f"[THIRD MIND] WARNING: could not read ani_vault: {e}")
        conn.close()
        return []

    rows = cur.fetchall()
    conn.close()

    notes: List[dict] = []
    for id_, q, a, persona, tags_json, emb_json in rows:
        try:
            tags = json.loads(tags_json) if tags_json else []
        except Exception:
            tags = []
        try:
            emb = json.loads(emb_json) if emb_json else []
        except Exception:
            emb = []
        notes.append(
            {
                "id": int(id_ or 0),
                "question": str(q or ""),
                "answer": str(a or ""),
                "persona": str(persona or "").upper(),
                "tags": tags if isinstance(tags, list) else [],
                "embedding": emb,
            }
        )

    print(f"[THIRD MIND] Loaded {len(notes)} ANI Vault entries from DB.")
    return notes


# ---- In-memory caches ----
_VERSE_CACHE: Optional[List[dict]] = None
_VAULT_CACHE: Optional[List[dict]] = None


def _get_verse_cache() -> List[dict]:
    global _VERSE_CACHE
    if _VERSE_CACHE is None:
        _VERSE_CACHE = _load_all_verses()
    return _VERSE_CACHE or []


def _get_vault_cache() -> List[dict]:
    global _VAULT_CACHE
    if _VAULT_CACHE is None:
        _VAULT_CACHE = _load_all_vault_notes()
    return _VAULT_CACHE or []


# ---------------- EMBEDDING + SIMILARITY ----------------

def _embed_text(text: str) -> List[float]:
    text = (text or "").strip()
    if not text:
        return []
    resp = client.embeddings.create(
        model=EMBED_MODEL,
        input=[text],
    )
    return resp.data[0].embedding


def _cosine(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


# ---------------- PUBLIC APIs ----------------

def search_scroll_verses(
    query: str,
    top_k: int = 5,
    min_score: float = 0.25,
) -> List[RetrievedVerse]:
    query = (query or "").strip()
    if not query:
        return []

    verses = _get_verse_cache()
    if not verses:
        return []

    q_emb = _embed_text(query)
    results: List[RetrievedVerse] = []

    for v in verses:
        score = _cosine(q_emb, v.get("embedding") or [])
        if score >= min_score:
            results.append(
                RetrievedVerse(
                    source="scroll",
                    scroll_id=v.get("scroll_id", ""),
                    scroll_title=v.get("scroll_title", ""),
                    verse_index=int(v.get("verse_index") or 0),
                    verse_text=v.get("verse_text", ""),
                    score=float(score),
                )
            )

    results.sort(key=lambda r: r.score, reverse=True)
    return results[:top_k]


def search_vault_notes(
    query: str,
    top_k: int = 5,
    min_score: float = 0.25,
) -> List[RetrievedVaultNote]:
    query = (query or "").strip()
    if not query:
        return []

    notes = _get_vault_cache()
    if not notes:
        return []

    q_emb = _embed_text(query)
    results: List[RetrievedVaultNote] = []

    for n in notes:
        score = _cosine(q_emb, n.get("embedding") or [])
        if score >= min_score:
            results.append(
                RetrievedVaultNote(
                    source="vault",
                    id=int(n.get("id") or 0),
                    question=n.get("question", ""),
                    answer=n.get("answer", ""),
                    persona=(n.get("persona") or "").upper(),
                    tags=n.get("tags") or [],
                    score=float(score),
                )
            )

    results.sort(key=lambda r: r.score, reverse=True)
    return results[:top_k]


def search_third_mind(
    query: str,
    top_k_scroll: int = 5,
    top_k_vault: int = 5,
    min_score: float = 0.25,
) -> Tuple[List[RetrievedVerse], List[RetrievedVaultNote]]:
    scroll_hits = search_scroll_verses(query, top_k=top_k_scroll, min_score=min_score)
    vault_hits = search_vault_notes(query, top_k=top_k_vault, min_score=min_score)
    return scroll_hits, vault_hits


def build_third_mind_context(
    query: str,
    top_k_scroll: int = 5,
    top_k_vault: int = 5,
) -> str:
    scroll_hits, vault_hits = search_third_mind(
        query,
        top_k_scroll=top_k_scroll,
        top_k_vault=top_k_vault,
    )

    if not scroll_hits and not vault_hits:
        return ""

    lines: List[str] = []

    for h in scroll_hits:
        vnum = h.verse_index + 1
        lines.append(f"[SCROLL · {h.scroll_title} – v{vnum}]")
        lines.append(h.verse_text)
        lines.append("")

    for v in vault_hits:
        tag_str = ", ".join(v.tags) if v.tags else ""
        tag_part = f" · {tag_str}" if tag_str else ""
        lines.append(f"[VAULT · {v.persona}{tag_part}]")
        lines.append(f"Q: {v.question}")
        lines.append(f"A: {v.answer}")
        lines.append("")

    return "\n".join(lines).strip()


if __name__ == "__main__":
    print("=== THIRD MIND · RETRIEVER TEST ===")
    q = input("Ask the Throne a question: ").strip()
    sh, vh = search_third_mind(q, top_k_scroll=5, top_k_vault=5)

    print("\n--- SCROLL HITS ---")
    for h in sh:
        print(f"[{h.scroll_title} · v{h.verse_index + 1} · score={h.score:.3f}]")
        print(h.verse_text)

    print("\n--- VAULT HITS ---")
    for v in vh:
        print(f"[VAULT #{v.id} · {v.persona} · score={v.score:.3f} · tags={v.tags}]")
        print("Q:", v.question)
        print("A:", v.answer)