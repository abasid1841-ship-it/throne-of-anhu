"""
Kiswahili Lexicon - A vocabulary reference for understanding Swahili words and phrases.

This lexicon provides word meanings to help the AI correctly interpret 
Swahili spiritual terms and East African teachings.
"""

from typing import Optional, Dict, List, Tuple

# Core Kiswahili vocabulary
# Format: word -> (meaning, context_note, scroll_reference)
KISWAHILI_LEXICON: Dict[str, Tuple[str, str, Optional[str]]] = {
    # Divine and spiritual terms
    "mungu": ("God", "The Supreme Being", None),
    "mwenyezi": ("Almighty, All-powerful", "Attribute of God", None),
    "bwana": ("Lord, Master", "Title for God or respected person", None),
    "roho": ("spirit, soul", "The inner being", None),
    "roho mtakatifu": ("Holy Spirit", "The divine Spirit", None),
    "malaika": ("angel", "Heavenly messenger", None),
    "shetani": ("devil, satan", "The evil one", None),
    "dhambi": ("sin", "Transgression against God", None),
    "wokovu": ("salvation", "Being saved", None),
    "imani": ("faith, belief", "Trust in God", None),
    
    # Key concepts
    "upendo": ("love", "Deep affection and care", None),
    "amani": ("peace", "Tranquility and harmony", None),
    "haki": ("justice, righteousness", "What is right and fair", None),
    "ukweli": ("truth", "What is real and genuine", None),
    "neema": ("grace, mercy", "Undeserved favor", None),
    "baraka": ("blessing", "Divine favor", None),
    "huruma": ("compassion, mercy", "Tender care for others", None),
    "uaminifu": ("faithfulness, loyalty", "Being true to one's word", None),
    "subira": ("patience", "Enduring with calm", None),
    "tumaini": ("hope", "Expectation of good", None),
    "furaha": ("joy, happiness", "Inner gladness", None),
    "hekima": ("wisdom", "Deep understanding", None),
    "ujuzi": ("knowledge", "Acquired understanding", None),
    "utu": ("humanity, humanness", "Similar to Ubuntu", None),
    
    # Religious terms
    "sala": ("prayer", "Communication with God", None),
    "kuomba": ("to pray, to ask", "Making requests", None),
    "kuabudu": ("to worship", "Giving honor to God", None),
    "toba": ("repentance", "Turning from wrong", None),
    "msamaha": ("forgiveness", "Pardoning wrongs", None),
    "ubatizo": ("baptism", "Water ceremony of faith", None),
    "ushirika": ("communion, fellowship", "Sharing together", None),
    "kanisa": ("church", "Place of worship", None),
    "msalaba": ("cross", "Symbol of salvation", None),
    "injili": ("gospel, good news", "Message of salvation", None),
    "biblia": ("Bible", "Holy scriptures", None),
    "kurani": ("Quran", "Holy book of Islam", None),
    
    # Key figures
    "nabii": ("prophet", "One who speaks for God", None),
    "mtume": ("apostle, messenger", "One sent with a message", None),
    "yesu": ("Jesus", "The Messiah", None),
    "kristo": ("Christ, Messiah", "The Anointed One", None),
    "musa": ("Moses", "The lawgiver", None),
    "ibrahim": ("Abraham", "Father of faith", None),
    "muhammadi": ("Muhammad", "Prophet of Islam", None),
    
    # Greetings and expressions
    "jambo": ("hello, how are you", "Common greeting", None),
    "habari": ("news, how are you", "Greeting asking about one's state", None),
    "shikamoo": ("respectful greeting to elders", "I hold your feet - deep respect", None),
    "marahaba": ("response to shikamoo", "I am pleased", None),
    "asante": ("thank you", "Expression of gratitude", None),
    "asante sana": ("thank you very much", "Deep gratitude", None),
    "karibu": ("welcome", "Warm reception", None),
    "kwaheri": ("goodbye", "Farewell", None),
    "pole": ("sorry, sympathy", "Expression of care", None),
    "pole pole": ("slowly, gently", "Take it easy", None),
    "hakuna matata": ("no worries, no problem", "Don't worry", None),
    "amina": ("amen", "So be it", None),
    
    # Family and community
    "baba": ("father", "Male parent or elder", None),
    "mama": ("mother", "Female parent or elder", None),
    "ndugu": ("sibling, relative", "Family member", None),
    "kaka": ("brother", "Male sibling", None),
    "dada": ("sister", "Female sibling", None),
    "familia": ("family", "Family unit", None),
    "jamii": ("community, society", "Group of people", None),
    "watoto": ("children", "Young ones", None),
    "mzee": ("elder, old person", "Respected elder", None),
    
    # Nature and creation
    "mbingu": ("heaven, sky", "The realm above", None),
    "dunia": ("world, earth", "The physical world", None),
    "maji": ("water", "Life-giving element", None),
    "moto": ("fire", "Transformative element", None),
    "jua": ("sun", "Source of light", None),
    "mwezi": ("moon", "Night light", None),
    "nyota": ("star", "Celestial light", None),
    "upepo": ("wind", "Moving air", None),
    
    # Life concepts
    "uzima": ("life, health", "State of living well", None),
    "kifo": ("death", "End of earthly life", None),
    "milele": ("forever, eternity", "Without end", None),
    "siku": ("day", "Period of time", None),
    "kesho": ("tomorrow", "The coming day", None),
    "leo": ("today", "This day", None),
    "jana": ("yesterday", "The past day", None),
}

