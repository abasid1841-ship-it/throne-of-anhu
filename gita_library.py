"""
Bhagavad Gita Library for Throne of Anhu
Provides verse lookup, reference parsing, and topic search for the Bhagavad Gita.
Uses Hindu/Vedic speaking style with reverence for Lord Krishna and Arjuna.
"""

import json
import re
import os
from typing import Optional, List, Dict, Any, Tuple

GITA_PATH = "sources/bhagavad_gita.json"

_gita_data: Optional[List[Dict]] = None

CHAPTER_NAMES = {
    1: ("Arjuna Vishada Yoga", "The Yoga of Arjuna's Dejection"),
    2: ("Sankhya Yoga", "The Yoga of Knowledge"),
    3: ("Karma Yoga", "The Yoga of Action"),
    4: ("Jnana Karma Sanyasa Yoga", "The Yoga of Knowledge and Action"),
    5: ("Karma Sanyasa Yoga", "The Yoga of Renunciation of Action"),
    6: ("Dhyana Yoga", "The Yoga of Meditation"),
    7: ("Jnana Vijnana Yoga", "The Yoga of Knowledge and Wisdom"),
    8: ("Aksara Brahma Yoga", "The Yoga of the Imperishable Brahman"),
    9: ("Raja Vidya Raja Guhya Yoga", "The Yoga of Royal Knowledge"),
    10: ("Vibhuti Yoga", "The Yoga of Divine Glories"),
    11: ("Visvarupa Darsana Yoga", "The Yoga of the Cosmic Form"),
    12: ("Bhakti Yoga", "The Yoga of Devotion"),
    13: ("Ksetra Ksetrajna Vibhaga Yoga", "The Yoga of the Field"),
    14: ("Gunatraya Vibhaga Yoga", "The Yoga of the Three Gunas"),
    15: ("Purusottama Yoga", "The Yoga of the Supreme Person"),
    16: ("Daivasura Sampad Vibhaga Yoga", "Divine and Demonic Natures"),
    17: ("Sraddhatraya Vibhaga Yoga", "The Yoga of the Three Faiths"),
    18: ("Moksa Sanyasa Yoga", "The Yoga of Liberation"),
}

DIVINE_NAMES = [
    "Krishna", "Shri Krishna", "Lord Krishna", "Bhagavan",
    "Arjuna", "Partha", "Dhananjaya", "Gudakesha",
    "Vishnu", "Narayana", "Govinda", "Madhava", "Vasudeva",
    "Brahman", "Atman", "Paramatma"
]


