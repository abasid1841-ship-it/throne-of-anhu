# source_library.py
# HOUSE OF WISDOM · Local sources for the Throne of Anhu
#
# Loads JSON files from ./sources and provides a simple keyword
# search over them with a unified result format.
#
# Also loads ABASID scrolls via scroll_library.get_all_scrolls()
# so the Scrolls can appear as witnesses in the SOURCES panel.

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# -----------------------------
# PATHS
# -----------------------------

BASE_DIR = Path(__file__).resolve().parent
SOURCES_DIR = BASE_DIR / "sources"


# -----------------------------
# SOURCE FILE MAP
# -----------------------------
# (Filename -> tradition label shown in UI)

SOURCE_FILES: Dict[str, str] = {
    "quran.json": "QURAN",
    "torah.json": "TORAH",
    "bible_nt.json": "BIBLE",
    "papyrus_ani.json": "PAPYRUS OF ANI",
    "papyrus_of_ani.json": "PAPYRUS OF ANI",
    "masowe_history.json": "MASOWE",
    "baba_johani_life.json": "BABA JOHANI",
    "nhoroondo_chronicle.json": "NHOROONDO CHRONICLE",
    "astronomy_cycles.json": "ASTRONOMY / ECLIPSES",
    "i_am_truth.json": "I AM TRUTH (IDI)",
    "shona_alphabet.json": "ABASID ALPHABET",
}


# -----------------------------
# MODEL
# -----------------------------

@dataclass
class SourceEntry:
    tradition: str       # e.g. "BIBLE", "QURAN", "SCROLL"
    ref: str             # e.g. "John 11:25" or "Book of Memory – v3"
    text: str            # short passage/snippet
    tags: List[str]      # lower-case tags


# In-memory cache
_ALL_SOURCES: List[SourceEntry] = []
_LOADED = False


# -----------------------------
# SAFE FIELD EXTRACTORS
# -----------------------------

def _safe_get_text(rec: Dict[str, Any]) -> str:
    """
    Try several common keys to pull a text/snippet from a JSON record.
    """
    candidates = [
        rec.get("text"),
        rec.get("snippet"),
        rec.get("verse"),
        rec.get("line"),
        rec.get("body"),
        rec.get("content"),
    ]
    for c in candidates:
        if not c:
            continue
        if isinstance(c, list):
            joined = " ".join(str(x) for x in c if str(x).strip())
            if joined.strip():
                return joined
        else:
            s = str(c).strip()
            if s:
                return s
    return ""


def _safe_get_ref(rec: Dict[str, Any]) -> str:
    """
    Try to pull a human-readable reference string.
    """
    candidates = [
        rec.get("ref"),
        rec.get("reference"),
        rec.get("id"),
        rec.get("location"),
        rec.get("loc"),
        rec.get("title"),
        rec.get("name"),
    ]
    for c in candidates:
        if c:
            s = str(c).strip()
            if s:
                return s
    return ""


def _safe_get_tags(rec: Dict[str, Any]) -> List[str]:
    """
    Pull tag/keyword list as lower-case strings.
    """
    tags_raw = rec.get("tags") or rec.get("keywords") or rec.get("topics") or []
    if isinstance(tags_raw, str):
        tags_raw = [tags_raw]
    out: List[str] = []
    for t in tags_raw or []:
        s = str(t).strip().lower()
        if s:
            out.append(s)
    return out


# -----------------------------
# LOAD EXTERNAL JSON SOURCES
# -----------------------------

SCROLL_ID_TO_TRADITION: Dict[str, Tuple[str, str]] = {
    "baba_johane_life_events": ("BABA JOHANI SCROLL", "Life of Baba Johani"),
    "nhoroondo_dzababa_johanne": ("NHOROONDO CHRONICLE", "Nhoroondo dzaBaba Johanne"),
    "alphabet_of_baba_johani": ("ABASID ALPHABET", "Alphabet of Baba Johani"),
}


