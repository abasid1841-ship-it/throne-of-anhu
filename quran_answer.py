"""
Quran Answer Module for Throne of Anhu
Provides Quran-based answers with Islamic honorifics and speaking style,
with cross-references to Abasid scrolls.
"""

from typing import Optional, Dict, Any, List
from quran_library import (
    is_quran_query,
    parse_quran_reference,
    find_ayah_reference_in_text,
    get_ayah,
    get_ayah_range,
    search_quran_topic,
    extract_topic_from_quran_query,
    format_ayah_islamic,
    add_islamic_honorifics,
    load_quran,
)


def get_abasid_crossref_for_topic(topic: str, limit: int = 3) -> List[Dict[str, Any]]:
    """Find Abasid scroll verses related to a topic."""
    try:
        from scroll_library import get_all_scrolls
        library = get_all_scrolls()
        
        results = []
        topic_lower = topic.lower()
        keywords = topic_lower.split()
        
        for scroll in library:
            verses = scroll.get("verses", [])
            for i, verse in enumerate(verses):
                if isinstance(verse, str):
                    verse_text = verse.lower()
                    verse_number = i + 1
                    original_text = verse
                elif isinstance(verse, dict):
                    verse_text = verse.get("text", "").lower()
                    verse_number = verse.get("verse_number", i + 1)
                    original_text = verse.get("text", "")
                else:
                    continue
                
                if topic_lower in verse_text or all(kw in verse_text for kw in keywords):
                    results.append({
                        "scroll_title": scroll.get("book_title", "Unknown Scroll"),
                        "verse_number": verse_number,
                        "text": original_text
                    })
                    if len(results) >= limit:
                        return results
        
        return results
    except Exception as e:
        print(f"[QURAN_ANSWER] Error getting Abasid crossref: {e}")
        return []


def format_islamic_response(
    ayah_data: Dict[str, Any],
    abasid_verses: List[Dict[str, Any]],
    query_type: str = "verse"
) -> str:
    """
    Format a response in Islamic speaking style.
    """
    response_parts = []
    
    response_parts.append("*Bismillah ir-Rahman ir-Raheem*\n")
    response_parts.append("(In the name of Allah, the Most Gracious, the Most Merciful)\n\n")
    
    ref = ayah_data.get("reference", "")
    arabic = ayah_data.get("arabic", "")
    translation = ayah_data.get("translation", "")
    
    response_parts.append(f"**{ref}** says:\n\n")
    
    if arabic:
        response_parts.append(f"*{arabic}*\n\n")
    
    response_parts.append(f'"{translation}"\n\n')
    
    if abasid_verses:
        response_parts.append("---\n\n")
        response_parts.append("**The Abasid Scrolls also bear witness:**\n\n")
        for v in abasid_verses:
            response_parts.append(f"From *{v['scroll_title']}* (v{v['verse_number']}):\n")
            response_parts.append(f'"{v["text"][:300]}{"..." if len(v["text"]) > 300 else ""}"\n\n')
    else:
        response_parts.append("\n*The Scrolls of Abasid have not yet spoken directly on this matter. ")
        response_parts.append("But the Word of Allah stands as witness, and in time, more may be revealed.*")
    
    return "".join(response_parts)


def format_topic_response(
    topic: str,
    ayahs: List[Dict[str, Any]],
    abasid_verses: List[Dict[str, Any]]
) -> str:
    """Format a topic-based Quran search response."""
    response_parts = []
    
    response_parts.append("*Bismillah ir-Rahman ir-Raheem*\n\n")
    
    if not ayahs:
        response_parts.append(f"I could not find specific ayahs about **{topic}** in the Holy Quran. ")
        response_parts.append("Perhaps the topic is addressed in different terms, or you may wish to consult a scholar.\n")
        return "".join(response_parts)
    
    response_parts.append(f"**The Holy Quran speaks of {topic}:**\n\n")
    
    for ayah in ayahs[:5]:
        ref = ayah.get("reference", "")
        translation = ayah.get("translation", "")
        response_parts.append(f"**{ref}:**\n")
        response_parts.append(f'"{translation}"\n\n')
    
    if abasid_verses:
        response_parts.append("---\n\n")
        response_parts.append("**The Abasid Scrolls also speak of this:**\n\n")
        for v in abasid_verses:
            response_parts.append(f"From *{v['scroll_title']}* (v{v['verse_number']}):\n")
            response_parts.append(f'"{v["text"][:300]}{"..." if len(v["text"]) > 300 else ""}"\n\n')
    else:
        response_parts.append("\n*The Scrolls of Abasid have not yet addressed this topic directly. ")
        response_parts.append("The Holy Quran's wisdom stands as the primary witness.*")
    
    return "".join(response_parts)


def answer_quran_query(query: str) -> Optional[Dict[str, Any]]:
    """
    Answer a Quran-related query with cross-references.
    Returns None if not a Quran query.
    """
    if not is_quran_query(query):
        return None
    
    parsed = parse_quran_reference(query)
    
    if not parsed:
        embedded_ref = find_ayah_reference_in_text(query)
        if embedded_ref:
            parsed = parse_quran_reference(embedded_ref)
    
    if parsed:
        surah, ayah_start, ayah_end = parsed
        
        if ayah_end:
            ayahs = get_ayah_range(surah, ayah_start, ayah_end)
            if ayahs:
                combined_text = " ".join(a.get("translation", "") for a in ayahs)
                topic_words = combined_text.split()[:5]
                topic = " ".join(topic_words)
                abasid = get_abasid_crossref_for_topic(topic)
                
                response_parts = ["*Bismillah ir-Rahman ir-Raheem*\n\n"]
                for ayah in ayahs:
                    response_parts.append(format_ayah_islamic(ayah))
                    response_parts.append("\n\n")
                
                if abasid:
                    response_parts.append("---\n\n**The Abasid Scrolls also speak:**\n\n")
                    for v in abasid:
                        response_parts.append(f"From *{v['scroll_title']}*: \"{v['text'][:200]}...\"\n\n")
                
                return {
                    "answer": "".join(response_parts),
                    "query_type": "quran_verse_range",
                    "ayahs": ayahs,
                    "abasid_crossref": abasid,
                    "is_islamic": True
                }
        else:
            ayah_data = get_ayah(surah, ayah_start)
            if ayah_data:
                topic_words = ayah_data.get("translation", "").split()[:5]
                topic = " ".join(topic_words)
                abasid = get_abasid_crossref_for_topic(topic)
                
                return {
                    "answer": format_islamic_response(ayah_data, abasid),
                    "query_type": "quran_verse",
                    "ayah": ayah_data,
                    "abasid_crossref": abasid,
                    "is_islamic": True
                }
    
    topic = extract_topic_from_quran_query(query)
    if topic:
        ayahs = search_quran_topic(topic, limit=5)
        abasid = get_abasid_crossref_for_topic(topic)
        
        return {
            "answer": format_topic_response(topic, ayahs, abasid),
            "query_type": "quran_topic",
            "topic": topic,
            "ayahs": ayahs,
            "abasid_crossref": abasid,
            "has_abasid": len(abasid) > 0,
            "has_quran": len(ayahs) > 0,
            "is_islamic": True
        }
    
    return None


def get_islamic_greeting() -> str:
    """Get an Islamic greeting for responses."""
    return "As-salamu alaykum (Peace be upon you)."


def get_islamic_closing() -> str:
    """Get an Islamic closing for responses."""
    return "Wa Alaikum Assalam wa Rahmatullahi wa Barakatuh."
