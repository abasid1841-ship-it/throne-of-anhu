"""
Bible Library - KJV Bible lookup and search system.
Supports verse references like "Isaiah 45:7" and topic searches.
Cross-references with Abasid scrolls.
"""
import json
import re
import os
from typing import Optional, List, Dict, Tuple

_BIBLE_CACHE = None
_BOOK_ALIASES = {
    "gen": "Genesis", "genesis": "Genesis",
    "exod": "Exodus", "exodus": "Exodus", "ex": "Exodus",
    "lev": "Leviticus", "leviticus": "Leviticus",
    "num": "Numbers", "numbers": "Numbers",
    "deut": "Deuteronomy", "deuteronomy": "Deuteronomy", "dt": "Deuteronomy",
    "josh": "Joshua", "joshua": "Joshua",
    "judg": "Judges", "judges": "Judges",
    "ruth": "Ruth",
    "1 sam": "1 Samuel", "1 samuel": "1 Samuel", "1sam": "1 Samuel",
    "2 sam": "2 Samuel", "2 samuel": "2 Samuel", "2sam": "2 Samuel",
    "1 kings": "1 Kings", "1 kgs": "1 Kings", "1kings": "1 Kings",
    "2 kings": "2 Kings", "2 kgs": "2 Kings", "2kings": "2 Kings",
    "1 chron": "1 Chronicles", "1 chronicles": "1 Chronicles", "1chron": "1 Chronicles",
    "2 chron": "2 Chronicles", "2 chronicles": "2 Chronicles", "2chron": "2 Chronicles",
    "ezra": "Ezra",
    "neh": "Nehemiah", "nehemiah": "Nehemiah",
    "esth": "Esther", "esther": "Esther",
    "job": "Job",
    "ps": "Psalms", "psalm": "Psalms", "psalms": "Psalms", "psa": "Psalms",
    "prov": "Proverbs", "proverbs": "Proverbs", "pr": "Proverbs",
    "eccl": "Ecclesiastes", "ecclesiastes": "Ecclesiastes", "ecc": "Ecclesiastes",
    "song": "Song of Solomon", "song of solomon": "Song of Solomon", "sos": "Song of Solomon",
    "isa": "Isaiah", "isaiah": "Isaiah",
    "jer": "Jeremiah", "jeremiah": "Jeremiah",
    "lam": "Lamentations", "lamentations": "Lamentations",
    "ezek": "Ezekiel", "ezekiel": "Ezekiel", "eze": "Ezekiel",
    "dan": "Daniel", "daniel": "Daniel",
    "hos": "Hosea", "hosea": "Hosea",
    "joel": "Joel",
    "amos": "Amos",
    "obad": "Obadiah", "obadiah": "Obadiah",
    "jonah": "Jonah", "jon": "Jonah",
    "mic": "Micah", "micah": "Micah",
    "nah": "Nahum", "nahum": "Nahum",
    "hab": "Habakkuk", "habakkuk": "Habakkuk",
    "zeph": "Zephaniah", "zephaniah": "Zephaniah",
    "hag": "Haggai", "haggai": "Haggai",
    "zech": "Zechariah", "zechariah": "Zechariah",
    "mal": "Malachi", "malachi": "Malachi",
    "matt": "Matthew", "matthew": "Matthew", "mt": "Matthew",
    "mark": "Mark", "mk": "Mark",
    "luke": "Luke", "lk": "Luke",
    "john": "John", "jn": "John",
    "acts": "Acts",
    "rom": "Romans", "romans": "Romans",
    "1 cor": "1 Corinthians", "1 corinthians": "1 Corinthians", "1cor": "1 Corinthians",
    "2 cor": "2 Corinthians", "2 corinthians": "2 Corinthians", "2cor": "2 Corinthians",
    "gal": "Galatians", "galatians": "Galatians",
    "eph": "Ephesians", "ephesians": "Ephesians",
    "phil": "Philippians", "philippians": "Philippians",
    "col": "Colossians", "colossians": "Colossians",
    "1 thess": "1 Thessalonians", "1 thessalonians": "1 Thessalonians", "1thess": "1 Thessalonians",
    "2 thess": "2 Thessalonians", "2 thessalonians": "2 Thessalonians", "2thess": "2 Thessalonians",
    "1 tim": "1 Timothy", "1 timothy": "1 Timothy", "1tim": "1 Timothy",
    "2 tim": "2 Timothy", "2 timothy": "2 Timothy", "2tim": "2 Timothy",
    "titus": "Titus", "tit": "Titus",
    "philem": "Philemon", "philemon": "Philemon", "phlm": "Philemon",
    "heb": "Hebrews", "hebrews": "Hebrews",
    "james": "James", "jas": "James",
    "1 pet": "1 Peter", "1 peter": "1 Peter", "1pet": "1 Peter",
    "2 pet": "2 Peter", "2 peter": "2 Peter", "2pet": "2 Peter",
    "1 john": "1 John", "1john": "1 John", "1 jn": "1 John",
    "2 john": "2 John", "2john": "2 John", "2 jn": "2 John",
    "3 john": "3 John", "3john": "3 John", "3 jn": "3 John",
    "jude": "Jude",
    "rev": "Revelation", "revelation": "Revelation", "revelations": "Revelation",
}

