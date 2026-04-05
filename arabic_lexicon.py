"""
Arabic Lexicon - A vocabulary reference for understanding Arabic/Quranic words and phrases.

This lexicon provides word meanings to help the AI correctly interpret 
Quranic teachings and Islamic spiritual terms.
"""

from typing import Optional, Dict, List, Tuple

# Core Arabic vocabulary from Quran and Islamic texts
# Format: word -> (meaning, context_note, scroll_reference)
ARABIC_LEXICON: Dict[str, Tuple[str, str, Optional[str]]] = {
    # Divine names (99 Names of Allah)
    "allah": ("God, The One God", "The supreme name of God in Islam", "Quran 1:1"),
    "ar-rahman": ("The Most Gracious", "Name of Allah - infinite mercy", "Quran 1:1"),
    "ar-rahim": ("The Most Merciful", "Name of Allah - compassionate mercy", "Quran 1:1"),
    "al-malik": ("The King, The Sovereign", "Name of Allah - ultimate ruler", None),
    "al-quddus": ("The Holy One", "Name of Allah - absolutely pure", None),
    "al-aziz": ("The Mighty, The Almighty", "Name of Allah - invincible power", None),
    "al-hakeem": ("The Wise", "Name of Allah - infinite wisdom", None),
    "al-wadud": ("The Loving", "Name of Allah - loving and beloved", None),
    
    # Core concepts
    "islam": ("submission, surrender to God", "The religion of peace through surrender", None),
    "muslim": ("one who submits to God", "A follower of Islam", None),
    "iman": ("faith, belief", "Inner conviction in God and His messengers", None),
    "taqwa": ("God-consciousness, piety", "Awareness of God in all actions", None),
    "deen": ("religion, way of life", "Complete system of faith and practice", None),
    "salah": ("prayer, ritual worship", "The five daily prayers", None),
    "zakat": ("charity, purification of wealth", "Obligatory giving", None),
    "sawm": ("fasting", "Especially during Ramadan", None),
    "hajj": ("pilgrimage to Mecca", "Sacred journey to the holy city", None),
    "jihad": ("striving, struggle for good", "Inner and outer struggle against evil", None),
    
    # Quranic terms
    "quran": ("recitation, that which is read", "The Holy Book of Islam", None),
    "ayah": ("verse, sign, miracle", "A verse of the Quran", None),
    "surah": ("chapter", "A chapter of the Quran", None),
    "bismillah": ("in the name of God", "Opening phrase of most surahs", "Quran 1:1"),
    "alhamdulillah": ("praise be to God", "Expression of gratitude", "Quran 1:2"),
    "subhanallah": ("glory be to God", "Expression of awe", None),
    "allahu akbar": ("God is greatest", "Declaration of God's supremacy", None),
    "inshallah": ("if God wills", "Acknowledging God's will", None),
    "mashallah": ("what God has willed", "Expression of appreciation", None),
    
    # Key figures
    "muhammad": ("Prophet Muhammad (PBUH)", "The final messenger of God", None),
    "ibrahim": ("Abraham", "Father of prophets", None),
    "musa": ("Moses", "Prophet who received Torah", None),
    "isa": ("Jesus", "Prophet and Messiah in Islam", None),
    "maryam": ("Mary", "Mother of Jesus, honored in Quran", "Surah Maryam"),
    "jibril": ("Gabriel", "Angel of revelation", None),
    "nabi": ("prophet", "One who receives divine message", None),
    "rasul": ("messenger", "Prophet sent with a book/law", None),
    
    # Important terms
    "jannah": ("paradise, garden", "The eternal reward", None),
    "jahannam": ("hellfire", "Place of punishment", None),
    "akhirah": ("the hereafter, afterlife", "Life after death", None),
    "dunya": ("this world, worldly life", "Temporary earthly existence", None),
    "sabr": ("patience, perseverance", "Enduring with faith", None),
    "shukr": ("gratitude, thankfulness", "Being grateful to God", None),
    "tawbah": ("repentance", "Returning to God", None),
    "hidayah": ("guidance", "Divine guidance to truth", None),
    "barakah": ("blessing", "Divine grace and increase", None),
    "rahma": ("mercy", "Divine compassion", None),
    "nur": ("light", "Divine light and guidance", "Surah An-Nur"),
    "haqq": ("truth, reality", "Ultimate truth", None),
    
    # Greetings
    "salam": ("peace", "Core of Islamic greeting", None),
    "assalamu alaikum": ("peace be upon you", "Islamic greeting", None),
    "wa alaikum assalam": ("and upon you peace", "Response to greeting", None),
    "jazakallah": ("may God reward you", "Expression of thanks", None),
    "ameen": ("amen, so be it", "Affirmation after prayer", None),
}

# Arabic phrases
ARABIC_PHRASES: Dict[str, Tuple[str, str]] = {
    "la ilaha illallah": (
        "there is no god but God",
        "TEACHING: The fundamental declaration of Islamic faith - tawhid (oneness of God)"
    ),
    "la ilaha illallah muhammadur rasulullah": (
        "there is no god but God, Muhammad is the messenger of God",
        "TEACHING: The complete shahada - declaration of faith"
    ),
    "bismillah ar-rahman ar-rahim": (
        "in the name of God, the Most Gracious, the Most Merciful",
        "Opening of every surah except At-Tawbah"
    ),
    "alhamdulillahi rabbil alamin": (
        "praise be to God, Lord of all worlds",
        "Opening of Al-Fatiha - the mother of the Quran"
    ),
    "inna lillahi wa inna ilaihi rajiun": (
        "indeed we belong to God and to Him we shall return",
        "Said upon hearing of death or calamity"
    ),
}

