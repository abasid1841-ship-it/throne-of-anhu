# sources_loader.py
"""
Loader for House of Wisdom source texts (Torah, Bible, Qur'an, etc.).

All JSON files live in the /sources folder.
"""

from pathlib import Path
import json
from functools import lru_cache

BASE_DIR = Path(__file__).resolve().parent
SOURCES_DIR = BASE_DIR / "sources"

# Map logical keys to filenames in /sources
SOURCE_FILES = {
    "TORAH": SOURCES_DIR / "torah.json",
    "BIBLE_NT": SOURCES_DIR / "bible_nt.json",
    "QURAN": SOURCES_DIR / "quran.json",
    "MASOWE_HISTORY": SOURCES_DIR / "masowe_history.json",
    "PAPYRUS_ANI": SOURCES_DIR / "papyrus_ani.json",
    "ASTRONOMY_CYCLES": SOURCES_DIR / "astronomy_cycles.json",
}


@lru_cache(maxsize=None)
def load_source(key: str):
    """
    Return parsed JSON for a named source (cached in-memory).

    key examples:
      "TORAH", "BIBLE_NT", "QURAN", "MASOWE_HISTORY", ...
    """
    key = (key or "").upper()
    path = SOURCE_FILES.get(key)
    if not path or not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)