def load_bible() -> Dict[str, str]:
    """Load the KJV Bible from JSON file."""
    global _BIBLE_CACHE
    if _BIBLE_CACHE is not None:
        return _BIBLE_CACHE
    
    bible_path = os.path.join(os.path.dirname(__file__), "sources", "kjv_bible.json")
    if not os.path.exists(bible_path):
        print(f"[BIBLE] Bible file not found at {bible_path}")
        return {}
    
    with open(bible_path, "r", encoding="utf-8") as f:
        _BIBLE_CACHE = json.load(f)
    
    print(f"[BIBLE] Loaded {len(_BIBLE_CACHE)} verses from KJV Bible")
    return _BIBLE_CACHE

def normalize_book_name(book: str) -> str:
    """Normalize a book name to its canonical form."""
    book_lower = book.lower().strip()
    return _BOOK_ALIASES.get(book_lower, book.title())

def parse_bible_reference(query: str) -> Optional[Tuple[str, int, int, Optional[int]]]:
    """
    Parse a Bible reference like 'Isaiah 45:7' or 'John 3:16-18'.
    Returns (book, chapter, verse_start, verse_end) or None if not a reference.
    ONLY matches known Bible book names to avoid false positives like "Geneology of Abasid 1841".
    """
    patterns = [
        r'^(\d?\s*[a-zA-Z]+(?:\s+of\s+[a-zA-Z]+)?)\s+(\d+)\s*:\s*(\d+)\s*-\s*(\d+)$',
        r'^(\d?\s*[a-zA-Z]+(?:\s+of\s+[a-zA-Z]+)?)\s+(\d+)\s*:\s*(\d+)$',
        r'^(\d?\s*[a-zA-Z]+(?:\s+of\s+[a-zA-Z]+)?)\s+(\d+)$',
    ]
    
    query = query.strip()
    
    for pattern in patterns:
        match = re.match(pattern, query, re.IGNORECASE)
        if match:
            groups = match.groups()
            raw_book = groups[0].strip()
            book = normalize_book_name(raw_book)
            
            # CRITICAL: Only accept KNOWN Bible book names
            # This prevents false positives like "Geneology Of Abasid 1841"
            book_lower = raw_book.lower().strip()
            if book_lower not in _BOOK_ALIASES:
                # Not a known Bible book - reject this match
                continue
            
            chapter = int(groups[1])
            if len(groups) >= 3 and groups[2]:
                verse_start = int(groups[2])
                verse_end = int(groups[3]) if len(groups) == 4 and groups[3] else None
                return (book, chapter, verse_start, verse_end)
            else:
                return (book, chapter, 1, None)
    
    return None

def get_verse(reference: str) -> Optional[str]:
    """
    Get a single verse by its reference (e.g., 'Isaiah 45:7').
    Returns the verse text or None.
    """
    bible = load_bible()
    
    parsed = parse_bible_reference(reference)
    if not parsed:
        if reference in bible:
            text = bible[reference]
            text = re.sub(r'^#\s*', '', text)
            text = re.sub(r'\[([^\]]+)\]', r'\1', text)
            return text
        return None
    
    book, chapter, verse_start, verse_end = parsed
    ref_key = f"{book} {chapter}:{verse_start}"
    
    if ref_key in bible:
        text = bible[ref_key]
        text = re.sub(r'^#\s*', '', text)
        text = re.sub(r'\[([^\]]+)\]', r'\1', text)
        return text
    
    return None

