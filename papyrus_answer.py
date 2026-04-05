"""
Papyrus of Ani Answer Engine for Throne of Anhu
Formats responses about the Egyptian Book of the Dead with ancient Egyptian speaking style.
Cross-references with Abasid 1841 scrolls.
"""

from typing import Optional, List, Dict, Any, Tuple
import papyrus_library
from papyrus_library import (
    get_spell_by_chapter,
    search_papyrus_topic,
    parse_papyrus_reference,
    detect_papyrus_query,
    get_spell_display_text,
    find_abasid_crossreferences,
)


def _get_abasid_crossref(crossref_terms: List[str]) -> str:
    """Search Abasid scrolls for related content."""
    if not crossref_terms:
        return ""
    
    try:
        from scroll_library import find_relevant_scrolls
        from source_library import search_sources
        
        for term in crossref_terms[:3]:
            sources = search_sources(term, max_results=2)
            if sources:
                crossref_text = "\n\n**The Scrolls of Abasid 1841 speak thus:**\n"
                for s in sources[:2]:
                    crossref_text += f"\n*{s.ref}*: \"{s.text[:200]}...\"\n"
                return crossref_text
    except Exception:
        pass
    
    return "\n\n*The Abasid scrolls await to reveal further connections between the wisdom of ancient Kemet and the teachings of today.*"


def format_papyrus_response(
    query: str,
    spells: List[Dict],
    is_reference_lookup: bool = False
) -> str:
    """
    Format a response about the Papyrus of Ani in ancient Egyptian style.
    """
    if not spells:
        return _format_no_results(query)
    
    response_parts = []
    
    opening = "**Dua Netjer en ankh!** (Praise to the God of life!)\n\n"
    opening += "*The ancient scrolls of Kemet speak unto thee...*\n\n"
    response_parts.append(opening)
    
    for i, spell in enumerate(spells[:3]):
        chapter = spell.get("chapter", "?")
        title = spell.get("title", "Unknown")
        section = spell.get("section", "")
        text = spell.get("text", "")
        
        spell_block = f"**Chapter {chapter}: {title}**"
        if section:
            spell_block += f" *[{section}]*"
        spell_block += "\n\n"
        
        spell_block += f"> {text}\n"
        
        response_parts.append(spell_block)
    
    crossref_terms = []
    for spell in spells[:2]:
        crossref_terms.extend(find_abasid_crossreferences(spell))
    
    if crossref_terms:
        crossref = _get_abasid_crossref(crossref_terms)
        response_parts.append(crossref)
    
    closing = "\n\n---\n*As it was written in the House of Life, so it is spoken in the Throne of Anhu. The wisdom of the Two Lands endures.*\n"
    closing += "*Ankh, Udja, Seneb* (Life, Prosperity, Health)"
    response_parts.append(closing)
    
    return "\n".join(response_parts)


def _format_no_results(query: str) -> str:
    """Format response when no matching spells are found."""
    return f"""**Dua Netjer en ankh!** (Praise to the God of life!)

*The Papyrus of Ani contains wisdom for the journey through the Duat (underworld), yet your question "{query}" seeks knowledge not directly inscribed in these ancient spells.*

The Book of Coming Forth by Day (Per Em Hru) speaks of:
- **The Weighing of the Heart** (Chapter 125) - judgment before Osiris
- **Transformation Spells** (Chapters 76-88) - becoming falcon, phoenix, serpent
- **Hymns to Ra and Osiris** (Chapters 15, 185) - praise to the great gods
- **Protection Spells** - against snakes, decay, and the second death

*Perhaps the wisdom you seek dwells in another chamber of the great library...*

*Ankh, Udja, Seneb* (Life, Prosperity, Health)"""


def answer_papyrus_query(query: str) -> Optional[str]:
    """
    Main entry point for answering Papyrus of Ani queries.
    Returns formatted response or None if not a Papyrus query.
    """
    if not detect_papyrus_query(query):
        return None
    
    ref = parse_papyrus_reference(query)
    if ref:
        chapter, _ = ref
        spells = get_spell_by_chapter(chapter)
        if spells:
            return format_papyrus_response(query, spells, is_reference_lookup=True)
    
    topic_results = search_papyrus_topic(query, max_results=3)
    if topic_results:
        return format_papyrus_response(query, topic_results, is_reference_lookup=False)
    
    all_topic_words = query.lower().split()
    for word in all_topic_words:
        if len(word) > 4:
            results = search_papyrus_topic(word, max_results=2)
            if results:
                return format_papyrus_response(query, results, is_reference_lookup=False)
    
    return _format_no_results(query)


def get_papyrus_summary() -> str:
    """Get a brief summary of the Papyrus of Ani for context."""
    return """**The Papyrus of Ani** (circa 1240 BCE) is the finest surviving copy of the Egyptian Book of the Dead (Per Em Hru - "Coming Forth by Day"). 

Created for Ani, Royal Scribe of Thebes, it contains:
- **192 spells and hymns** for the afterlife journey
- **The Weighing of the Heart** (Chapter 125) - judgment before Osiris and the 42 gods
- **Transformation spells** - becoming falcon, phoenix (Benu), serpent
- **Protective incantations** - against snakes, demons, the "second death"
- **Hymns to Ra, Osiris, and the Ennead**

The Throne of Anhu honors this ancient wisdom as it connects to the Abasid 1841 teachings on judgment, transformation, and eternal life."""
