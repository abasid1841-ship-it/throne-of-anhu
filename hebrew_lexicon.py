"""
Hebrew Lexicon - A vocabulary reference for understanding Hebrew words and phrases.

This lexicon provides word meanings to help the AI correctly interpret 
Torah teachings and Hebrew spiritual terms.
"""

from typing import Optional, Dict, List, Tuple

# Core Hebrew vocabulary from Torah and spiritual texts
# Format: word -> (meaning, context_note, scroll_reference)
HEBREW_LEXICON: Dict[str, Tuple[str, str, Optional[str]]] = {
    # Divine names
    "elohim": ("God, the Divine plural", "Name for God emphasizing power and majesty", "Genesis 1:1"),
    "adonai": ("Lord, my Lord", "Used in place of YHWH in speech", None),
    "yahweh": ("The LORD, I AM", "The sacred Name - pronounced with reverence", "Exodus 3:14"),
    "yhwh": ("The LORD, I AM", "The Tetragrammaton - sacred Name", "Exodus 3:14"),
    "el": ("God, mighty one", "Root word for deity", None),
    "el shaddai": ("God Almighty", "God the All-Sufficient", "Genesis 17:1"),
    "hashem": ("The Name", "Respectful reference to God's Name", None),
    
    # Core concepts
    "shalom": ("peace, wholeness, completeness", "More than absence of conflict - total wellbeing", None),
    "torah": ("instruction, teaching, law", "The five books of Moses - divine guidance", "Torah scrolls"),
    "chesed": ("loving-kindness, mercy, covenant love", "God's faithful love", None),
    "emet": ("truth, faithfulness, reliability", "Absolute truth", None),
    "tzedakah": ("righteousness, justice, charity", "Right action and giving", None),
    "shema": ("hear, listen, obey", "The call to hear and obey God", "Deuteronomy 6:4"),
    "kodesh": ("holy, sacred, set apart", "Holiness - belonging to God", None),
    "ruach": ("spirit, wind, breath", "God's Spirit or breath of life", None),
    "nefesh": ("soul, life, being", "The living soul/person", None),
    "lev": ("heart", "Center of thought and will", None),
    
    # Important terms
    "bereshit": ("in the beginning", "First word of Torah", "Genesis 1:1"),
    "amen": ("truly, so be it, I believe", "Affirmation of truth", None),
    "hallelujah": ("praise the LORD", "Exclamation of praise", "Psalms"),
    "hosanna": ("save us, please save", "Cry for salvation", None),
    "selah": ("pause and reflect", "Musical/meditation term in Psalms", "Psalms"),
    "mazel tov": ("good fortune, congratulations", "Blessing for celebrations", None),
    "mitzvah": ("commandment, good deed", "Divine instruction", None),
    "shabbat": ("sabbath, rest", "The seventh day of rest", "Exodus 20:8"),
    "brit": ("covenant, agreement", "Sacred agreement with God", None),
    
    # Key figures
    "moshe": ("Moses", "The lawgiver who led Israel from Egypt", "Exodus"),
    "avraham": ("Abraham", "Father of faith, friend of God", "Genesis 12"),
    "yitzhak": ("Isaac", "Son of promise", "Genesis 21"),
    "yaakov": ("Jacob/Israel", "Father of the 12 tribes", "Genesis 25"),
    "david": ("David", "King of Israel, psalmist", "Samuel, Psalms"),
    "mashiach": ("messiah, anointed one", "The promised deliverer", None),
    
    # Greetings and phrases
    "baruch": ("blessed", "Opening of blessings", None),
    "baruch hashem": ("blessed be the Name", "Thank God", None),
    "todah": ("thank you, gratitude", "Expression of thanks", None),
    "shalom aleichem": ("peace be upon you", "Traditional greeting", None),
    "l'chaim": ("to life", "Toast/blessing for life", None),
    
    # Sacred places/concepts
    "yerushalayim": ("Jerusalem", "The holy city", None),
    "bet": ("house", "Often used for 'house of' (Beth-el = house of God)", None),
    "mikdash": ("sanctuary, temple", "Holy dwelling place", None),
    "gan eden": ("Garden of Eden", "Paradise, the original garden", "Genesis 2"),
}

