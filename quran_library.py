"""
Quran Library for Throne of Anhu
Provides verse lookup, reference parsing, and topic search for the Holy Quran.
Uses Islamic honorifics and speaking style.
"""

import json
import re
import os
from typing import Optional, List, Dict, Any, Tuple

QURAN_ARABIC_PATH = "sources/quran_arabic.json"
QURAN_ENGLISH_PATH = "sources/quran_english.json"

_quran_data: Optional[List[Dict]] = None
_quran_arabic: Optional[List[Dict]] = None

SURAH_NAMES = {
    "al-fatihah": 1, "fatihah": 1, "fatiha": 1, "the opener": 1,
    "al-baqarah": 2, "baqarah": 2, "baqara": 2, "the cow": 2,
    "al-imran": 3, "ali imran": 3, "imran": 3, "family of imran": 3,
    "an-nisa": 4, "nisa": 4, "women": 4, "the women": 4,
    "al-maidah": 5, "maidah": 5, "the table spread": 5,
    "al-anam": 6, "anam": 6, "the cattle": 6,
    "al-araf": 7, "araf": 7, "the heights": 7,
    "al-anfal": 8, "anfal": 8, "the spoils of war": 8,
    "at-tawbah": 9, "tawbah": 9, "taubah": 9, "repentance": 9,
    "yunus": 10, "jonah": 10,
    "hud": 11,
    "yusuf": 12, "joseph": 12,
    "ar-rad": 13, "rad": 13, "thunder": 13,
    "ibrahim": 14, "abraham": 14,
    "al-hijr": 15, "hijr": 15,
    "an-nahl": 16, "nahl": 16, "the bee": 16,
    "al-isra": 17, "isra": 17, "the night journey": 17,
    "al-kahf": 18, "kahf": 18, "the cave": 18,
    "maryam": 19, "mary": 19,
    "ta-ha": 20, "taha": 20,
    "al-anbiya": 21, "anbiya": 21, "the prophets": 21,
    "al-hajj": 22, "hajj": 22, "the pilgrimage": 22,
    "al-muminun": 23, "muminun": 23, "the believers": 23,
    "an-nur": 24, "nur": 24, "the light": 24,
    "al-furqan": 25, "furqan": 25, "the criterion": 25,
    "ash-shuara": 26, "shuara": 26, "the poets": 26,
    "an-naml": 27, "naml": 27, "the ant": 27,
    "al-qasas": 28, "qasas": 28, "the stories": 28,
    "al-ankabut": 29, "ankabut": 29, "the spider": 29,
    "ar-rum": 30, "rum": 30, "the romans": 30,
    "luqman": 31,
    "as-sajdah": 32, "sajdah": 32, "prostration": 32,
    "al-ahzab": 33, "ahzab": 33, "the combined forces": 33,
    "saba": 34, "sheba": 34,
    "fatir": 35, "originator": 35,
    "ya-sin": 36, "yasin": 36, "ya sin": 36,
    "as-saffat": 37, "saffat": 37, "those who set the ranks": 37,
    "sad": 38,
    "az-zumar": 39, "zumar": 39, "the troops": 39,
    "ghafir": 40, "the forgiver": 40,
    "fussilat": 41, "explained in detail": 41,
    "ash-shura": 42, "shura": 42, "consultation": 42,
    "az-zukhruf": 43, "zukhruf": 43, "ornaments of gold": 43,
    "ad-dukhan": 44, "dukhan": 44, "smoke": 44,
    "al-jathiyah": 45, "jathiyah": 45, "crouching": 45,
    "al-ahqaf": 46, "ahqaf": 46, "the wind-curved sandhills": 46,
    "muhammad": 47,
    "al-fath": 48, "fath": 48, "victory": 48,
    "al-hujurat": 49, "hujurat": 49, "the rooms": 49,
    "qaf": 50,
    "adh-dhariyat": 51, "dhariyat": 51, "the winnowing winds": 51,
    "at-tur": 52, "tur": 52, "the mount": 52,
    "an-najm": 53, "najm": 53, "the star": 53,
    "al-qamar": 54, "qamar": 54, "the moon": 54,
    "ar-rahman": 55, "rahman": 55, "the beneficent": 55,
    "al-waqiah": 56, "waqiah": 56, "the inevitable": 56,
    "al-hadid": 57, "hadid": 57, "iron": 57,
    "al-mujadila": 58, "mujadila": 58, "the pleading woman": 58,
    "al-hashr": 59, "hashr": 59, "the exile": 59,
    "al-mumtahanah": 60, "mumtahanah": 60, "she that is to be examined": 60,
    "as-saf": 61, "saf": 61, "the ranks": 61,
    "al-jumuah": 62, "jumuah": 62, "friday": 62,
    "al-munafiqun": 63, "munafiqun": 63, "the hypocrites": 63,
    "at-taghabun": 64, "taghabun": 64, "mutual disillusion": 64,
    "at-talaq": 65, "talaq": 65, "divorce": 65,
    "at-tahrim": 66, "tahrim": 66, "the prohibition": 66,
    "al-mulk": 67, "mulk": 67, "sovereignty": 67,
    "al-qalam": 68, "qalam": 68, "the pen": 68,
    "al-haqqah": 69, "haqqah": 69, "the reality": 69,
    "al-maarij": 70, "maarij": 70, "the ascending stairways": 70,
    "nuh": 71, "noah": 71,
    "al-jinn": 72, "jinn": 72,
    "al-muzzammil": 73, "muzzammil": 73, "the enshrouded one": 73,
    "al-muddaththir": 74, "muddaththir": 74, "the cloaked one": 74,
    "al-qiyamah": 75, "qiyamah": 75, "resurrection": 75,
    "al-insan": 76, "insan": 76, "dahr": 76, "man": 76,
    "al-mursalat": 77, "mursalat": 77, "the emissaries": 77,
    "an-naba": 78, "naba": 78, "the tidings": 78,
    "an-naziat": 79, "naziat": 79, "those who drag forth": 79,
    "abasa": 80, "he frowned": 80,
    "at-takwir": 81, "takwir": 81, "the overthrowing": 81,
    "al-infitar": 82, "infitar": 82, "the cleaving": 82,
    "al-mutaffifin": 83, "mutaffifin": 83, "defrauding": 83,
    "al-inshiqaq": 84, "inshiqaq": 84, "the sundering": 84,
    "al-buruj": 85, "buruj": 85, "the mansions of the stars": 85,
    "at-tariq": 86, "tariq": 86, "the nightcomer": 86,
    "al-ala": 87, "ala": 87, "the most high": 87,
    "al-ghashiyah": 88, "ghashiyah": 88, "the overwhelming": 88,
    "al-fajr": 89, "fajr": 89, "the dawn": 89,
    "al-balad": 90, "balad": 90, "the city": 90,
    "ash-shams": 91, "shams": 91, "the sun": 91,
    "al-layl": 92, "layl": 92, "the night": 92,
    "ad-duhaa": 93, "duhaa": 93, "the morning hours": 93,
    "ash-sharh": 94, "sharh": 94, "the relief": 94,
    "at-tin": 95, "tin": 95, "the fig": 95,
    "al-alaq": 96, "alaq": 96, "the clot": 96,
    "al-qadr": 97, "qadr": 97, "power": 97,
    "al-bayyinah": 98, "bayyinah": 98, "clear evidence": 98,
    "az-zalzalah": 99, "zalzalah": 99, "the earthquake": 99,
    "al-adiyat": 100, "adiyat": 100, "the courser": 100,
    "al-qariah": 101, "qariah": 101, "the calamity": 101,
    "at-takathur": 102, "takathur": 102, "rivalry in world increase": 102,
    "al-asr": 103, "asr": 103, "the declining day": 103,
    "al-humazah": 104, "humazah": 104, "the traducer": 104,
    "al-fil": 105, "fil": 105, "the elephant": 105,
    "quraysh": 106,
    "al-maun": 107, "maun": 107, "small kindnesses": 107,
    "al-kawthar": 108, "kawthar": 108, "abundance": 108,
    "al-kafirun": 109, "kafirun": 109, "the disbelievers": 109,
    "an-nasr": 110, "nasr": 110, "divine support": 110,
    "al-masad": 111, "masad": 111, "palm fiber": 111,
    "al-ikhlas": 112, "ikhlas": 112, "sincerity": 112,
    "al-falaq": 113, "falaq": 113, "daybreak": 113,
    "an-nas": 114, "nas": 114, "mankind": 114,
}

