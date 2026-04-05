"""
Ancient Prayers Library for Throne of Anhu
Provides prayer lookup, search, and retrieval for sacred prayers across traditions.
"""

import json
import os
from typing import Optional, List, Dict, Any

PRAYERS_PATH = "sources/ancient_prayers.json"

_prayers_data: Optional[Dict] = None


def _load_prayers() -> Dict:
    """Load the ancient prayers JSON data."""
    global _prayers_data
    if _prayers_data is not None:
        return _prayers_data
    
    try:
        if os.path.exists(PRAYERS_PATH):
            with open(PRAYERS_PATH, 'r', encoding='utf-8') as f:
                _prayers_data = json.load(f)
                print(f"[ANCIENT PRAYERS] Loaded {len(_prayers_data.get('prayers', []))} prayers from sacred traditions")
                return _prayers_data
    except Exception as e:
        print(f"[ANCIENT PRAYERS] Error loading: {e}")
    
    _prayers_data = {"metadata": {}, "prayers": []}
    return _prayers_data


def get_all_prayers() -> List[Dict]:
    """Get all prayers from the collection."""
    data = _load_prayers()
    return data.get("prayers", [])


def get_prayer_by_id(prayer_id: str) -> Optional[Dict]:
    """Get a specific prayer by its ID."""
    prayers = get_all_prayers()
    for prayer in prayers:
        if prayer.get("id") == prayer_id:
            return prayer
    return None


def get_prayer_by_title(title: str) -> Optional[Dict]:
    """Get a prayer by its title (case-insensitive partial match)."""
    prayers = get_all_prayers()
    title_lower = title.lower()
    for prayer in prayers:
        if title_lower in prayer.get("title", "").lower():
            return prayer
    return None


def get_prayers_by_tradition(tradition: str) -> List[Dict]:
    """Get all prayers from a specific tradition."""
    prayers = get_all_prayers()
    tradition_lower = tradition.lower()
    return [p for p in prayers if tradition_lower in p.get("tradition", "").lower()]


def search_prayers(query: str) -> List[Dict]:
    """
    Search prayers by keyword in title, tradition, origin, taught_by, meaning, or content.
    Returns matching prayers sorted by relevance.
    """
    prayers = get_all_prayers()
    query_lower = query.lower()
    results = []
    
    for prayer in prayers:
        score = 0
        
        if query_lower in prayer.get("title", "").lower():
            score += 10
        if query_lower in prayer.get("tradition", "").lower():
            score += 5
        if query_lower in prayer.get("taught_by", "").lower():
            score += 5
        if query_lower in prayer.get("origin", "").lower():
            score += 3
        if query_lower in prayer.get("meaning", "").lower():
            score += 2
        if query_lower in prayer.get("spiritual_significance", "").lower():
            score += 2
        
        languages = prayer.get("languages", {})
        for lang_text in languages.values():
            if isinstance(lang_text, str) and query_lower in lang_text.lower():
                score += 3
                break
        
        if score > 0:
            results.append((score, prayer))
    
    results.sort(key=lambda x: x[0], reverse=True)
    return [r[1] for r in results]


def get_lords_prayer(language: str = "english") -> Optional[str]:
    """Get the Lord's Prayer in the specified language."""
    prayer = get_prayer_by_id("PRAYER-001")
    if prayer:
        languages = prayer.get("languages", {})
        lang_key = language.lower()
        if lang_key in languages:
            return languages[lang_key]
        if "shona" in lang_key or lang_key == "chishona":
            return languages.get("shona")
        if "aramaic" in lang_key:
            return languages.get("aramaic_transliteration")
    return None


def get_papyrus_prayers() -> List[Dict]:
    """Get all prayers from the Papyrus of Ani."""
    prayers = get_all_prayers()
    return [p for p in prayers if "papyrus" in p.get("origin", "").lower() or "kemetic" in p.get("tradition", "").lower()]


def get_african_prayers() -> List[Dict]:
    """Get African traditional prayers including Shona and Masowe traditions."""
    prayers = get_all_prayers()
    african_keywords = ["shona", "masowe", "african", "zimbabwe", "bantu"]
    return [p for p in prayers if any(kw in p.get("tradition", "").lower() or kw in p.get("origin", "").lower() for kw in african_keywords)]


def get_prayer_with_shona(prayer_id: str = None, title: str = None) -> Optional[Dict]:
    """Get a prayer that includes Shona translation."""
    prayer = None
    if prayer_id:
        prayer = get_prayer_by_id(prayer_id)
    elif title:
        prayer = get_prayer_by_title(title)
    
    if prayer and "shona" in prayer.get("languages", {}):
        return prayer
    return None


