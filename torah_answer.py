"""
Torah Answer Engine for Throne of Anhu
Formats responses with Hebrew speaking style and Abasid cross-references.
"""

from typing import Optional, Dict, List
from torah_library import (
    detect_torah_query,
    parse_torah_reference,
    get_verse,
    search_torah_topic,
    get_verse_display_text,
    find_abasid_crossreferences,
    load_torah
)


def answer_torah_query(query: str) -> Optional[str]:
    """Generate a Torah-style answer for the query."""
    if not detect_torah_query(query):
        return None
    
    load_torah()
    
    book, chapter, verse_num = parse_torah_reference(query)
    
    if book and chapter and verse_num:
        verse = get_verse(book, chapter, verse_num)
        if verse:
            return format_torah_response([verse], query)
    
    if book and chapter:
        verses = search_by_chapter(book, chapter)
        if verses:
            return format_torah_response(verses[:5], query)
    
    topic_keywords = extract_topic_keywords(query)
    if topic_keywords:
        verses = search_torah_topic(topic_keywords, max_results=5)
        if verses:
            return format_torah_response(verses, query)
    
    return None


def search_by_chapter(book: int, chapter: int) -> List[Dict]:
    """Get verses from a specific chapter."""
    from torah_library import get_all_verses
    all_verses = get_all_verses()
    return [v for v in all_verses 
            if v.get("chapter") == chapter 
            and any(b.get("book") == book for b in load_torah().get("books", [])
                   if b.get("name_english") == v.get("book_english"))]


def extract_topic_keywords(query: str) -> str:
    """Extract meaningful topic keywords from the query."""
    import re
    stop_words = {"what", "does", "the", "torah", "say", "about", "tell", "me", "explain",
                  "hebrew", "bible", "scripture", "mean", "meaning", "of", "in", "a", "an",
                  "is", "are", "was", "were", "how", "why", "where", "when", "who", "can",
                  "you", "please", "give", "show", "according", "to", "from"}
    
    clean_query = re.sub(r'[^\w\s]', '', query.lower())
    words = clean_query.split()
    keywords = [w for w in words if w not in stop_words and len(w) > 2]
    return " ".join(keywords)


def format_torah_response(verses: List[Dict], query: str) -> str:
    """Format Torah verses with Hebrew greeting and Abasid cross-references."""
    lines = []
    
    lines.append("**Baruch HaShem!** (בָּרוּךְ הַשֵּׁם - Blessed be The Name!)")
    lines.append("")
    lines.append("*The Torah, the teaching of HaShem, speaks unto thee...*")
    lines.append("")
    
    for verse in verses:
        lines.append(get_verse_display_text(verse))
        lines.append("")
    
    topic = extract_topic_keywords(query)
    if topic:
        crossrefs = find_abasid_crossreferences(topic, max_results=2)
        if crossrefs:
            lines.append("---")
            lines.append("**The Abasid Scrolls witness:**")
            lines.append("")
            for ref in crossrefs:
                scroll_title = ref.get("scroll_title", "Abasid")
                text = ref.get("text", "")[:200]
                lines.append(f"*{scroll_title}*: {text}...")
                lines.append("")
        else:
            lines.append("---")
            lines.append("*The Abasid scrolls have not yet spoken directly on this matter, but the Torah witnesses the same God who spoke to Baba Johani in Africa.*")
            lines.append("")
    
    lines.append("---")
    lines.append("*Shalom u'vracha (שָׁלוֹם וּבְרָכָה) — Peace and blessing be upon you.*")
    
    return "\n".join(lines)
