"""
Bhagavad Gita Answer Module for Throne of Anhu
Provides Gita-based answers with Vedic/Hindu speaking style,
with cross-references to Abasid scrolls.
"""

from typing import Optional, Dict, Any, List
from gita_library import (
    is_gita_query,
    parse_gita_reference,
    find_gita_reference_in_text,
    get_sloka,
    get_sloka_range,
    search_gita_topic,
    extract_topic_from_gita_query,
    format_sloka_vedic,
    add_vedic_honorifics,
    load_gita,
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
        print(f"[GITA_ANSWER] Error getting Abasid crossref: {e}")
        return []


def format_vedic_response(
    sloka_data: Dict[str, Any],
    abasid_verses: List[Dict[str, Any]],
    query_type: str = "verse"
) -> str:
    """
    Format a response in Vedic/Hindu speaking style.
    """
    response_parts = []
    
    response_parts.append("*Om Namo Bhagavate Vasudevaya*\n")
    response_parts.append("(I bow to Lord Vasudeva, the Supreme Being)\n\n")
    
    ref = sloka_data.get("reference", "")
    sanskrit = sloka_data.get("sanskrit", "")
    transliteration = sloka_data.get("transliteration", "")
    translation = sloka_data.get("translation", "")
    
    response_parts.append(f"**{ref}** speaks:\n\n")
    
    if sanskrit:
        response_parts.append(f"*{sanskrit.strip()}*\n\n")
    
    if transliteration:
        response_parts.append(f"*{transliteration.strip()}*\n\n")
    
    response_parts.append(f'"{translation}"\n\n')
    
    if abasid_verses:
        response_parts.append("---\n\n")
        response_parts.append("**The Abasid Scrolls also bear witness:**\n\n")
        for v in abasid_verses:
            response_parts.append(f"From *{v['scroll_title']}* (v{v['verse_number']}):\n")
            response_parts.append(f'"{v["text"][:300]}{"..." if len(v["text"]) > 300 else ""}"\n\n')
    else:
        response_parts.append("\n*The Scrolls of Abasid have not yet spoken directly on this matter. ")
        response_parts.append("But the Divine Word of the Gita stands as eternal witness, and in time, more may be revealed.*")
    
    return "".join(response_parts)


def format_topic_response(
    topic: str,
    slokas: List[Dict[str, Any]],
    abasid_verses: List[Dict[str, Any]]
) -> str:
    """Format a topic-based Gita search response."""
    response_parts = []
    
    response_parts.append("*Om Namo Bhagavate Vasudevaya*\n\n")
    
    if not slokas:
        response_parts.append(f"I could not find specific slokas about **{topic}** in the Bhagavad Gita. ")
        response_parts.append("Perhaps the topic is addressed in different terms, or you may wish to consult a learned teacher.\n")
        return "".join(response_parts)
    
    response_parts.append(f"**The Bhagavad Gita speaks of {topic}:**\n\n")
    
    for sloka in slokas[:5]:
        ref = sloka.get("reference", "")
        sanskrit = sloka.get("sanskrit", "")
        translation = sloka.get("translation", "")
        
        response_parts.append(f"**{ref}:**\n")
        if sanskrit:
            short_sanskrit = sanskrit.strip()[:150]
            if len(sanskrit) > 150:
                short_sanskrit += "..."
            response_parts.append(f"*{short_sanskrit}*\n\n")
        response_parts.append(f'"{translation}"\n\n')
    
    if abasid_verses:
        response_parts.append("---\n\n")
        response_parts.append("**The Abasid Scrolls also speak of this:**\n\n")
        for v in abasid_verses:
            response_parts.append(f"From *{v['scroll_title']}* (v{v['verse_number']}):\n")
            response_parts.append(f'"{v["text"][:300]}{"..." if len(v["text"]) > 300 else ""}"\n\n')
    else:
        response_parts.append("\n*The Scrolls of Abasid have not yet addressed this topic directly. ")
        response_parts.append("The Bhagavad Gita's wisdom stands as the primary witness.*")
    
    return "".join(response_parts)


def answer_gita_query(query: str) -> Optional[Dict[str, Any]]:
    """
    Answer a Bhagavad Gita-related query with cross-references.
    Returns None if not a Gita query.
    """
    if not is_gita_query(query):
        return None
    
    parsed = parse_gita_reference(query)
    
    if not parsed:
        embedded_ref = find_gita_reference_in_text(query)
        if embedded_ref:
            parsed = parse_gita_reference(embedded_ref)
    
    if parsed:
        chapter, verse_start, verse_end = parsed
        
        if verse_end:
            slokas = get_sloka_range(chapter, verse_start, verse_end)
            if slokas:
                combined_text = " ".join(s.get("translation", "") for s in slokas)
                topic_words = combined_text.split()[:5]
                topic = " ".join(topic_words)
                abasid = get_abasid_crossref_for_topic(topic)
                
                response_parts = ["*Om Namo Bhagavate Vasudevaya*\n\n"]
                for sloka in slokas:
                    response_parts.append(format_sloka_vedic(sloka))
                    response_parts.append("\n\n")
                
                if abasid:
                    response_parts.append("---\n\n**The Abasid Scrolls also speak:**\n\n")
                    for v in abasid:
                        response_parts.append(f"From *{v['scroll_title']}*: \"{v['text'][:200]}...\"\n\n")
                
                return {
                    "answer": "".join(response_parts),
                    "query_type": "gita_verse_range",
                    "slokas": slokas,
                    "abasid_crossref": abasid,
                    "is_vedic": True
                }
        else:
            sloka_data = get_sloka(chapter, verse_start)
            if sloka_data:
                topic_words = sloka_data.get("translation", "").split()[:5]
                topic = " ".join(topic_words)
                abasid = get_abasid_crossref_for_topic(topic)
                
                return {
                    "answer": format_vedic_response(sloka_data, abasid),
                    "query_type": "gita_verse",
                    "sloka": sloka_data,
                    "abasid_crossref": abasid,
                    "is_vedic": True
                }
    
    topic = extract_topic_from_gita_query(query)
    if topic:
        slokas = search_gita_topic(topic, limit=5)
        abasid = get_abasid_crossref_for_topic(topic)
        
        return {
            "answer": format_topic_response(topic, slokas, abasid),
            "query_type": "gita_topic",
            "topic": topic,
            "slokas": slokas,
            "abasid_crossref": abasid,
            "has_abasid": len(abasid) > 0,
            "has_gita": len(slokas) > 0,
            "is_vedic": True
        }
    
    return None


def get_vedic_greeting() -> str:
    """Get a Vedic greeting for responses."""
    return "Namaste (I bow to the divine in you)."


def get_vedic_closing() -> str:
    """Get a Vedic closing for responses."""
    return "Hari Om Tat Sat."