def _resolve_scroll_citation(rec: Dict[str, Any], scrolls_cache: Dict[str, List[str]]) -> List[SourceEntry]:
    """
    Resolve a citation-style entry that points to scroll verses.
    Returns SourceEntry objects with actual verse text.
    Preserves original scroll identity in tradition/ref.
    """
    scroll_id = rec.get("scroll_id")
    verse_range = rec.get("verse_range")
    ref_base = rec.get("ref", "")
    tags = _safe_get_tags(rec)
    
    if not scroll_id or not verse_range:
        return []
    
    if scroll_id not in scrolls_cache:
        return []
    
    tradition, ref_prefix = SCROLL_ID_TO_TRADITION.get(
        scroll_id, 
        ("ABASID SCROLL", scroll_id.replace("_", " ").title())
    )
    
    verses = scrolls_cache[scroll_id]
    start, end = verse_range[0], verse_range[1]
    
    entries = []
    for v_num in range(start, min(end + 1, len(verses) + 1)):
        if v_num <= 0 or v_num > len(verses):
            continue
        verse_text = verses[v_num - 1]
        if not verse_text.strip():
            continue
        entries.append(SourceEntry(
            tradition=tradition,
            ref=f"{ref_prefix} v{v_num}",
            text=verse_text,
            tags=tags
        ))
    
    return entries


def _get_scrolls_verse_cache() -> Dict[str, List[str]]:
    """
    Build a cache of scroll_id -> verses for citation resolution.
    """
    try:
        from scroll_library import get_all_scrolls
        scrolls = get_all_scrolls() or []
    except Exception:
        return {}
    
    cache = {}
    for s in scrolls:
        scroll_id = s.get("scroll_id", "")
        if not scroll_id:
            title = s.get("book_title", "")
            scroll_id = re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")
        
        verses = s.get("verses") or s.get("lines") or []
        if isinstance(verses, str):
            verses = [ln.strip() for ln in verses.splitlines() if ln.strip()]
        elif isinstance(verses, list):
            verses = [str(v).strip() for v in verses if str(v).strip()]
        else:
            verses = []
        
        if verses:
            cache[scroll_id] = verses
    
    return cache


def _load_source_file(path: Path, tradition: str) -> List[SourceEntry]:
    """
    Load a single JSON file and normalise its entries.
    Accepts either:
      - list[dict]
      - {"entries": [...]}
      - {"items": [...]}
      - {"records": [...]}
    
    Special handling for citation-style entries that have scroll_id + verse_range.
    """
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[HOUSE OF WISDOM] Could not read {path}: {e}")
        return []

    # Allow either a list of records or { "entries": [...] }
    records = None
    if isinstance(data, list):
        records = data
    elif isinstance(data, dict):
        for key in ("entries", "items", "records", "verses", "lines"):
            val = data.get(key)
            if isinstance(val, list):
                records = val
                break
        if records is None:
            records = [data]
    else:
        records = []

    if not isinstance(records, list):
        print(f"[HOUSE OF WISDOM] {path} has unexpected structure.")
        return []

    # Check if this file uses citation-style entries (scroll_id + verse_range)
    has_citations = any(isinstance(r, dict) and r.get("scroll_id") and r.get("verse_range") for r in records if isinstance(r, dict))
    
    scrolls_cache = {}
    if has_citations:
        scrolls_cache = _get_scrolls_verse_cache()

    out: List[SourceEntry] = []
    for rec in records:
        if isinstance(rec, str):
            rec = {"text": rec}
        if not isinstance(rec, dict):
            continue

        # Handle citation-style entries
        if rec.get("scroll_id") and rec.get("verse_range"):
            citation_entries = _resolve_scroll_citation(rec, scrolls_cache)
            out.extend(citation_entries)
            continue

        # Handle regular text entries
        text = _safe_get_text(rec)
        if not text:
            continue

        ref = _safe_get_ref(rec)
        tags = _safe_get_tags(rec)
        out.append(SourceEntry(tradition=tradition, ref=ref, text=text, tags=tags))

    print(f"[HOUSE OF WISDOM] Loaded {len(out)} entries from {path.name} ({tradition}).")
    return out


# -----------------------------
# LOAD ABASID SCROLLS AS SOURCES
# -----------------------------