def get_verses(reference: str) -> List[Dict[str, str]]:
    """
    Get one or more verses by reference (e.g., 'Isaiah 45:7' or 'John 3:16-18').
    Returns list of {reference, text} dicts.
    """
    bible = load_bible()
    results = []
    
    parsed = parse_bible_reference(reference)
    if not parsed:
        if reference in bible:
            text = bible[reference]
            text = re.sub(r'^#\s*', '', text)
            text = re.sub(r'\[([^\]]+)\]', r'\1', text)
            results.append({"reference": reference, "text": text})
        return results
    
    book, chapter, verse_start, verse_end = parsed
    
    if verse_end is None:
        verse_end = verse_start
    
    for v in range(verse_start, verse_end + 1):
        ref_key = f"{book} {chapter}:{v}"
        if ref_key in bible:
            text = bible[ref_key]
            text = re.sub(r'^#\s*', '', text)
            text = re.sub(r'\[([^\]]+)\]', r'\1', text)
            results.append({"reference": ref_key, "text": text})
    
    return results

def search_bible_topic(topic: str, limit: int = 5) -> List[Dict[str, str]]:
    """
    Search the Bible for verses related to a topic.
    Returns list of {reference, text} dicts.
    """
    bible = load_bible()
    results = []
    
    topic_words = topic.lower().split()
    
    for ref, text in bible.items():
        text_lower = text.lower()
        if all(word in text_lower for word in topic_words):
            clean_text = re.sub(r'^#\s*', '', text)
            clean_text = re.sub(r'\[([^\]]+)\]', r'\1', clean_text)
            results.append({"reference": ref, "text": clean_text})
            if len(results) >= limit:
                break
    
    return results

def find_verse_reference_in_text(query: str) -> Optional[str]:
    """
    Find a Bible verse reference anywhere in the text.
    Returns the first found reference or None.
    """
    book_pattern = r"(\d?\s*[A-Za-z]+(?:\s+of\s+[A-Za-z]+)?)"
    patterns = [
        rf"{book_pattern}\s+(\d+)\s*:\s*(\d+)\s*-\s*(\d+)",
        rf"{book_pattern}\s+(\d+)\s*:\s*(\d+)",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            groups = match.groups()
            book = normalize_book_name(groups[0])
            if book.lower() in [alias.lower() for alias in _BOOK_ALIASES.values()] or book.lower() in _BOOK_ALIASES:
                return match.group(0).strip()
    
    return None

def is_bible_query(query: str) -> bool:
    """
    Detect if a query is asking about the Bible or a specific verse.
    Now detects verses embedded anywhere in the query.
    """
    query_lower = query.lower()
    
    quran_indicators = ["surah", "sura", "quran", "ayah", "ayat", "koran"]
    for qi in quran_indicators:
        if qi in query_lower:
            return False
    
    if parse_bible_reference(query):
        return True
    
    if find_verse_reference_in_text(query):
        return True
    
    bible_indicators = [
        "what does the bible say",
        "bible say about",
        "bible says about",
        "in the bible",
        "according to the bible",
        "bible verse",
        "scripture say",
        "scriptures say",
        "what does scripture",
        "what do scriptures",
    ]
    
    for indicator in bible_indicators:
        if indicator in query_lower:
            return True
    
    return False

def extract_topic_from_bible_query(query: str) -> str:
    """
    Extract the topic from a Bible query like 'what does the bible say about prayer'.
    """
    query_lower = query.lower()
    
    patterns = [
        r"what does the bible say about\s+(.+)",
        r"what do(?:es)? scriptures? say about\s+(.+)",
        r"bible (?:says?|verse) about\s+(.+)",
        r"according to the bible,?\s*(.+)",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, query_lower)
        if match:
            topic = match.group(1).strip()
            topic = re.sub(r'[?.!,;]+$', '', topic)
            return topic
    
    return query