def load_gita() -> List[Dict]:
    """Load the complete Bhagavad Gita."""
    global _gita_data
    if _gita_data is not None:
        return _gita_data
    
    if not os.path.exists(GITA_PATH):
        print(f"[GITA] Warning: {GITA_PATH} not found")
        return []
    
    try:
        with open(GITA_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if data:
                _gita_data = data
                total_verses = sum(len(ch.get('verses', [])) for ch in data)
                print(f"[GITA] Loaded {len(_gita_data)} chapters, {total_verses} slokas")
                return _gita_data
        return []
    except Exception as e:
        print(f"[GITA] Error loading Gita: {e}")
        return []


def parse_gita_reference(query: str) -> Optional[Tuple[int, int, Optional[int]]]:
    """
    Parse a Gita reference like 'BG 2.47', 'Gita 2:47', 'Chapter 2 Verse 47'.
    Returns (chapter, verse_start, verse_end) or None.
    """
    query = query.strip()
    
    patterns = [
        r'(?:bg|gita|bhagavad\s*gita)\s*(\d+)[.:\s]+(\d+)(?:\s*[-–]\s*(\d+))?',
        r'chapter\s*(\d+)\s*(?:verse|sloka|shloka)?\s*(\d+)(?:\s*[-–]\s*(\d+))?',
        r'(\d+)[.:](\d+)(?:\s*[-–]\s*(\d+))?',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            chapter = int(match.group(1))
            verse_start = int(match.group(2))
            verse_end = int(match.group(3)) if match.group(3) else None
            if 1 <= chapter <= 18:
                return (chapter, verse_start, verse_end)
    
    return None


def find_gita_reference_in_text(text: str) -> Optional[str]:
    """Find an embedded Gita reference in text like 'Explain BG 2.47'."""
    patterns = [
        r'(?:bg|gita|bhagavad\s*gita)\s*(\d+)[.:\s]+(\d+)(?:\s*[-–]\s*(\d+))?',
        r'(\d+)[.:](\d+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    
    return None


def get_sloka(chapter: int, verse: int) -> Optional[Dict[str, Any]]:
    """Get a specific sloka with Sanskrit and translation."""
    gita = load_gita()
    
    if not gita or chapter < 1 or chapter > 18:
        return None
    
    chapter_data = gita[chapter - 1]
    verses = chapter_data.get("verses", [])
    
    for v in verses:
        if v.get("verse_number") == verse:
            ch_name = CHAPTER_NAMES.get(chapter, ("", ""))
            return {
                "chapter": chapter,
                "chapter_name": ch_name[0],
                "chapter_meaning": ch_name[1],
                "verse": verse,
                "sanskrit": v.get("sanskrit", ""),
                "transliteration": v.get("transliteration", ""),
                "word_meanings": v.get("word_meanings", ""),
                "translation": v.get("translation", ""),
                "reference": f"Bhagavad Gita {chapter}.{verse}"
            }
    
    return None


def get_sloka_range(chapter: int, start: int, end: int) -> List[Dict[str, Any]]:
    """Get a range of slokas."""
    results = []
    for verse_num in range(start, end + 1):
        sloka = get_sloka(chapter, verse_num)
        if sloka:
            results.append(sloka)
    return results


def is_gita_query(query: str) -> bool:
    """Check if this is a Bhagavad Gita-related query."""
    query_lower = query.lower()
    
    from bible_library import is_bible_query
    from quran_library import is_quran_query
    if is_bible_query(query) or is_quran_query(query):
        return False
    
    gita_indicators = [
        "what does the gita say",
        "gita say about",
        "gita says about",
        "in the gita",
        "according to the gita",
        "bhagavad gita",
        "bhagavadgita",
        "bhagwat gita",
        "shrimad bhagavad",
        "srimad bhagavad",
        "lord krishna say",
        "krishna says",
        "krishna teaches",
        "arjuna asks",
        "bg ",
        "bg:",
        "sloka",
        "shloka",
    ]
    
    for indicator in gita_indicators:
        if indicator in query_lower:
            return True
    
    if find_gita_reference_in_text(query):
        for word in ['gita', 'krishna', 'bg', 'chapter', 'sloka']:
            if word in query_lower:
                return True
    
    return False


def extract_topic_from_gita_query(query: str) -> str:
    """Extract the topic from a Gita query like 'what does the gita say about karma'."""
    query_lower = query.lower()
    
    patterns = [
        r"what does (?:the )?(?:bhagavad )?gita say about (.+)",
        r"(?:bhagavad )?gita say(?:s)? about (.+)",
        r"(?:lord )?krishna (?:say|teach|speak)(?:s|es)? about (.+)",
        r"in the (?:bhagavad )?gita about (.+)",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, query_lower)
        if match:
            return match.group(1).strip()
    
    return query


def search_gita_topic(topic: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Search for slokas about a topic."""
    gita = load_gita()
    if not gita:
        return []
    
    topic_lower = topic.lower()
    keywords = topic_lower.split()
    
    results = []
    
    for chapter_data in gita:
        chapter_num = chapter_data.get("chapter_number")
        
        for verse in chapter_data.get("verses", []):
            translation = verse.get("translation", "").lower()
            word_meanings = verse.get("word_meanings", "").lower()
            search_text = translation + " " + word_meanings
            
            if topic_lower in search_text or all(kw in search_text for kw in keywords):
                ch_name = CHAPTER_NAMES.get(chapter_num, ("", ""))
                results.append({
                    "chapter": chapter_num,
                    "chapter_name": ch_name[0],
                    "verse": verse.get("verse_number"),
                    "sanskrit": verse.get("sanskrit", ""),
                    "transliteration": verse.get("transliteration", ""),
                    "translation": verse.get("translation", ""),
                    "reference": f"Bhagavad Gita {chapter_num}.{verse.get('verse_number')}"
                })
                
                if len(results) >= limit:
                    return results
    
    return results


def format_sloka_vedic(sloka_data: Dict[str, Any], include_sanskrit: bool = True) -> str:
    """Format a sloka with Vedic/Hindu speaking style."""
    ref = sloka_data.get("reference", "")
    translation = sloka_data.get("translation", "")
    sanskrit = sloka_data.get("sanskrit", "")
    transliteration = sloka_data.get("transliteration", "")
    
    text = f"**{ref}**\n\n"
    
    if include_sanskrit and sanskrit:
        text += f"*{sanskrit.strip()}*\n\n"
    
    if transliteration:
        text += f"*{transliteration.strip()}*\n\n"
    
    text += f'"{translation}"'
    
    return text


def add_vedic_honorifics(text: str) -> str:
    """Add Vedic honorifics to divine names in text."""
    result = text
    
    result = re.sub(
        r'\b(Lord Krishna|Shri Krishna|Krishna)\b(?!\s*\()',
        r'\1 (the Supreme Personality of Godhead)',
        result,
        count=1
    )
    
    result = re.sub(
        r'\b(Arjuna)\b(?!\s*\()',
        r'\1 (the great warrior)',
        result,
        count=1
    )
    
    return result


def get_total_slokas() -> int:
    """Get total number of slokas in the Gita."""
    gita = load_gita()
    if not gita:
        return 0
    return sum(len(ch.get("verses", [])) for ch in gita)
