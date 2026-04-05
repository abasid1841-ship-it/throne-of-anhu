"""
scroll_embedder.py
------------------
Builds the THIRD MIND memory for the Throne of Anhu.

- Reads all scrolls from:  allscrolls.json/scrolls.json
- Splits them into verses
- Creates embeddings for each verse
- Stores them in: third_mind.db, table: scroll_verses
"""

from pathlib import Path
import json
import sqlite3
from typing import List, Tuple

from openai import OpenAI
from config import get_settings

# ---------------- PATHS & SETTINGS ----------------

BASE_DIR = Path(__file__).resolve().parent
SCROLLS_FOLDER = BASE_DIR / "allscrolls.json"
SCROLLS_FILE = SCROLLS_FOLDER / "scrolls.json"
DB_PATH = BASE_DIR / "third_mind.db"

settings = get_settings()

# Choose an embedding model - must be an actual embedding model, not a chat model
EMBED_MODEL = getattr(settings, "embedding_model", None) or "text-embedding-3-small"

# For embeddings, always use standard OpenAI API (not proxies which may not support embeddings)
client = OpenAI(api_key=settings.openai_api_key)


# ---------------- DB SETUP ----------------

def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    return conn


def init_db() -> None:
    """
    Create the scroll_verses table if it does not exist.
    """
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS scroll_verses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scroll_id TEXT NOT NULL,
            scroll_title TEXT NOT NULL,
            verse_index INTEGER NOT NULL,
            verse_text TEXT NOT NULL,
            embedding TEXT NOT NULL
        );
        """
    )
    # Speed up similarity search later
    cur.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS idx_scroll_unique
        ON scroll_verses (scroll_id, verse_index);
        """
    )
    conn.commit()
    conn.close()


# ---------------- SCROLL LOADING ----------------

ADDITIONAL_SCROLL_SOURCES: List[Path] = [
    BASE_DIR / "allscrolls.json" / "abasid_1841_scrolls.json",
    BASE_DIR / "static" / "allscrolls.json" / "abasid_1841_scrolls.json",
    BASE_DIR / "static" / "allscrolls.json" / "scrolls.json",
    BASE_DIR / "static" / "allscrolls.json" / "abasid_1841_laws.json",
    BASE_DIR / "sources" / "masowe_history.json",
    BASE_DIR / "static" / "allscrolls.json" / "islam_abasid_caliphate.json",
    BASE_DIR / "static" / "allscrolls.json" / "shona_dynasty_masowe_connection.json",
    BASE_DIR / "sources" / "gospel_of_cyrus.json",
    BASE_DIR / "sources" / "god_is_time.json",
    BASE_DIR / "sources" / "gospel_of_christos.json",
    BASE_DIR / "sources" / "book_of_new_calendar.json",
    BASE_DIR / "sources" / "book_of_asar.json",
    BASE_DIR / "sources" / "gospel_of_yesu.json",
    BASE_DIR / "sources" / "true_exodus.json",
    BASE_DIR / "sources" / "god_is_number.json",
    BASE_DIR / "sources" / "book_of_risen_seeds.json",
    BASE_DIR / "sources" / "power_of_trinity.json",
    BASE_DIR / "sources" / "planet_2_jupiter_abasid" / "lineage_of_abasid_1841.json",
]

