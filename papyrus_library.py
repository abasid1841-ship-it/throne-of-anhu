"""
Papyrus of Ani Library for Throne of Anhu
Provides spell lookup, reference parsing, and topic search for the Egyptian Book of the Dead.
Uses ancient Egyptian speaking style and connects to Abasid 1841 teachings.
"""

import json
import re
import os
from typing import Optional, List, Dict, Any, Tuple

PAPYRUS_PATH = "sources/papyrus_of_ani.json"

_papyrus_data: Optional[Dict] = None

CHAPTER_ALIASES = {
    "weighing of the heart": 125,
    "weighing heart": 125,
    "negative confession": 125,
    "judgment": 125,
    "forty-two gods": 125,
    "42 gods": 125,
    "confession": 125,
    "hymn to ra": 15,
    "sunrise hymn": 15,
    "hymn to osiris": 185,
    "osiris hymn": 185,
    "opening of the mouth": 23,
    "opening mouth": 23,
    "benu bird": 83,
    "phoenix": 83,
    "transformation falcon": 77,
    "golden falcon": 77,
    "fields of hetep": 110,
    "paradise": 110,
    "seven gates": 144,
    "gates": 144,
    "seven cows": 148,
    "fourteen mounds": 149,
    "mummy protection": 151,
    "shabti": 6,
    "ba soul": 89,
    "reunite ba": 89,
    "heart spell": 30,
    "protecting heart": 30,
    "going forth by day": 72,
    "coming forth by day": 72,
    "four winds": 161,
    "second death": 175,
    "atum": 17,
    "creation": 17,
    "transformation": 76,
    "snake spell": 33,
    "serpent": 87,
    "crocodile": 88,
    "swallow": 86,
    "heron": 84,
    "ptah": 82,
    "drinking water": 63,
    "burial": 1,
    "day of burial": 1,
}


def _load_papyrus() -> Dict:
    """Load the Papyrus of Ani JSON data."""
    global _papyrus_data
    if _papyrus_data is not None:
        return _papyrus_data
    
    try:
        if os.path.exists(PAPYRUS_PATH):
            with open(PAPYRUS_PATH, 'r', encoding='utf-8') as f:
                _papyrus_data = json.load(f)
                print(f"[PAPYRUS LIBRARY] Loaded {len(_papyrus_data.get('spells', []))} spells from Papyrus of Ani")
                return _papyrus_data
    except Exception as e:
        print(f"[PAPYRUS LIBRARY] Error loading: {e}")
    
    _papyrus_data = {"metadata": {}, "spells": []}
    return _papyrus_data


def get_all_spells() -> List[Dict]:
    """Get all spells from the Papyrus of Ani."""
    data = _load_papyrus()
    return data.get("spells", [])


def get_spell_by_chapter(chapter: int) -> Optional[List[Dict]]:
    """Get spell(s) by chapter number (some chapters have multiple parts)."""
    spells = get_all_spells()
    return [s for s in spells if s.get("chapter") == chapter]