def _load_scroll_sources() -> List[SourceEntry]:
    """
    Load ABASID 1841 scroll verses as an extra 'SCROLL' tradition,
    via scroll_library.get_all_scrolls().

    This works even when your scroll JSON is in /static/allscrolls.json,
    because scroll_library.py now searches root + static paths.
    """
    try:
        from scroll_library import get_all_scrolls
    except Exception as e:
        print(f"[HOUSE OF WISDOM] Could not import scroll_library.get_all_scrolls: {e}")
        return []

    try:
        scrolls = get_all_scrolls() or []
    except Exception as e:
        print(f"[HOUSE OF WISDOM] Could not load scrolls via scroll_library: {e}")
        return []

    entries: List[SourceEntry] = []
    total_verses = 0

    for s in scrolls:
        book_title = (s.get("book_title") or s.get("title") or s.get("name") or "").strip()
        if not book_title:
            book_title = "Untitled Scroll"

        verses = s.get("verses") or s.get("lines") or s.get("text") or s.get("body") or []

        # Ensure list[str]
        if isinstance(verses, str):
            verses_list = [ln.strip() for ln in verses.splitlines() if ln.strip()]
            verses = verses_list if verses_list else [verses.strip()]
        elif isinstance(verses, list):
            verses = [str(v).strip() for v in verses if str(v).strip()]
        else:
            verses = []

        if not verses:
            continue

        title_tokens = [t for t in re.split(r"[^a-z0-9]+", book_title.lower()) if t]

        for idx, verse in enumerate(verses, start=1):
            text = str(verse).strip()
            if not text:
                continue
            ref = f"{book_title} – v{idx}"
            entries.append(
                SourceEntry(
                    tradition="ABASID 1841 SCROLL",
                    ref=ref,
                    text=text,
                    tags=title_tokens,
                )
            )
            total_verses += 1

    print(f"[HOUSE OF WISDOM] Loaded {len(entries)} SCROLL witness entries ({total_verses} verses).")
    return entries


# -----------------------------
# MAIN LOADER
# -----------------------------

def load_all_sources(force_reload: bool = False) -> List[SourceEntry]:
    """
    Load all configured JSON sources AND ABASID scrolls into memory once.
    """
    global _ALL_SOURCES, _LOADED
    if _LOADED and _ALL_SOURCES and not force_reload:
        return _ALL_SOURCES

    all_entries: List[SourceEntry] = []

    # 1) External JSON sources in ./sources
    if not SOURCES_DIR.is_dir():
        print(f"[HOUSE OF WISDOM] Sources dir not found at {SOURCES_DIR}")
    else:
        for filename, tradition in SOURCE_FILES.items():
            path = SOURCES_DIR / filename
            if not path.is_file():
                print(f"[HOUSE OF WISDOM] Missing source file {path.name}")
                continue
            entries = _load_source_file(path, tradition)
            all_entries.extend(entries)

    # 2) ABASID scrolls from scroll_library (root or static)
    scroll_entries = _load_scroll_sources()
    all_entries.extend(scroll_entries)

    _ALL_SOURCES = all_entries
    _LOADED = True
    print(f"[HOUSE OF WISDOM] Total entries loaded: {len(_ALL_SOURCES)}")
    return _ALL_SOURCES


# -----------------------------
# SEARCH
# -----------------------------

def _tokenize(text: str) -> List[str]:
    """
    Simple tokenizer: lower-case, split on non-letters.
    """
    text = (text or "").lower()
    return [t for t in re.split(r"[^a-z0-9]+", text) if t]


def _score_entry(entry: SourceEntry, q_lower: str, q_tokens: set) -> float:
    """
    Scoring:
    - +2 for exact phrase match
    - +1 per token overlap
    - +1 per tag overlap token
    """
    text_lower = entry.text.lower()
    score = 0.0

    if q_lower and q_lower in text_lower:
        score += 2.0

    if q_tokens:
        tokens_text = set(_tokenize(entry.text))
        score += float(len(q_tokens.intersection(tokens_text)))

    if entry.tags and q_tokens:
        score += float(len(q_tokens.intersection(set(entry.tags))))

    return score


def search_sources(
    query: str,
    max_results: int = 8,
    per_tradition_cap: int = 3,   # ✅ prevents MASOWE dominating
) -> List[SourceEntry]:
    """
    Keyword search over all sources (external + scrolls).

    per_tradition_cap:
      Limits how many results from one tradition can appear in the final list.
      Keeps "MASOWE" from crowding out SCROLL/BIBLE/QURAN when it has many matches.
    """
    query = (query or "").strip()
    if not query:
        return []

    entries = load_all_sources()
    if not entries:
        return []

    q_lower = query.lower()
    q_tokens = set(_tokenize(query))

    scored: List[Tuple[float, SourceEntry]] = []
    for entry in entries:
        score = _score_entry(entry, q_lower, q_tokens)
        if score > 0:
            scored.append((score, entry))

    scored.sort(key=lambda x: x[0], reverse=True)

    # Apply per-tradition cap
    out: List[SourceEntry] = []
    counts: Dict[str, int] = {}

    for _, e in scored:
        t = (e.tradition or "").upper().strip()
        counts.setdefault(t, 0)
        if per_tradition_cap > 0 and counts[t] >= per_tradition_cap:
            continue
        out.append(e)
        counts[t] += 1
        if len(out) >= max_results:
            break

    return out