def load_scrolls() -> List[dict]:
    """
    Load the scrolls from all sources including additional scroll files.

    Expected format: a JSON array of objects:
      {
        "scroll_id": "...",
        "series": "...",
        "book_title": "...",
        "language": "EN",
        "verses": ["1. ...", "2. ...", ...]
      }
    """
    all_scrolls: List[dict] = []
    
    if SCROLLS_FOLDER.exists() and SCROLLS_FOLDER.is_dir() and SCROLLS_FILE.exists():
        with SCROLLS_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            all_scrolls.extend(data)
            print(f"[EMBEDDER] Loaded {len(data)} scroll objects from {SCROLLS_FILE}.")
    
    loaded_files = set()
    for extra_p in ADDITIONAL_SCROLL_SOURCES:
        try:
            if extra_p and extra_p.is_file():
                if extra_p.name in loaded_files:
                    continue
                data = json.loads(extra_p.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    if "scrolls" in data:
                        data = data["scrolls"]
                    elif "entries" in data:
                        data = data["entries"]
                    elif "verses" in data:
                        all_scrolls.append(data)
                        loaded_files.add(extra_p.name)
                        print(f"[EMBEDDER] Loaded single scroll from {extra_p.name}")
                        continue
                if isinstance(data, list):
                    all_scrolls.extend(data)
                    loaded_files.add(extra_p.name)
                    print(f"[EMBEDDER] Loaded {len(data)} additional scrolls from {extra_p.name}")
        except Exception as e:
            print(f"[EMBEDDER] WARNING: Could not load additional scrolls from {extra_p}: {e}")
    
    print(f"[EMBEDDER] Total scrolls available for embedding: {len(all_scrolls)}")
    return all_scrolls


# ---------------- EMBEDDING ----------------

def embed_batch(texts: List[str]) -> List[List[float]]:
    """
    Call the embedding model on a batch of texts.
    """
    if not texts:
        return []

    resp = client.embeddings.create(
        model=EMBED_MODEL,
        input=texts,
    )
    # OpenAI-compatible: resp.data is a list with .embedding
    vectors = [item.embedding for item in resp.data]
    return vectors


def chunk_list(items: List[str], size: int) -> List[List[str]]:
    return [items[i : i + size] for i in range(0, len(items), size)]


# ---------------- MAIN BUILD LOGIC ----------------

def build_embeddings(clear_existing: bool = True, batch_size: int = 64) -> None:
    """
    Main builder:
    - Optionally clears old data
    - Embeds verses in batches
    - Stores everything in third_mind.db
    """
    init_db()
    conn = get_conn()
    cur = conn.cursor()

    if clear_existing:
        print("[EMBEDDER] Clearing existing entries in scroll_verses...")
        cur.execute("DELETE FROM scroll_verses;")
        conn.commit()

    scrolls = load_scrolls()

    total_verses = 0

    for scroll in scrolls:
        scroll_id = str(scroll.get("scroll_id") or scroll.get("id") or "UNKNOWN")
        title = str(scroll.get("book_title") or scroll.get("title") or "Untitled Scroll")
        verses = scroll.get("verses") or []

        if not verses:
            continue

        print(f"[EMBEDDER] Processing scroll: {scroll_id} · {title} "
              f"({len(verses)} verses)")

        # We embed in batches for efficiency
        for batch_start in range(0, len(verses), batch_size):
            batch_verses = verses[batch_start : batch_start + batch_size]

            # Prepare clean text - handle both string and dict verse formats
            clean_texts = []
            for v in batch_verses:
                if isinstance(v, dict):
                    text = str(v.get("text") or v.get("verse_text") or "")
                else:
                    text = str(v)
                text = text.strip()
                # Replace empty strings with a placeholder to avoid API errors
                if not text:
                    text = "[empty verse]"
                clean_texts.append(text)
            
            # Skip if all texts are empty/placeholder
            if all(t == "[empty verse]" for t in clean_texts):
                continue
                
            try:
                embeddings = embed_batch(clean_texts)
            except Exception as e:
                print(f"[EMBEDDER] WARNING: Failed to embed batch for {scroll_id}: {e}")
                continue

            for offset, (verse_text, emb) in enumerate(zip(clean_texts, embeddings)):
                verse_index = batch_start + offset

                cur.execute(
                    """
                    INSERT OR REPLACE INTO scroll_verses
                    (scroll_id, scroll_title, verse_index, verse_text, embedding)
                    VALUES (?, ?, ?, ?, ?);
                    """,
                    (
                        scroll_id,
                        title,
                        verse_index,
                        verse_text,
                        json.dumps(emb),
                    ),
                )
                total_verses += 1

            conn.commit()

    conn.close()
    print(f"[EMBEDDER] DONE. Stored embeddings for {total_verses} verses.")


# ---------------- CLI ENTRY ----------------

if __name__ == "__main__":
    print("=== THRONE OF ANHU · SCROLL EMBEDDER ===")
    print(f"DB:      {DB_PATH}")
    print(f"Scrolls: {SCROLLS_FILE}")
    print(f"Model:   {EMBED_MODEL}")
    build_embeddings(clear_existing=True)