"""
Torah Library for Throne of Anhu
Provides verse lookup, reference parsing, and topic search for the Hebrew Torah.
Uses Hebrew terminology and speaking style with Abasid cross-references.
"""

import json
import re
import os
from typing import Optional, List, Dict, Any, Tuple

HEBREW_TORAH_PATH = "sources/hebrew_torah.json"

_torah_data: Optional[Dict] = None

BOOK_NAMES = {
    "genesis": 1, "bereshit": 1, "bereishit": 1, "בראשית": 1, "in the beginning": 1,
    "exodus": 2, "shemot": 2, "sh'mot": 2, "שמות": 2, "names": 2,
    "leviticus": 3, "vayikra": 3, "vayyiqra": 3, "ויקרא": 3, "and he called": 3,
    "numbers": 4, "bamidbar": 4, "bemidbar": 4, "במדבר": 4, "in the wilderness": 4,
    "deuteronomy": 5, "devarim": 5, "d'varim": 5, "דברים": 5, "words": 5,
}

PARSHA_NAMES = {
    "bereshit": (1, "1:1-6:8"), "noach": (1, "6:9-11:32"), "noah": (1, "6:9-11:32"),
    "lech lecha": (1, "12:1-17:27"), "vayera": (1, "18:1-22:24"),
    "chayei sarah": (1, "23:1-25:18"), "toldot": (1, "25:19-28:9"),
    "vayetze": (1, "28:10-32:3"), "vayishlach": (1, "32:4-36:43"),
    "vayeshev": (1, "37:1-40:23"), "miketz": (1, "41:1-44:17"),
    "vayigash": (1, "44:18-47:27"), "vayechi": (1, "47:28-50:26"),
    "shemot": (2, "1:1-6:1"), "vaera": (2, "6:2-9:35"), "bo": (2, "10:1-13:16"),
    "beshalach": (2, "13:17-17:16"), "yitro": (2, "18:1-20:23"), "jethro": (2, "18:1-20:23"),
    "mishpatim": (2, "21:1-24:18"), "terumah": (2, "25:1-27:19"),
    "tetzaveh": (2, "27:20-30:10"), "ki tisa": (2, "30:11-34:35"),
    "vayakhel": (2, "35:1-38:20"), "pekudei": (2, "38:21-40:38"),
}

TORAH_INDICATORS = [
    "torah", "hebrew torah", "תורה", "bereshit", "shemot", "vayikra", "bamidbar", "devarim",
    "five books of moses", "pentateuch", "chumash", "חומש",
    "moses wrote", "moshe", "משה", "abraham", "avraham", "אברהם",
    "isaac", "yitzchak", "יצחק", "jacob", "yaakov", "יעקב", "israel", "ישראל",
    "ten commandments", "aseret hadibrot", "עשרת הדברות",
    "shema yisrael", "שמע ישראל", "mount sinai", "har sinai", "הר סיני",
    "hebrew scripture", "hebrew bible", "tanakh portion",
    "parsha", "parashat", "פרשת", "sedra",
]

TORAH_EXCLUSIONS = [
    "quran", "surah", "ayah", "allah", "muhammad", "pbuh",
    "gita", "krishna", "arjuna", "bhagavad", "sloka",
    "papyrus", "osiris", "anubis", "egyptian book",
    "kjv", "new testament", "gospel", "jesus said", "apostle"
]


def load_torah() -> Dict:
    """Load the Hebrew Torah with verses."""
    global _torah_data
    if _torah_data is not None:
        return _torah_data
    
    if not os.path.exists(HEBREW_TORAH_PATH):
        print(f"[TORAH] Warning: {HEBREW_TORAH_PATH} not found")
        return {"books": [], "parshiot": []}
    
    try:
        with open(HEBREW_TORAH_PATH, 'r', encoding='utf-8') as f:
            _torah_data = json.load(f)
            book_count = len(_torah_data.get("books", []))
            verse_count = sum(len(b.get("verses", [])) for b in _torah_data.get("books", []))
            print(f"[TORAH LIBRARY] Loaded {book_count} books with {verse_count} verses from Hebrew Torah")
            return _torah_data
    except Exception as e:
        print(f"[TORAH] Error loading Torah: {e}")
        return {"books": [], "parshiot": []}


def get_all_verses() -> List[Dict]:
    """Get all Torah verses as a flat list."""
    data = load_torah()
    all_verses = []
    for book in data.get("books", []):
        book_name = book.get("name_english", "")
        book_hebrew = book.get("name_hebrew", "")
        for verse in book.get("verses", []):
            verse_copy = verse.copy()
            verse_copy["book_english"] = book_name
            verse_copy["book_hebrew"] = book_hebrew
            all_verses.append(verse_copy)
    return all_verses


