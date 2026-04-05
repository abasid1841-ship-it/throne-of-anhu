# scroll_library.py
# THRONE OF ANHU · Scroll Library Loader + Search Helpers
#
# IMPORTANT:
# Your ABASID 1841 scrolls live in:
#   static/allscrolls.json  (and/or static/scrolls.json)
#
# This library searches both root and /static paths.
# It also exposes the functions expected by:
#   - local_storehouse.py
#   - throne_engine.py
#   - source_library.py

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

BASE_DIR = Path(__file__).resolve().parent

SCROLLS_PATH_CANDIDATES: List[Path] = [
    BASE_DIR / "allscrolls.json" / "scrolls.json",
    BASE_DIR / "static" / "allscrolls.json" / "scrolls.json",
    BASE_DIR / "allscrolls.json",
    BASE_DIR / "scrolls.json",
    BASE_DIR / "data" / "allscrolls.json",
    BASE_DIR / "data" / "scrolls.json",
    BASE_DIR / "static" / "allscrolls.json",
    BASE_DIR / "static" / "scrolls.json",
]

ADDITIONAL_SCROLL_SOURCES: List[Path] = [
    BASE_DIR / "sources" / "gospel_god_church_baba_johane.json",
    BASE_DIR / "static" / "allscrolls.json" / "baba_johane_life_events.json",
    BASE_DIR / "allscrolls.json" / "baba_johane_life_events.json",
    BASE_DIR / "allscrolls.json" / "abasid_1841_scrolls.json",
    BASE_DIR / "static" / "allscrolls.json" / "abasid_1841_scrolls.json",
    BASE_DIR / "static" / "allscrolls.json" / "nhoroondo_dzababa_johanne.json",
    BASE_DIR / "allscrolls.json" / "nhoroondo_dzababa_johanne.json",
    BASE_DIR / "static" / "allscrolls.json" / "alphabet_of_baba_johani.json",
    BASE_DIR / "allscrolls.json" / "alphabet_of_baba_johani.json",
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
    BASE_DIR / "sources" / "planet_7_moon_zimbabwe" / "shona_history_sekuru_chigamba.json",
    BASE_DIR / "sources" / "planet_2_jupiter_abasid" / "scroll_of_existence_abakara.json",
    BASE_DIR / "sources" / "planet_2_jupiter_abasid" / "book_of_the_measure.json",
    BASE_DIR / "sources" / "planet_2_jupiter_abasid" / "book_of_the_witness.json",
    BASE_DIR / "sources" / "planet_2_jupiter_abasid" / "book_of_life_1841.json",
    # THE ABASID CALIPHATE Collection (25 scrolls, compiled Jan 2026 by Lord Blessed Murove)
    BASE_DIR / "sources" / "planet_2_jupiter_abasid" / "abasid_caliphate_2026" / "scroll_01_mwari_wedu_mumwe_chete.json",
    BASE_DIR / "sources" / "planet_2_jupiter_abasid" / "abasid_caliphate_2026" / "scroll_02_zuva_reva_tema.json",
    BASE_DIR / "sources" / "planet_2_jupiter_abasid" / "abasid_caliphate_2026" / "scroll_03_shona_ndi_john.json",
    BASE_DIR / "sources" / "planet_2_jupiter_abasid" / "abasid_caliphate_2026" / "scroll_04_kukosha_kwebvudzi.json",
    BASE_DIR / "sources" / "planet_2_jupiter_abasid" / "abasid_caliphate_2026" / "scroll_05_pio.json",
    BASE_DIR / "sources" / "planet_2_jupiter_abasid" / "abasid_caliphate_2026" / "scroll_06_izwi.json",
    BASE_DIR / "sources" / "planet_2_jupiter_abasid" / "abasid_caliphate_2026" / "scroll_07_hamheno_shona_mutauro.json",
    BASE_DIR / "sources" / "planet_2_jupiter_abasid" / "abasid_caliphate_2026" / "scroll_08_mwari_mumwe_chete_se_zuva.json",
    BASE_DIR / "sources" / "planet_2_jupiter_abasid" / "abasid_caliphate_2026" / "scroll_09_angles_engels_engirosi.json",
    BASE_DIR / "sources" / "planet_2_jupiter_abasid" / "abasid_caliphate_2026" / "scroll_10_maonero_aani_na_ani.json",
    BASE_DIR / "sources" / "planet_2_jupiter_abasid" / "abasid_caliphate_2026" / "scroll_11_chaminuka_ndimambo.json",
    BASE_DIR / "sources" / "planet_2_jupiter_abasid" / "abasid_caliphate_2026" / "scroll_12_dna_ndo_alphabet_yeshona.json",
    BASE_DIR / "sources" / "planet_2_jupiter_abasid" / "abasid_caliphate_2026" / "scroll_13_kuyera_kwa_ra.json",
    BASE_DIR / "sources" / "planet_2_jupiter_abasid" / "abasid_caliphate_2026" / "scroll_14_karanga.json",
    BASE_DIR / "sources" / "planet_2_jupiter_abasid" / "abasid_caliphate_2026" / "scroll_15_muporofiti_wemata.json",
    BASE_DIR / "sources" / "planet_2_jupiter_abasid" / "abasid_caliphate_2026" / "scroll_16_shona_ndimi.json",
    BASE_DIR / "sources" / "planet_2_jupiter_abasid" / "abasid_caliphate_2026" / "scroll_17_rungano_rwa_gure.json",
    BASE_DIR / "sources" / "planet_2_jupiter_abasid" / "abasid_caliphate_2026" / "scroll_18_kuraswa_nezwi.json",
    BASE_DIR / "sources" / "planet_2_jupiter_abasid" / "abasid_caliphate_2026" / "scroll_19_ani_na_ani_anenyenyedzi_take.json",
    BASE_DIR / "sources" / "planet_2_jupiter_abasid" / "abasid_caliphate_2026" / "scroll_20_tisu_anhu_acho.json",
    BASE_DIR / "sources" / "planet_2_jupiter_abasid" / "abasid_caliphate_2026" / "scroll_21_hapana_anoziva_someone.json",
    BASE_DIR / "sources" / "planet_2_jupiter_abasid" / "abasid_caliphate_2026" / "scroll_22_re_nje_nje_re.json",
    BASE_DIR / "sources" / "planet_2_jupiter_abasid" / "abasid_caliphate_2026" / "scroll_23_kumuka_kwevakafa.json",
    BASE_DIR / "sources" / "planet_2_jupiter_abasid" / "abasid_caliphate_2026" / "scroll_24_ivai_vanotenda.json",
    BASE_DIR / "sources" / "planet_2_jupiter_abasid" / "abasid_caliphate_2026" / "scroll_25_idi_harisi_rakareruka_kuriparidza.json",
    BASE_DIR / "sources" / "planet_2_jupiter_abasid" / "gospels_of_iyesu.json",
    # ABASID 1841 own scrolls (not disciple scrolls)
    BASE_DIR / "sources" / "planet_2_jupiter_abasid" / "the_voice_from_the_throne.json",
    BASE_DIR / "sources" / "planet_2_jupiter_abasid" / "shoko_ra_mwari.json",
]