PROPHET_NAMES = [
    "Muhammad", "Ibrahim", "Musa", "Isa", "Nuh", "Adam", "Dawud", "Sulayman",
    "Yusuf", "Yakub", "Ishaq", "Ismail", "Harun", "Zakariya", "Yahya",
    "Ayyub", "Yunus", "Ilyas", "Alyasa", "Dhul-Kifl", "Salih", "Hud", "Shuayb", "Lut"
]


def load_quran() -> List[Dict]:
    """Load the complete Quran with English translation."""
    global _quran_data
    if _quran_data is not None:
        return _quran_data
    
    if not os.path.exists(QURAN_ENGLISH_PATH):
        print(f"[QURAN] Warning: {QURAN_ENGLISH_PATH} not found")
        return []
    
    try:
        with open(QURAN_ENGLISH_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if data:
                _quran_data = data
                print(f"[QURAN] Loaded {len(_quran_data)} surahs from Quran")
                return _quran_data
        return []
    except Exception as e:
        print(f"[QURAN] Error loading Quran: {e}")
        return []


def load_quran_arabic() -> List[Dict]:
    """Load the Arabic Quran text."""
    global _quran_arabic
    if _quran_arabic is not None:
        return _quran_arabic
    
    if not os.path.exists(QURAN_ARABIC_PATH):
        return []
    
    try:
        with open(QURAN_ARABIC_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if data:
                _quran_arabic = data
                return _quran_arabic
        return []
    except Exception as e:
        print(f"[QURAN] Error loading Arabic Quran: {e}")
        return []


def get_surah_number(name: str) -> Optional[int]:
    """Convert surah name to number."""
    name_lower = name.lower().strip()
    
    if name_lower.isdigit():
        num = int(name_lower)
        if 1 <= num <= 114:
            return num
        return None
    
    if name_lower in SURAH_NAMES:
        return SURAH_NAMES[name_lower]
    
    for key, num in SURAH_NAMES.items():
        if key in name_lower or name_lower in key:
            return num
    
    return None


def parse_quran_reference(query: str) -> Optional[Tuple[int, int, Optional[int]]]:
    """
    Parse a Quran reference like 'Al-Baqarah 2:255' or 'Surah 2:255' or '2:255'.
    Returns (surah_number, ayah_start, ayah_end) or None.
    """
    query = query.strip()
    
    pattern = r'(?:surah\s+)?(\d+)[:\s]+(\d+)(?:\s*[-–]\s*(\d+))?'
    match = re.search(pattern, query, re.IGNORECASE)
    if match:
        surah = int(match.group(1))
        ayah_start = int(match.group(2))
        ayah_end = int(match.group(3)) if match.group(3) else None
        if 1 <= surah <= 114:
            return (surah, ayah_start, ayah_end)
    
    for name, num in sorted(SURAH_NAMES.items(), key=lambda x: -len(x[0])):
        if name in query.lower():
            ayah_match = re.search(r'(\d+)(?:\s*[-–]\s*(\d+))?', query)
            if ayah_match:
                ayah_start = int(ayah_match.group(1))
                ayah_end = int(ayah_match.group(2)) if ayah_match.group(2) else None
                return (num, ayah_start, ayah_end)
            break
    
    return None


def find_ayah_reference_in_text(text: str) -> Optional[str]:
    """Find an embedded Quran reference in text like 'Explain Al-Baqarah 2:255'."""
    pattern = r'(?:surah\s+)?(\d+)[:\s]+(\d+)(?:\s*[-–]\s*(\d+))?'
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(0)
    
    for name in sorted(SURAH_NAMES.keys(), key=lambda x: -len(x)):
        if name in text.lower():
            ayah_match = re.search(r'(\d+)(?:\s*[-–]\s*(\d+))?', text)
            if ayah_match:
                return f"{name} {ayah_match.group(0)}"
    
    return None


def get_ayah(surah: int, ayah: int) -> Optional[Dict[str, Any]]:
    """Get a specific ayah with Arabic and English."""
    quran = load_quran()
    quran_arabic = load_quran_arabic()
    
    if not quran or surah < 1 or surah > 114:
        return None
    
    surah_data = quran[surah - 1]
    verses = surah_data.get("verses", [])
    
    for v in verses:
        if v.get("id") == ayah:
            arabic_text = ""
            if quran_arabic and surah <= len(quran_arabic):
                arabic_surah = quran_arabic[surah - 1]
                for av in arabic_surah.get("verses", []):
                    if av.get("id") == ayah:
                        arabic_text = av.get("text", "")
                        break
            
            return {
                "surah": surah,
                "surah_name": surah_data.get("name", ""),
                "surah_transliteration": surah_data.get("transliteration", ""),
                "surah_translation": surah_data.get("translation", ""),
                "ayah": ayah,
                "arabic": arabic_text or v.get("text", ""),
                "translation": v.get("translation", ""),
                "reference": f"Surah {surah_data.get('transliteration', '')} ({surah}:{ayah})"
            }
    
    return None


def get_ayah_range(surah: int, start: int, end: int) -> List[Dict[str, Any]]:
    """Get a range of ayahs."""
    results = []
    for ayah_num in range(start, end + 1):
        ayah = get_ayah(surah, ayah_num)
        if ayah:
            results.append(ayah)
    return results


def is_quran_query(query: str) -> bool:
    """Check if this is a Quran-related query."""
    query_lower = query.lower()
    
    from bible_library import is_bible_query
    if is_bible_query(query):
        return False
    
    quran_indicators = [
        "what does the quran say",
        "quran say about",
        "quran says about",
        "in the quran",
        "according to the quran",
        "ayah",
        "ayat",
        "surah",
        "sura",
        "holy quran",
        "quranic",
        "koran",
    ]
    
    for indicator in quran_indicators:
        if indicator in query_lower:
            return True
    
    if find_ayah_reference_in_text(query):
        return True
    
    return False


def extract_topic_from_quran_query(query: str) -> str:
    """Extract the topic from a Quran query like 'what does the quran say about mercy'."""
    query_lower = query.lower()
    
    patterns = [
        r"what does the quran say about (.+)",
        r"quran say about (.+)",
        r"quran says about (.+)",
        r"in the quran about (.+)",
        r"quranic (.+)",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, query_lower)
        if match:
            return match.group(1).strip()
    
    return query


def search_quran_topic(topic: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Search for ayahs about a topic."""
    quran = load_quran()
    if not quran:
        return []
    
    topic_lower = topic.lower()
    keywords = topic_lower.split()
    
    results = []
    
    for surah_data in quran:
        surah_num = surah_data.get("id")
        surah_name = surah_data.get("transliteration", "")
        
        for verse in surah_data.get("verses", []):
            translation = verse.get("translation", "").lower()
            
            if topic_lower in translation or all(kw in translation for kw in keywords):
                results.append({
                    "surah": surah_num,
                    "surah_name": surah_data.get("name", ""),
                    "surah_transliteration": surah_name,
                    "ayah": verse.get("id"),
                    "translation": verse.get("translation", ""),
                    "reference": f"Surah {surah_name} ({surah_num}:{verse.get('id')})"
                })
                
                if len(results) >= limit:
                    return results
    
    return results


def format_ayah_islamic(ayah_data: Dict[str, Any], include_arabic: bool = True) -> str:
    """Format an ayah with Islamic honorifics and style."""
    ref = ayah_data.get("reference", "")
    translation = ayah_data.get("translation", "")
    arabic = ayah_data.get("arabic", "")
    
    text = f"**{ref}**\n\n"
    
    if include_arabic and arabic:
        text += f"*{arabic}*\n\n"
    
    text += f'"{translation}"'
    
    return text


def add_islamic_honorifics(text: str) -> str:
    """Add PBUH and other honorifics to prophet names in text."""
    result = text
    
    result = re.sub(
        r'\b(Muhammad|Prophet Muhammad|the Prophet)\b(?!\s*\()',
        r'\1 ﷺ (peace be upon him)',
        result,
        count=1
    )
    result = re.sub(
        r'\b(Muhammad|Prophet Muhammad|the Prophet)\b(?!\s*[ﷺ(])',
        r'\1 ﷺ',
        result
    )
    
    for prophet in PROPHET_NAMES[1:]:
        result = re.sub(
            rf'\b({prophet})\b(?!\s*\(peace)',
            rf'\1 (peace be upon him)',
            result,
            count=1
        )
        result = re.sub(
            rf'\b({prophet})\b(?!\s*\(peace)',
            rf'\1 (AS)',
            result
        )
    
    return result


def get_total_ayahs() -> int:
    """Get total number of ayahs in the Quran."""
    quran = load_quran()
    if not quran:
        return 0
    return sum(len(s.get("verses", [])) for s in quran)
