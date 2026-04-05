"""
Bible Answer Handler - Answers Bible questions with Abasid cross-references.
"""
import os
from typing import Dict, List, Optional, Any
from bible_library import (
    is_bible_query, 
    parse_bible_reference, 
    get_verses, 
    search_bible_topic,
    extract_topic_from_bible_query,
    find_verse_reference_in_text
)
from scroll_library import get_all_scrolls

def search_abasid_scrolls_for_topic(topic: str, limit: int = 3) -> List[Dict[str, str]]:
    """
    Search Abasid scrolls for verses related to a topic.
    Returns list of {scroll_title, verse} dicts.
    """
    try:
        all_scrolls = get_all_scrolls()
        
        results = []
        topic_words = topic.lower().split()
        
        for scroll in all_scrolls:
            scroll_title = scroll.get("book_title", scroll.get("scroll_id", "Unknown Scroll"))
            verses = scroll.get("verses", [])
            
            for verse in verses:
                if isinstance(verse, str):
                    verse_lower = verse.lower()
                    if any(word in verse_lower for word in topic_words):
                        results.append({
                            "scroll_title": scroll_title,
                            "verse": verse
                        })
                        if len(results) >= limit:
                            return results
        
        return results
    except Exception as e:
        print(f"[BIBLE] Error searching Abasid scrolls: {e}")
        return []

def format_bible_answer(
    bible_verses: List[Dict[str, str]], 
    abasid_verses: List[Dict[str, str]],
    is_verse_lookup: bool = False,
    topic: str = ""
) -> Dict[str, Any]:
    """
    Format the answer combining Bible verses with Abasid cross-references.
    """
    response_parts = []
    witnesses = []
    
    if bible_verses:
        if is_verse_lookup:
            for bv in bible_verses:
                response_parts.append(f"**{bv['reference']}** says:\n\n\"{bv['text']}\"")
                witnesses.append({
                    "source": f"KJV Bible - {bv['reference']}",
                    "text": bv['text']
                })
        else:
            response_parts.append(f"The Bible speaks of **{topic}** in these verses:\n")
            for bv in bible_verses[:3]:
                response_parts.append(f"**{bv['reference']}**: \"{bv['text']}\"")
                witnesses.append({
                    "source": f"KJV Bible - {bv['reference']}",
                    "text": bv['text']
                })
    
    if abasid_verses:
        response_parts.append("\n\n**The Abasid Scrolls also speak of this:**\n")
        for av in abasid_verses:
            short_verse = av['verse'][:200] + "..." if len(av['verse']) > 200 else av['verse']
            response_parts.append(f"From *{av['scroll_title']}*: \"{short_verse}\"")
            witnesses.append({
                "source": av['scroll_title'],
                "text": av['verse']
            })
    else:
        if bible_verses:
            response_parts.append("\n\n*Abasid has not yet spoken directly on this matter. Perhaps in time, more will be revealed. But the Scripture stands as witness.*")
    
    return {
        "answer": "\n\n".join(response_parts),
        "witnesses": witnesses,
        "has_abasid": len(abasid_verses) > 0,
        "has_bible": len(bible_verses) > 0
    }

def answer_bible_query(query: str) -> Optional[Dict[str, Any]]:
    """
    Answer a Bible-related query with cross-references.
    Returns None if not a Bible query.
    """
    if not is_bible_query(query):
        return None
    
    parsed = parse_bible_reference(query)
    
    if not parsed:
        embedded_ref = find_verse_reference_in_text(query)
        if embedded_ref:
            parsed = parse_bible_reference(embedded_ref)
    
    if parsed:
        book, chapter, verse_start, verse_end = parsed
        if verse_end:
            ref_str = f"{book} {chapter}:{verse_start}-{verse_end}"
        else:
            ref_str = f"{book} {chapter}:{verse_start}"
        
        bible_verses = get_verses(ref_str)
        
        if not bible_verses:
            return {
                "answer": f"I could not find the verse **{ref_str}** in the KJV Bible. Please check the reference and try again.",
                "witnesses": [],
                "has_abasid": False,
                "has_bible": False
            }
        
        topics = []
        for bv in bible_verses:
            words = bv['text'].lower().split()
            for word in words:
                if len(word) > 5 and word.isalpha():
                    topics.append(word)
        
        topic_str = " ".join(topics[:3]) if topics else ""
        abasid_verses = search_abasid_scrolls_for_topic(topic_str, limit=2) if topic_str else []
        
        return format_bible_answer(bible_verses, abasid_verses, is_verse_lookup=True)
    
    topic = extract_topic_from_bible_query(query)
    
    if topic:
        bible_verses = search_bible_topic(topic, limit=5)
        abasid_verses = search_abasid_scrolls_for_topic(topic, limit=3)
        
        if not bible_verses:
            if abasid_verses:
                response_parts = [f"The Bible does not speak directly of **{topic}** in those exact words, but the Abasid Scrolls say:\n"]
                witnesses = []
                for av in abasid_verses:
                    short_verse = av['verse'][:200] + "..." if len(av['verse']) > 200 else av['verse']
                    response_parts.append(f"From *{av['scroll_title']}*: \"{short_verse}\"")
                    witnesses.append({
                        "source": av['scroll_title'],
                        "text": av['verse']
                    })
                return {
                    "answer": "\n\n".join(response_parts),
                    "witnesses": witnesses,
                    "has_abasid": True,
                    "has_bible": False
                }
            else:
                return {
                    "answer": f"Neither the Bible nor the Abasid Scrolls speak directly of **{topic}** in those exact words. Perhaps you could rephrase your question, or ask about a related matter.",
                    "witnesses": [],
                    "has_abasid": False,
                    "has_bible": False
                }
        
        return format_bible_answer(bible_verses, abasid_verses, is_verse_lookup=False, topic=topic)
    
    return None

def get_bible_verse_for_throne(reference: str) -> Optional[str]:
    """
    Simple helper to get a Bible verse text for the Throne to quote.
    """
    verses = get_verses(reference)
    if verses:
        return verses[0]['text']
    return None