# Hebrew phrases
HEBREW_PHRASES: Dict[str, Tuple[str, str]] = {
    "shema yisrael": (
        "Hear O Israel",
        "TEACHING: The central declaration of Jewish faith - God is One"
    ),
    "shema yisrael adonai eloheinu adonai echad": (
        "Hear O Israel, the LORD our God, the LORD is One",
        "TEACHING: The fundamental truth - there is only One God"
    ),
    "baruch ata adonai": (
        "Blessed are You, Lord",
        "Opening of Hebrew blessings"
    ),
    "ani adonai": (
        "I am the LORD",
        "Divine self-declaration"
    ),
    "im yirtzeh hashem": (
        "if God wills",
        "Acknowledging God's sovereignty over plans"
    ),
}

# Ambiguous terms
HEBREW_AMBIGUOUS: Dict[str, List[Dict]] = {
    "chai": [
        {"meaning": "life, living", "context": "Hebrew - as in 'l'chaim' (to life)"},
        {"meaning": "tea", "context": "Could be confused with Hindi/English chai"}
    ],
}


def normalize_hebrew(text: str) -> str:
    """Normalize Hebrew text for lookup."""
    return ' '.join(text.lower().strip().split())


def lookup_hebrew_word(word: str, use_fuzzy: bool = True) -> Optional[Dict]:
    """Look up a Hebrew word in the lexicon with fuzzy matching support."""
    from fuzzy_match import fuzzy_lookup
    
    normalized = normalize_hebrew(word)
    
    if normalized in HEBREW_LEXICON:
        meaning, context, scroll_ref = HEBREW_LEXICON[normalized]
        return {
            "word": word,
            "meaning": meaning,
            "context": context,
            "scroll_reference": scroll_ref,
            "source": "hebrew_lexicon",
            "fuzzy_match": False
        }
    
    # Try without spaces
    no_spaces = normalized.replace(' ', '')
    if no_spaces in HEBREW_LEXICON:
        meaning, context, scroll_ref = HEBREW_LEXICON[no_spaces]
        return {
            "word": word,
            "meaning": meaning,
            "context": context,
            "scroll_reference": scroll_ref,
            "source": "hebrew_lexicon",
            "fuzzy_match": False
        }
    
    # Try fuzzy matching
    if use_fuzzy:
        fuzzy_result = fuzzy_lookup(word, HEBREW_LEXICON, threshold=0.75)
        if fuzzy_result:
            matched_key, value, similarity = fuzzy_result
            meaning, context, scroll_ref = value
            return {
                "word": word,
                "meaning": meaning,
                "context": context,
                "scroll_reference": scroll_ref,
                "source": "hebrew_lexicon",
                "fuzzy_match": True,
                "corrected_to": matched_key
            }
    
    return None


def lookup_hebrew_phrase(phrase: str) -> Optional[Dict]:
    """Look up a Hebrew phrase."""
    normalized = normalize_hebrew(phrase)
    
    if normalized in HEBREW_PHRASES:
        meaning, teaching = HEBREW_PHRASES[normalized]
        return {
            "phrase": phrase,
            "meaning": meaning,
            "teaching": teaching,
            "source": "hebrew_lexicon"
        }
    
    # Partial match
    for stored_phrase, (meaning, teaching) in HEBREW_PHRASES.items():
        if stored_phrase in normalized or normalized in stored_phrase:
            return {
                "phrase": phrase,
                "meaning": meaning,
                "teaching": teaching,
                "source": "hebrew_lexicon"
            }
    
    return None


def annotate_hebrew_query(query: str) -> Dict:
    """Analyze a query for Hebrew words/phrases."""
    annotations = []
    normalized_query = normalize_hebrew(query)
    
    # Check phrases first
    phrase_result = lookup_hebrew_phrase(query)
    if phrase_result:
        annotations.append(phrase_result)
    
    # Check full query as a compound term
    full_word_result = lookup_hebrew_word(query)
    if full_word_result:
        annotations.append(full_word_result)
    
    # Check individual words (with punctuation stripped)
    words = normalized_query.split()
    for word in words:
        clean_word = word.strip('.,!?;:')
        word_result = lookup_hebrew_word(clean_word)
        if word_result:
            annotations.append(word_result)
    
    return {
        "original_query": query,
        "annotations": annotations,
        "has_hebrew_content": len(annotations) > 0
    }


def get_hebrew_context_for_prompt(query: str) -> Optional[str]:
    """Generate Hebrew lexical context for AI prompt."""
    result = annotate_hebrew_query(query)
    
    if not result["has_hebrew_content"]:
        return None
    
    lines = ["[HEBREW LEXICAL CONTEXT]"]
    lines.append("The user's query contains Hebrew words. Here are their meanings:")
    
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
    lines.append("IMPORTANT: Use these Hebrew meanings to enrich your response.")
    lines.append("Speak with reverence when referencing divine names.")
    
    return "\n".join(lines)