# In-memory cache
_SCROLLS_CACHE: Optional[List[dict]] = None
_SCROLLS_PATHS_USED: List[Path] = []


def _read_json_file(path: Path) -> Optional[Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[SCROLL LIBRARY] Could not read {path}: {e}")
        return None


def _normalise_scroll_record(s: dict) -> dict:
    """
    Ensure we have consistent keys:
      book_title, verses (list[str]), tags(list[str]), series(str)
    """
    if not isinstance(s, dict):
        return {}

    title = (
        s.get("book_title")
        or s.get("title")
        or s.get("name")
        or s.get("scroll_title")
        or "Untitled Scroll"
    )

    verses = (
        s.get("verses")
        or s.get("lines")
        or s.get("text")
        or s.get("body")
        or []
    )

    # If verses is a string, make it a 1-item list
    if isinstance(verses, str):
        verses = [verses]
    if not isinstance(verses, list):
        verses = []

    # Normalize verses - extract text from dict format or use string directly
    normalized_verses = []
    for v in verses:
        if isinstance(v, dict):
            text = str(v.get("text") or v.get("verse_text") or v.get("content") or "").strip()
        else:
            text = str(v).strip()
        if text:
            normalized_verses.append(text)
    verses = normalized_verses

    tags = s.get("tags") or s.get("keywords") or s.get("topics") or []
    if isinstance(tags, str):
        tags = [tags]
    if not isinstance(tags, list):
        tags = []
    tags = [str(t).strip().lower() for t in tags if str(t).strip()]

    series = s.get("series") or ""

    out = dict(s)
    out["book_title"] = str(title).strip()
    out["verses"] = verses
    out["tags"] = tags
    out["series"] = series
    out["verses_count"] = len(verses)
    return out


def _extract_scrolls_from_json(data: Any) -> List[dict]:
    """Extract scroll list from JSON data (handles dict wrapper, single scroll, or direct list)."""
    if isinstance(data, dict):
        for key in ("scrolls", "items", "entries", "records"):
            if isinstance(data.get(key), list):
                return data[key]
        if data.get("verses") or data.get("book_title") or data.get("scroll_id"):
            return [data]
        return []
    if isinstance(data, list):
        return data
    return []


def _load_scrolls_from_disk() -> List[dict]:
    global _SCROLLS_CACHE, _SCROLLS_PATHS_USED

    if _SCROLLS_CACHE is not None:
        return _SCROLLS_CACHE

    all_scrolls: List[dict] = []
    paths_used: List[Path] = []

    chosen: Optional[Path] = None
    for p in SCROLLS_PATH_CANDIDATES:
        if p.exists() and p.is_file():
            chosen = p
            break

    if chosen is not None:
        data = _read_json_file(chosen)
        if data is not None:
            items = _extract_scrolls_from_json(data)
            for s in items:
                if isinstance(s, dict):
                    norm = _normalise_scroll_record(s)
                    if norm.get("book_title") and norm.get("verses"):
                        all_scrolls.append(norm)
            paths_used.append(chosen)
            print(f"[SCROLL LIBRARY] Loaded {len(all_scrolls)} scroll(s) from {chosen}")
    else:
        print("[SCROLL LIBRARY] WARNING: No primary scrolls.json / allscrolls.json found.")

    loaded_files = set()
    for extra_path in ADDITIONAL_SCROLL_SOURCES:
        if extra_path.exists() and extra_path.is_file():
            if extra_path.name in loaded_files:
                continue
            data = _read_json_file(extra_path)
            if data is not None:
                items = _extract_scrolls_from_json(data)
                count_before = len(all_scrolls)
                for s in items:
                    if isinstance(s, dict):
                        norm = _normalise_scroll_record(s)
                        if norm.get("book_title") and norm.get("verses"):
                            all_scrolls.append(norm)
                count_added = len(all_scrolls) - count_before
                loaded_files.add(extra_path.name)
                paths_used.append(extra_path)
                print(f"[SCROLL LIBRARY] Loaded {count_added} additional scroll(s) from {extra_path.name}")

    _SCROLLS_CACHE = all_scrolls
    _SCROLLS_PATHS_USED = paths_used
    print(f"[SCROLL LIBRARY] Total scrolls available: {len(all_scrolls)}")
    return all_scrolls


def get_all_scrolls() -> List[dict]:
    """
    Public API used by source_library.py and other modules.
    """
    return _load_scrolls_from_disk()


def _norm_text(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def find_scroll_by_title_like(title: str, language: str = "ENGLISH") -> Optional[dict]:
    """
    Find a scroll by approximate title match.
    """
    if not title:
        return None

    q = _norm_text(title)
    scrolls = get_all_scrolls()

    # Exact-ish match first
    for s in scrolls:
        t = _norm_text(s.get("book_title") or "")
        if t == q:
            return s

    # Contains match
    for s in scrolls:
        t = _norm_text(s.get("book_title") or "")
        if q in t or t in q:
            return s

    # Token overlap fallback
    q_tokens = set(re.split(r"[^a-z0-9]+", q))
    best: Tuple[int, Optional[dict]] = (0, None)
    for s in scrolls:
        t = _norm_text(s.get("book_title") or "")
        t_tokens = set(re.split(r"[^a-z0-9]+", t))
        score = len(q_tokens.intersection(t_tokens))
        if score > best[0]:
            best = (score, s)

    return best[1] if best[0] > 0 else None


def find_relevant_scrolls(query: str, top_k: int = 3) -> List[dict]:
    """
    Simple keyword-based relevance finder across title + verses.
    Used by throne_engine.py fallback path.
    """
    q = _norm_text(query)
    if not q:
        return []

    q_tokens = [t for t in re.split(r"[^a-z0-9]+", q) if t]
    scrolls = get_all_scrolls()
    scored: List[Tuple[float, dict]] = []

    for s in scrolls:
        title = _norm_text(s.get("book_title") or "")
        verses = s.get("verses") or []
        body = " ".join(_norm_text(v) for v in verses[:200])  # cap work

        hay = f"{title} {body}"

        score = 0.0
        if q in hay:
            score += 3.0

        # token overlap
        for tok in q_tokens:
            if tok and tok in hay:
                score += 1.0

        # tag overlap
        tags = s.get("tags") or []
        for tok in q_tokens:
            if tok in tags:
                score += 0.75

        if score > 0:
            scored.append((score, s))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [s for _, s in scored[: max(1, int(top_k))]]


def get_scroll_slice(title: str, start_verse: int, end_verse: int) -> str:
    """
    Return verses start_verse..end_verse inclusive (1-based indices in UI).
    Used by throne_engine pinned scroll sections.
    """
    s = find_scroll_by_title_like(title)
    if not s:
        return ""

    verses = s.get("verses") or []
    if not verses:
        return ""

    # UI expects 1-based, python is 0-based
    a = max(1, int(start_verse))
    b = max(a, int(end_verse))
    a0 = a - 1
    b0 = b

    chunk = verses[a0:b0]
    return "\n".join(str(v) for v in chunk if str(v).strip())