def format_prayer_response(prayer: Dict, include_all_languages: bool = False) -> str:
    """Format a prayer for display in chat responses."""
    lines = []
    lines.append(f"**{prayer.get('title', 'Unknown Prayer')}**")
    lines.append(f"*Tradition: {prayer.get('tradition', 'Unknown')}*")
    lines.append(f"*Origin: {prayer.get('origin', 'Unknown')}*")
    lines.append(f"*Taught by: {prayer.get('taught_by', 'Unknown')}*")
    lines.append("")
    
    languages = prayer.get("languages", {})
    if include_all_languages:
        for lang, text in languages.items():
            if isinstance(text, str):
                lines.append(f"**{lang.title()}:**")
                lines.append(text)
                lines.append("")
    else:
        if "english" in languages:
            lines.append(languages["english"])
            lines.append("")
        if "shona" in languages:
            lines.append("**Shona:**")
            lines.append(languages["shona"])
            lines.append("")
    
    if prayer.get("meaning"):
        lines.append(f"**Meaning:** {prayer.get('meaning')}")
        lines.append("")
    
    if prayer.get("spiritual_significance"):
        lines.append(f"**Spiritual Significance:** {prayer.get('spiritual_significance')}")
    
    return "\n".join(lines)


def get_prayers_summary() -> str:
    """Get a summary of all available prayers grouped by tradition."""
    prayers = get_all_prayers()
    traditions = {}
    
    for prayer in prayers:
        tradition = prayer.get("tradition", "Unknown")
        if tradition not in traditions:
            traditions[tradition] = []
        traditions[tradition].append(prayer.get("title", "Untitled"))
    
    lines = ["**Sacred Prayers Available:**\n"]
    for tradition, titles in sorted(traditions.items()):
        lines.append(f"**{tradition}:**")
        for title in titles:
            lines.append(f"  - {title}")
        lines.append("")
    
    return "\n".join(lines)


PRAYER_KEYWORDS = {
    "lord's prayer": "PRAYER-001",
    "our father": "PRAYER-001",
    "baba wedu": "PRAYER-001",
    "munamato wa baba": "PRAYER-001",
    "pater noster": "PRAYER-001",
    "shema": "PRAYER-002",
    "shema yisrael": "PRAYER-002",
    "al fatiha": "PRAYER-003",
    "fatiha": "PRAYER-003",
    "opening": "PRAYER-003",
    "hymn to ra": "PRAYER-004",
    "sunrise hymn": "PRAYER-004",
    "negative confession": "PRAYER-005",
    "42 confessions": "PRAYER-005",
    "declaration of innocence": "PRAYER-005",
    "heart scarab": "PRAYER-006",
    "heart spell": "PRAYER-006",
    "opening of the mouth": "PRAYER-007",
    "hymn to osiris": "PRAYER-008",
    "aaronic blessing": "PRAYER-010",
    "priestly blessing": "PRAYER-010",
    "jabez": "PRAYER-011",
    "solomon wisdom": "PRAYER-012",
    "daniel": "PRAYER-013",
    "psalm 23": "PRAYER-014",
    "shepherd psalm": "PRAYER-014",
    "ayat al kursi": "PRAYER-015",
    "throne verse": "PRAYER-015",
    "jesus prayer": "PRAYER-016",
    "prayer of the heart": "PRAYER-016",
    "gayatri": "PRAYER-019",
    "mahamrityunjaya": "PRAYER-020",
    "death conquering": "PRAYER-020",
    "three refuges": "PRAYER-021",
    "metta": "PRAYER-022",
    "loving kindness": "PRAYER-022",
    "kaddish": "PRAYER-024",
    "al ikhlas": "PRAYER-025",
    "an nas": "PRAYER-026",
    "st francis": "PRAYER-027",
    "serenity prayer": "PRAYER-028",
    "baba johani": "PRAYER-029",
    "johane masowe": "PRAYER-029",
    "coming forth by day": "PRAYER-030",
    "golden falcon": "PRAYER-031",
    "ba soul": "PRAYER-032",
    "fields of hetep": "PRAYER-033",
    "second death": "PRAYER-034",
    "modeh ani": "PRAYER-035",
    "adon olam": "PRAYER-036",
    "istikhara": "PRAYER-037",
    "parents prayer": "PRAYER-038",
    "manasseh": "PRAYER-039",
    "om mani padme hum": "PRAYER-040",
    "amitabha": "PRAYER-041",
    "namo amituofo": "PRAYER-041",
    "kutenda": "PRAYER-042",
    "thanksgiving shona": "PRAYER-042",
}


def lookup_prayer_by_keyword(keyword: str) -> Optional[Dict]:
    """Look up a prayer by common keyword."""
    keyword_lower = keyword.lower()
    for kw, prayer_id in PRAYER_KEYWORDS.items():
        if kw in keyword_lower:
            return get_prayer_by_id(prayer_id)
    return None


if __name__ == "__main__":
    prayers = get_all_prayers()
    print(f"Total prayers: {len(prayers)}")
    
    lords_prayer = get_lords_prayer("shona")
    if lords_prayer:
        print("\nLord's Prayer (Shona):")
        print(lords_prayer)
    
    papyrus = get_papyrus_prayers()
    print(f"\nPapyrus of Ani prayers: {len(papyrus)}")
    for p in papyrus[:3]:
        print(f"  - {p.get('title')}")