# Kiswahili phrases
KISWAHILI_PHRASES: Dict[str, Tuple[str, str]] = {
    "mungu akubariki": (
        "may God bless you",
        "Blessing spoken to another"
    ),
    "mungu ni mwema": (
        "God is good",
        "TEACHING: Declaration of God's goodness"
    ),
    "bwana asifiwe": (
        "praise the Lord",
        "Expression of worship"
    ),
    "hakuna mungu kama wewe": (
        "there is no God like You",
        "TEACHING: Declaration of God's uniqueness"
    ),
    "yesu ni bwana": (
        "Jesus is Lord",
        "Christian declaration of faith"
    ),
    "upendo ni muhimu": (
        "love is important",
        "TEACHING: The centrality of love"
    ),
    "harambee": (
        "let us pull together",
        "TEACHING: Unity and collective effort - famous Kenyan motto"
    ),
    "pamoja tunaweza": (
        "together we can",
        "TEACHING: Unity brings strength"
    ),
}


def normalize_kiswahili(text: str) -> str:
    """Normalize Kiswahili text for lookup."""
    return ' '.join(text.lower().strip().split())


def lookup_kiswahili_word(word: str, use_fuzzy: bool = True) -> Optional[Dict]:
    """Look up a Kiswahili word in the lexicon with fuzzy matching support."""
    from fuzzy_match import fuzzy_lookup
    
    normalized = normalize_kiswahili(word)
    
    if normalized in KISWAHILI_LEXICON:
        meaning, context, scroll_ref = KISWAHILI_LEXICON[normalized]
        return {
            "word": word,
            "meaning": meaning,
            "context": context,
            "scroll_reference": scroll_ref,
            "source": "kiswahili_lexicon",
            "fuzzy_match": False
        }
    
    # Try without spaces
    no_spaces = normalized.replace(' ', '')
    if no_spaces in KISWAHILI_LEXICON:
        meaning, context, scroll_ref = KISWAHILI_LEXICON[no_spaces]
        return {
            "word": word,
            "meaning": meaning,
            "context": context,
            "scroll_reference": scroll_ref,
            "source": "kiswahili_lexicon",
            "fuzzy_match": False
        }
    
    # Try fuzzy matching
    if use_fuzzy:
        fuzzy_result = fuzzy_lookup(word, KISWAHILI_LEXICON, threshold=0.75)
        if fuzzy_result:
            matched_key, value, similarity = fuzzy_result
            meaning, context, scroll_ref = value
            return {
                "word": word,
                "meaning": meaning,
                "context": context,
                "scroll_reference": scroll_ref,
                "source": "kiswahili_lexicon",
                "fuzzy_match": True,
                "corrected_to": matched_key
            }
    
    return None


def lookup_kiswahili_phrase(phrase: str) -> Optional[Dict]:
    """Look up a Kiswahili phrase."""
    normalized = normalize_kiswahili(phrase)
    
    if normalized in KISWAHILI_PHRASES:
        meaning, teaching = KISWAHILI_PHRASES[normalized]
        return {
            "phrase": phrase,
            "meaning": meaning,
            "teaching": teaching,
            "source": "kiswahili_lexicon"
        }
    
    # Partial match
    for stored_phrase, (meaning, teaching) in KISWAHILI_PHRASES.items():
        if stored_phrase in normalized or normalized in stored_phrase:
            return {
                "phrase": phrase,
                "meaning": meaning,
                "teaching": teaching,
                "source": "kiswahili_lexicon"
            }
    
    return None


def annotate_kiswahili_query(query: str) -> Dict:
    """Analyze a query for Kiswahili words/phrases."""
    annotations = []
    normalized_query = normalize_kiswahili(query)
    
    # Check phrases first
    phrase_result = lookup_kiswahili_phrase(query)
    if phrase_result:
        annotations.append(phrase_result)
    
    # Check full query as a compound word (e.g., "hakuna matata")
    full_word_result = lookup_kiswahili_word(query)
    if full_word_result:
        annotations.append(full_word_result)
    
    # Check individual words
    words = normalized_query.split()
    for word in words:
        # Strip punctuation
        clean_word = word.strip('.,!?;:')
        word_result = lookup_kiswahili_word(clean_word)
        if word_result:
            annotations.append(word_result)
    
    return {
        "original_query": query,
        "annotations": annotations,
        "has_kiswahili_content": len(annotations) > 0
    }


def get_kiswahili_context_for_prompt(query: str) -> Optional[str]:
    """Generate Kiswahili lexical context for AI prompt."""
    result = annotate_kiswahili_query(query)
    
    if not result["has_kiswahili_content"]:
        return None
    
    lines = ["[KISWAHILI LEXICAL CONTEXT]"]
    lines.append("The user's query contains Kiswahili words. Here are their meanings:")
    
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
    lines.append("IMPORTANT: Use these Kiswahili meanings to enrich your response.")
    lines.append("Embrace the warmth and communal spirit of East African wisdom.")
    
    return "\n".join(lines)
