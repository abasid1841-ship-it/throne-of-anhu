# models.py — Pydantic models + Scroll loader for Throne of Anhu

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import os

from pydantic import BaseModel, Field, validator


# -------------------------------------------------------------------
# API MODELS
# -------------------------------------------------------------------

class ThroneRequest(BaseModel):
    """
    Payload from the frontend:

    - message: what the user asked
    - language: "ENGLISH", "SHONA", etc.
    - pinned_scroll_title: optional scroll to pin as primary context
    - pinned_section: optional slice:
          { "start_verse": int, "end_verse": int }
    - conversation_id: optional ID for conversation continuity
    - client_mode: the mode selected by the user ("outer_court", "inner_court", "holy_of_holies")
    """
    message: str = Field(..., min_length=1)
    language: str = "ENGLISH"
    pinned_scroll_title: Optional[str] = None
    pinned_section: Optional[Dict[str, Any]] = None
    conversation_id: Optional[str] = None
    client_mode: Optional[str] = None

    @validator("language", pre=True)
    def _norm_lang(cls, v: Any) -> str:
        s = (v or "ENGLISH")
        return str(s).strip().upper()

    @validator("message", pre=True)
    def _strip_message(cls, v: Any) -> str:
        return str(v or "").strip()


class ThroneResponse(BaseModel):
    """
    Unified response model for /api/throne.

    persona:
      "RA"  – outer court (Sun voice)
      "DZI" – inner court (teacher)
      "MA"  – holy of holies (law / verdict)

    mode:
      "outer_court" | "inner_court" | "holy_of_holies"

    answer:
      The main text that the Throne speaks back.

    witnesses:
      Optional list of witness lines for HOUSE OF WISDOM UI panel.

      IMPORTANT: Always a list (or None), never a single string.
      This avoids schema drift across different code paths.

    key_verses:
      Optional list of verse indices that MA used in judgement mode.
    
    conversation_id:
      Optional ID for conversation continuity.
    
    offer_metadata:
      Optional metadata about what was offered to the user.
      Used for intelligent follow-up handling when user says "yes" to an offer.
      Contains: offer_type, related_topics, power_teaching_id
    """
    persona: str
    mode: str
    answer: str
    witnesses: Optional[List[str]] = None
    key_verses: Optional[List[int]] = None
    conversation_id: Optional[str] = None
    offer_metadata: Optional[Dict[str, Any]] = None

    @validator("persona", pre=True)
    def _norm_persona(cls, v: Any) -> str:
        return str(v or "RA").strip().upper()

    @validator("mode", pre=True)
    def _norm_mode(cls, v: Any) -> str:
        return str(v or "outer_court").strip()

    @validator("answer", pre=True)
    def _norm_answer(cls, v: Any) -> str:
        return str(v or "").strip()


# -------------------------------------------------------------------
# SCROLL LIBRARY LOADER (robust + flexible)
# -------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

# If you ever want to override via env in production:
#   THRONE_SCROLLS_PATH=/abs/path/to/scrolls.json
ENV_SCROLLS_PATH = os.environ.get("THRONE_SCROLLS_PATH")

# Your special layout:
#   /allscrolls.json/scrolls.json   ← folder named allscrolls.json
SPECIAL_DIR_LAYOUT = BASE_DIR / "allscrolls.json" / "scrolls.json"

# Common layouts across deployments:
CANDIDATES: List[Path] = []
if ENV_SCROLLS_PATH:
    CANDIDATES.append(Path(ENV_SCROLLS_PATH))

CANDIDATES.extend(
    [
        SPECIAL_DIR_LAYOUT,
        BASE_DIR / "scrolls.json",
        BASE_DIR / "allscrolls.json",
        BASE_DIR / "data" / "scrolls.json",
        BASE_DIR / "data" / "allscrolls.json",
    ]
)

ADDITIONAL_SCROLL_SOURCES: List[Path] = [
    BASE_DIR / "sources" / "gospel_god_church_baba_johane.json",
    BASE_DIR / "allscrolls.json" / "abasid_1841_scrolls.json",
    BASE_DIR / "static" / "allscrolls.json" / "abasid_1841_scrolls.json",
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
    BASE_DIR / "sources" / "planet_2_jupiter_abasid" / "gospels_of_iyesu.json",
    BASE_DIR / "sources" / "planet_2_jupiter_abasid" / "the_voice_from_the_throne.json",
    BASE_DIR / "sources" / "planet_2_jupiter_abasid" / "shoko_ra_mwari.json",
]

SCROLLS: List[Dict[str, Any]] = []
_loaded_from: Optional[str] = None


def load_scrolls(force_reload: bool = False) -> List[Dict[str, Any]]:
    """
    Load the scroll library once (or reload on demand).
    Returns a list of scroll dicts including additional scroll sources.
    """
    global SCROLLS, _loaded_from

    if SCROLLS and not force_reload:
        return SCROLLS

    all_scrolls: List[Dict[str, Any]] = []

    for p in CANDIDATES:
        try:
            if p and p.is_file():
                data = json.loads(p.read_text(encoding="utf-8"))
                if isinstance(data, dict) and "scrolls" in data:
                    data = data["scrolls"]
                if isinstance(data, list):
                    all_scrolls.extend(data)
                    _loaded_from = str(p)
                    print(f"[THRONE] Loaded {len(data)} scrolls from {p}")
                    break
        except Exception as e:
            print(f"[THRONE] WARNING: Could not load scrolls from {p}: {e}")

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
                        print(f"[THRONE] Loaded single scroll from {extra_p.name}")
                        continue
                if isinstance(data, list):
                    for scroll_item in data:
                        if isinstance(scroll_item, dict) and "verses" in scroll_item:
                            vlist = scroll_item["verses"]
                            if vlist and isinstance(vlist[0], dict):
                                scroll_item["verses"] = [
                                    str(v.get("text") or v.get("verse_text") or v.get("content") or "")
                                    for v in vlist if isinstance(v, dict)
                                ]
                    all_scrolls.extend(data)
                    loaded_files.add(extra_p.name)
                    print(f"[THRONE] Loaded {len(data)} additional scrolls from {extra_p.name}")
        except Exception as e:
            print(f"[THRONE] WARNING: Could not load additional scrolls from {extra_p}: {e}")

    if all_scrolls:
        SCROLLS = all_scrolls
        print(f"[THRONE] Total scrolls available: {len(SCROLLS)}")
    else:
        SCROLLS = []
        _loaded_from = None
        print("[THRONE] WARNING: No scroll library found. The Throne may be silent.")

    return SCROLLS


# Load on import (safe) — can be reloaded later with load_scrolls(force_reload=True)
load_scrolls(force_reload=False)