def parse_papyrus_reference(text: str) -> Optional[Tuple[int, Optional[str]]]:
    """
    Parse a Papyrus of Ani reference from text.
    Returns (chapter_number, subtitle) or None.
    
    Examples:
        "Chapter 125" -> (125, None)
        "Spell 83" -> (83, None)
        "Chapter 125 Negative Confession" -> (125, "Negative Confession")
        "Weighing of the Heart" -> (125, None)
    """
    text_lower = text.lower().strip()
    
    for alias, chapter in CHAPTER_ALIASES.items():
        if alias in text_lower:
            return (chapter, None)
    
    patterns = [
        r"chapter\s*(\d+)",
        r"spell\s*(\d+)",
        r"papyrus\s*(\d+)",
        r"ani\s*(\d+)",
        r"book\s*of\s*(?:the\s*)?dead\s*(\d+)",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            chapter = int(match.group(1))
            return (chapter, None)
    
    return None


def detect_papyrus_query(text: str) -> Optional[bool]:
    """
    Detect if a query is about the Papyrus of Ani / Egyptian Book of the Dead.
    Returns:
        True - definitely about Papyrus of Ani
        False - definitely NOT about Papyrus of Ani
        None - ambiguous, should ask user for clarification
    Uses context-aware detection to avoid false matches with Shona words.
    """
    text_lower = text.lower()
    
    masowe_context = ["johani", "johane", "baba johani", "baba johane", "masowe", 
                      "vatendi", "apostolic", "abasid", "1841", "anhu", "zimbabwe",
                      "shona", "mutendi", "marange", "mwari", "tenzi", "mweya"]
    for term in masowe_context:
        if term in text_lower:
            return False
    
    shona_ani_patterns = [
        r'\bndi\s*ani\b',      # "ndi ani" = "who is" in Shona
        r'\bndiani\b',         # "ndiani" = "who is" (no space)
        r'\bani\s+uyu\b',      # "ani uyu" = "who is this"
        r'\bani\s+ari\b',      # "ani ari" = "who is"
        r'\bko\s+ani\b',       # "ko ani" = "so who"
        r'\bani\s+wacho\b',    # "who exactly"
        r'\bani\s+akati\b',    # "who said"
        r'\bani\s+ndiye\b',    # "who is the one"
        r'\bani\s+akanzi\b',   # "who was called"
        r'\bani\s+anga\b',     # "who was"
    ]
    for pattern in shona_ani_patterns:
        if re.search(pattern, text_lower):
            return False
    
    bible_indicators = ["bible", "genesis", "exodus", "leviticus", "matthew", "john", "luke", "mark", "psalm", "proverbs", "isaiah", "jeremiah", "revelation", "corinthians", "romans", "hebrews", "kjv", "new testament", "old testament"]
    quran_indicators = ["quran", "surah", "ayah", "bismillah", "al-", "muhammad", "allah", "islam"]
    gita_indicators = ["gita", "bhagavad", "krishna", "arjuna", "vedic", "sanskrit", "sloka", "yoga"]
    
    for indicator in bible_indicators + quran_indicators + gita_indicators:
        if indicator in text_lower:
            return False
    
    strong_papyrus_context = [
        "papyrus of ani", "scribe ani", "ani the scribe", "osiris ani",
        "book of the dead", "book of dead", "egyptian book",
        "weighing of the heart", "negative confession", "forty-two gods",
        "coming forth by day", "going forth by day", "per em hru",
        "hall of two truths", "fields of hetep", "chapter 125"
    ]
    for phrase in strong_papyrus_context:
        if phrase in text_lower:
            return True
    
    egyptian_context = [
        "egyptian", "egypt", "kemet", "osiris", "isis", "horus",
        "anubis", "maat", "thoth", "ptah", "atum", "nun", "netjer",
        "duat", "underworld", "afterlife", "mummy", "embalm",
        "benu", "phoenix", "sekhem", "abydos", "heliopolis", 
        "memphis", "thebes", "hieroglyph", "pharaoh", "pyramid"
    ]
    egyptian_matches = sum(1 for term in egyptian_context if term in text_lower)
    
    if egyptian_matches >= 2:
        return True
    
    if egyptian_matches == 1 and re.search(r'\bani\b', text_lower):
        return True
    
    if re.search(r'\bani\b', text_lower) and egyptian_matches == 0:
        return None
    
    return False


def search_papyrus_topic(topic: str, max_results: int = 5) -> List[Dict]:
    """
    Search for spells related to a topic.
    Returns matching spells with relevance scores.
    """
    spells = get_all_spells()
    if not spells:
        return []
    
    topic_lower = topic.lower()
    topic_tokens = set(re.split(r'\W+', topic_lower))
    topic_tokens.discard('')
    
    scored = []
    for spell in spells:
        score = 0
        
        title = (spell.get("title") or "").lower()
        text = (spell.get("text") or "").lower()
        section = (spell.get("section") or "").lower()
        tags = [t.lower() for t in spell.get("tags", [])]
        
        if topic_lower in title:
            score += 5
        if topic_lower in text:
            score += 3
        
        for token in topic_tokens:
            if len(token) < 3:
                continue
            if token in title:
                score += 2
            if token in text:
                score += 1
            if token in tags:
                score += 3
            if token in section:
                score += 1
        
        if score > 0:
            scored.append((score, spell))
    
    scored.sort(key=lambda x: x[0], reverse=True)
    return [s[1] for s in scored[:max_results]]


def get_spell_display_text(spell: Dict) -> str:
    """Format a spell for display."""
    chapter = spell.get("chapter", "?")
    title = spell.get("title", "Unknown Spell")
    subtitle = spell.get("subtitle", "")
    section = spell.get("section", "")
    text = spell.get("text", "")
    
    display = f"Chapter {chapter}: {title}"
    if subtitle:
        display += f" ({subtitle})"
    if section:
        display += f" [{section}]"
    display += f"\n\n{text}"
    
    return display


def find_abasid_crossreferences(spell: Dict) -> List[str]:
    """
    Find Abasid scroll topics that relate to this Egyptian spell.
    Returns list of suggested search terms for Abasid scrolls.
    """
    tags = spell.get("tags", [])
    crossref_mapping = {
        "judgment": ["judgment", "day of judgment", "weighing", "balance", "maat"],
        "resurrection": ["resurrection", "rise from the dead", "eternal life"],
        "transformation": ["transformation", "change", "becoming"],
        "creation": ["creation", "beginning", "first", "primordial"],
        "osiris": ["osiris", "lord", "king", "ruler"],
        "ra": ["sun", "light", "dawn", "ra"],
        "truth": ["truth", "maat", "righteousness"],
        "heart": ["heart", "soul", "spirit"],
        "afterlife": ["afterlife", "eternal", "everlasting"],
        "protection": ["protection", "guard", "shield"],
        "soul": ["soul", "ba", "ka", "spirit"],
        "gods": ["gods", "divine", "holy"],
    }
    
    crossrefs = []
    for tag in tags:
        tag_lower = tag.lower()
        if tag_lower in crossref_mapping:
            crossrefs.extend(crossref_mapping[tag_lower])
    
    return list(set(crossrefs))