# Honorifics to add after names
ARABIC_HONORIFICS = {
    "muhammad": "(peace be upon him)",
    "isa": "(peace be upon him)",
    "musa": "(peace be upon him)",
    "ibrahim": "(peace be upon him)",
}


def normalize_arabic(text: str) -> str:
    """Normalize Arabic text for lookup."""
    return ' '.join(text.lower().strip().split())


def lookup_arabic_word(word: str, use_fuzzy: bool = True) -> Optional[Dict]:
    """Look up an Arabic word in the lexicon with fuzzy matching support."""
    from fuzzy_match import fuzzy_lookup
    
    normalized = normalize_arabic(word)
    
    if normalized in ARABIC_LEXICON:
        meaning, context, scroll_ref = ARABIC_LEXICON[normalized]
        honorific = ARABIC_HONORIFICS.get(normalized, "")
        return {
            "word": word,
            "meaning": meaning + (f" {honorific}" if honorific else ""),
            "context": context,
            "scroll_reference": scroll_ref,
            "source": "arabic_lexicon",
            "fuzzy_match": False
        }
    
    # Try without spaces
    no_spaces = normalized.replace(' ', '')
    if no_spaces in ARABIC_LEXICON:
        meaning, context, scroll_ref = ARABIC_LEXICON[no_spaces]
        return {
            "word": word,
            "meaning": meaning,
            "context": context,
            "scroll_reference": scroll_ref,
            "source": "arabic_lexicon",
            "fuzzy_match": False
        }
    
    # Try fuzzy matching
    if use_fuzzy:
        fuzzy_result = fuzzy_lookup(word, ARABIC_LEXICON, threshold=0.75)
        if fuzzy_result:
            matched_key, value, similarity = fuzzy_result
            meaning, context, scroll_ref = value
            honorific = ARABIC_HONORIFICS.get(matched_key, "")
            return {
                "word": word,
                "meaning": meaning + (f" {honorific}" if honorific else ""),
                "context": context,
                "scroll_reference": scroll_ref,
                "source": "arabic_lexicon",
                "fuzzy_match": True,
                "corrected_to": matched_key
            }
    
    return None


def lookup_arabic_phrase(phrase: str) -> Optional[Dict]:
    """Look up an Arabic phrase."""
    normalized = normalize_arabic(phrase)
    
    if normalized in ARABIC_PHRASES:
        meaning, teaching = ARABIC_PHRASES[normalized]
        return {
            "phrase": phrase,
            "meaning": meaning,
            "teaching": teaching,
            "source": "arabic_lexicon"
        }
    
    # Partial match
    for stored_phrase, (meaning, teaching) in ARABIC_PHRASES.items():
        if stored_phrase in normalized or normalized in stored_phrase:
            return {
                "phrase": phrase,
                "meaning": meaning,
                "teaching": teaching,
                "source": "arabic_lexicon"
            }
    
    return None


def annotate_arabic_query(query: str) -> Dict:
    """Analyze a query for Arabic words/phrases."""
    annotations = []
    normalized_query = normalize_arabic(query)
    
    # Check phrases first
    phrase_result = lookup_arabic_phrase(query)
    if phrase_result:
        annotations.append(phrase_result)
    
    # Check full query as a compound term
    full_word_result = lookup_arabic_word(query)
    if full_word_result:
        annotations.append(full_word_result)
    
    # Check individual words (with punctuation stripped)
    words = normalized_query.split()
    for word in words:
        clean_word = word.strip('.,!?;:')
        word_result = lookup_arabic_word(clean_word)
        if word_result:
            annotations.append(word_result)
    
    return {
        "original_query": query,
        "annotations": annotations,
        "has_arabic_content": len(annotations) > 0
    }


def get_arabic_context_for_prompt(query: str) -> Optional[str]:
    """Generate Arabic lexical context for AI prompt."""
    result = annotate_arabic_query(query)
    
    if not result["has_arabic_content"]:
        return None
    
    lines = ["[ARABIC/QURANIC LEXICAL CONTEXT]"]
    lines.append("The user's query contains Arabic/Islamic terms. Here are their meanings:")
    
    seen = set()
    for ann in result["annotations"]:
        word = ann.get("word") or ann.get("phrase", "")
        if word.upper() in seen:
            continue
        seen.add(word.upper())
        
        meaning = ann.get("meaning", "")
        lines.append(f"• {word.upper()}: {meaning}")
        
        if ann.get("teaching"):
            lines.append(f"  TEACHING: {ann['teaching']}")
        elif ann.get("context"):
            lines.append(f"  CONTEXT: {ann['context']}")
        
        if ann.get("scroll_reference"):
            lines.append(f"  REFERENCE: {ann['scroll_reference']}")
    
    lines.append("")
    lines.append("IMPORTANT: Use proper Islamic honorifics when referencing prophets.")
    lines.append("Speak with reverence about Allah and divine matters.")
    
    return "\n".join(lines)