def detect_torah_query(query: str) -> bool:
    """Detect if a query is asking about the Hebrew Torah."""
    q_lower = query.lower()
    
    for excl in TORAH_EXCLUSIONS:
        if excl in q_lower:
            return False
    
    for indicator in TORAH_INDICATORS:
        if indicator in q_lower:
            return True
    
    ref_pattern = r'\b(genesis|exodus|leviticus|numbers|deuteronomy|bereshit|shemot|vayikra|bamidbar|devarim)\s+\d+[:\.\s]\d+'
    if re.search(ref_pattern, q_lower):
        return True
    
    parsha_pattern = r'\b(parsha|parashat|parshat)\s+\w+'
    if re.search(parsha_pattern, q_lower):
        return True
    
    return False


def parse_torah_reference(query: str) -> Tuple[Optional[int], Optional[int], Optional[int]]:
    """Parse a Torah reference and return (book, chapter, verse) or partial match."""
    q_lower = query.lower().strip()
    
    ref_pattern = r'(\w+)\s+(\d+)[:\.\s]+(\d+)'
    match = re.search(ref_pattern, q_lower)
    if match:
        book_name = match.group(1)
        chapter = int(match.group(2))
        verse = int(match.group(3))
        book_num = BOOK_NAMES.get(book_name)
        if book_num:
            return (book_num, chapter, verse)
    
    book_chapter_pattern = r'(\w+)\s+(\d+)'
    match = re.search(book_chapter_pattern, q_lower)
    if match:
        book_name = match.group(1)
        chapter = int(match.group(2))
        book_num = BOOK_NAMES.get(book_name)
        if book_num:
            return (book_num, chapter, None)
    
    for name, book_num in BOOK_NAMES.items():
        if name in q_lower and len(name) > 3:
            return (book_num, None, None)
    
    return (None, None, None)


def get_verse(book: int, chapter: int, verse: int) -> Optional[Dict]:
    """Get a specific verse by book, chapter, and verse number."""
    data = load_torah()
    for b in data.get("books", []):
        if b.get("book") == book:
            for v in b.get("verses", []):
                if v.get("chapter") == chapter and v.get("verse") == verse:
                    result = v.copy()
                    result["book_english"] = b.get("name_english", "")
                    result["book_hebrew"] = b.get("name_hebrew", "")
                    result["book_transliterated"] = b.get("name_transliterated", "")
                    return result
    return None


def search_torah_topic(topic: str, max_results: int = 5) -> List[Dict]:
    """Search Torah verses by topic keywords."""
    import re
    clean_topic = re.sub(r'[^\w\s]', '', topic.lower())
    keywords = clean_topic.split()
    all_verses = get_all_verses()
    
    scored = []
    for v in all_verses:
        english = v.get("english", "").lower()
        hebrew = v.get("hebrew", "")
        transliteration = v.get("transliteration", "").lower()
        
        score = 0
        for kw in keywords:
            if kw in english:
                score += 2
            if kw in transliteration:
                score += 1
            for word in english.split():
                if word.startswith(kw) or kw.startswith(word[:4]) if len(word) > 4 else word == kw:
                    score += 1
        
        if score > 0:
            scored.append((score, v))
    
    scored.sort(key=lambda x: -x[0])
    return [v for _, v in scored[:max_results]]


def get_verse_display_text(verse: Dict) -> str:
    """Format a verse for display with Hebrew, transliteration, and English."""
    book = verse.get("book_english", "")
    book_heb = verse.get("book_hebrew", "")
    ch = verse.get("chapter", "")
    vs = verse.get("verse", "")
    hebrew = verse.get("hebrew", "")
    english = verse.get("english", "")
    transliteration = verse.get("transliteration", "")
    
    lines = []
    lines.append(f"**{book} ({book_heb}) {ch}:{vs}**")
    if hebrew:
        lines.append(f"*{hebrew}*")
    if transliteration:
        lines.append(f"*({transliteration})*")
    lines.append(f"> {english}")
    
    return "\n".join(lines)


def find_abasid_crossreferences(topic: str, max_results: int = 3) -> List[Dict]:
    """Find related Abasid scroll verses for Torah cross-referencing."""
    try:
        from scroll_library import get_all_scrolls
        
        keywords = topic.lower().split()
        results = []
        
        scrolls = get_all_scrolls()
        for scroll in scrolls:
            scroll_title = scroll.get("book_title", "Abasid Scroll")
            verses = scroll.get("verses", [])
            
            for i, verse in enumerate(verses):
                if isinstance(verse, dict):
                    text = verse.get("text", "").lower()
                    verse_num = verse.get("verse_num", str(i + 1))
                    verse_text = verse.get("text", "")
                elif isinstance(verse, str):
                    text = verse.lower()
                    verse_num = str(i + 1)
                    verse_text = verse
                else:
                    continue
                    
                score = sum(1 for kw in keywords if kw in text)
                if score > 0:
                    results.append({
                        "score": score,
                        "scroll_title": scroll_title,
                        "verse_num": verse_num,
                        "text": verse_text
                    })
        
        results.sort(key=lambda x: -x["score"])
        return results[:max_results]
    except Exception as e:
        print(f"[TORAH] Error finding cross-references: {e}")
        return []
