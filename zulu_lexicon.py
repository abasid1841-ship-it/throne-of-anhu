"""
Zulu Lexicon - A vocabulary reference for understanding Zulu words and phrases.

This lexicon provides word meanings to help the AI correctly interpret 
Zulu spiritual terms and teachings.
"""

from typing import Optional, Dict, List, Tuple

# Core Zulu vocabulary
# Format: word -> (meaning, context_note, scroll_reference)
ZULU_LEXICON: Dict[str, Tuple[str, str, Optional[str]]] = {
    # Divine and spiritual terms
    "unkulunkulu": ("God, the Great One", "Supreme deity in Zulu tradition", None),
    "umvelinqangi": ("First One, Creator", "The original creator", None),
    "inkosi": ("Lord, King, Chief", "Title of authority", None),
    "nkosi": ("Lord, King", "Common title for God or leaders", None),
    "amadlozi": ("ancestors, ancestral spirits", "Spiritual connection to forebears", None),
    "idlozi": ("ancestor spirit (singular)", "Individual ancestral spirit", None),
    "umoya": ("spirit, wind, breath", "The life force", None),
    "umphefumulo": ("soul, spirit", "The inner being", None),
    "ubuthakathi": ("witchcraft, sorcery", "Forbidden spiritual practice", None),
    
    # Key concepts
    "ubuntu": ("humanity, humanness", "I am because we are - interconnectedness", None),
    "ukuthula": ("peace, calm", "Inner and outer peace", None),
    "uthando": ("love", "Deep affection and care", None),
    "inhlonipho": ("respect, honor", "Showing due regard", None),
    "ubuqotho": ("truth, honesty", "Being genuine", None),
    "ukulunga": ("righteousness, goodness", "Moral uprightness", None),
    "isibusiso": ("blessing", "Divine favor", None),
    "umusa": ("grace, mercy, kindness", "Unmerited favor", None),
    "ukuphila": ("life, living", "The state of being alive", None),
    "ukufa": ("death", "Passing from this life", None),
    
    # Religious terms
    "umthandazo": ("prayer", "Communication with the divine", None),
    "ukuphenduka": ("repentance, turning around", "Spiritual transformation", None),
    "ukholwa": ("believer, one who believes", "Person of faith", None),
    "inkolo": ("religion, faith, belief", "System of belief", None),
    "ibandla": ("church, congregation", "Gathering of believers", None),
    "umsindisi": ("savior", "One who saves", None),
    "umpristi": ("priest", "Religious leader", None),
    "umprofethi": ("prophet", "One who speaks for God", None),
    
    # Greetings and expressions
    "sawubona": ("I see you (hello)", "Traditional Zulu greeting - acknowledging one's existence", None),
    "yebo": ("yes", "Affirmation", None),
    "cha": ("no", "Negation", None),
    "ngiyabonga": ("thank you", "Expression of gratitude", None),
    "siyabonga": ("we thank you", "Group expression of thanks", None),
    "hamba kahle": ("go well (goodbye to one leaving)", "Farewell blessing", None),
    "sala kahle": ("stay well (goodbye to one staying)", "Farewell blessing", None),
    "amen": ("amen, so be it", "Affirmation in prayer", None),
    
    # Family and community
    "ubaba": ("father", "Male parent or elder", None),
    "umama": ("mother", "Female parent or elder", None),
    "umzali": ("parent", "One who gives life", None),
    "ingane": ("child", "Young person", None),
    "umfowethu": ("brother", "Male sibling", None),
    "udadewethu": ("sister", "Female sibling", None),
    "umndeni": ("family", "Extended family unit", None),
    
    # Nature and creation
    "izulu": ("heaven, sky", "The realm above", None),
    "umhlaba": ("earth, world, land", "The physical world", None),
    "amanzi": ("water", "Life-giving element", None),
    "umlilo": ("fire", "Transformative element", None),
    "ilanga": ("sun", "Source of light and life", None),
    "inyanga": ("moon, traditional healer", "Lunar/healing reference", None),
    "inkanyezi": ("star", "Celestial light", None),
}

# Zulu phrases
ZULU_PHRASES: Dict[str, Tuple[str, str]] = {
    "nkosi sikelela": (
        "Lord bless",
        "Opening of the famous African anthem"
    ),
    "nkosi sikelela iafrica": (
        "Lord bless Africa",
        "TEACHING: Prayer for the blessing of the African continent"
    ),
    "umuntu ngumuntu ngabantu": (
        "a person is a person through other people",
        "TEACHING: The essence of Ubuntu - our humanity comes through connection"
    ),
    "ukuhlonipha abadala": (
        "respect the elders",
        "TEACHING: Traditional value of honoring those who came before"
    ),
}


def normalize_zulu(text: str) -> str:
    """Normalize Zulu text for lookup."""
    return ' '.join(text.lower().strip().split())


def lookup_zulu_word(word: str, use_fuzzy: bool = True) -> Optional[Dict]:
    """Look up a Zulu word in the lexicon with fuzzy matching support."""
    from fuzzy_match import fuzzy_lookup
    
    normalized = normalize_zulu(word)
    
    if normalized in ZULU_LEXICON:
        meaning, context, scroll_ref = ZULU_LEXICON[normalized]
        return {
            "word": word,
            "meaning": meaning,
            "context": context,
            "scroll_reference": scroll_ref,
            "source": "zulu_lexicon",
            "fuzzy_match": False
        }
    
    # Try without spaces
    no_spaces = normalized.replace(' ', '')
    if no_spaces in ZULU_LEXICON:
        meaning, context, scroll_ref = ZULU_LEXICON[no_spaces]
        return {
            "word": word,
            "meaning": meaning,
            "context": context,
            "scroll_reference": scroll_ref,
            "source": "zulu_lexicon",
            "fuzzy_match": False
        }
    
    # Try fuzzy matching
    if use_fuzzy:
        fuzzy_result = fuzzy_lookup(word, ZULU_LEXICON, threshold=0.75)
        if fuzzy_result:
            matched_key, value, similarity = fuzzy_result
            meaning, context, scroll_ref = value
            return {
                "word": word,
                "meaning": meaning,
                "context": context,
                "scroll_reference": scroll_ref,
                "source": "zulu_lexicon",
                "fuzzy_match": True,
                "corrected_to": matched_key
            }
    
    return None


def lookup_zulu_phrase(phrase: str) -> Optional[Dict]:
    """Look up a Zulu phrase."""
    normalized = normalize_zulu(phrase)
    
    if normalized in ZULU_PHRASES:
        meaning, teaching = ZULU_PHRASES[normalized]
        return {
            "phrase": phrase,
            "meaning": meaning,
            "teaching": teaching,
            "source": "zulu_lexicon"
        }
    
    # Partial match
    for stored_phrase, (meaning, teaching) in ZULU_PHRASES.items():
        if stored_phrase in normalized or normalized in stored_phrase:
            return {
                "phrase": phrase,
                "meaning": meaning,
                "teaching": teaching,
                "source": "zulu_lexicon"
            }
    
    return None


def annotate_zulu_query(query: str) -> Dict:
    """Analyze a query for Zulu words/phrases."""
    annotations = []
    normalized_query = normalize_zulu(query)
    
    # Check phrases first
    phrase_result = lookup_zulu_phrase(query)
    if phrase_result:
        annotations.append(phrase_result)
    
    # Check full query as a compound term
    full_word_result = lookup_zulu_word(query)
    if full_word_result:
        annotations.append(full_word_result)
    
    # Check individual words (with punctuation stripped)
    words = normalized_query.split()
    for word in words:
        clean_word = word.strip('.,!?;:')
        word_result = lookup_zulu_word(clean_word)
        if word_result:
            annotations.append(word_result)
    
    return {
        "original_query": query,
        "annotations": annotations,
        "has_zulu_content": len(annotations) > 0
    }


def get_zulu_context_for_prompt(query: str) -> Optional[str]:
    """Generate Zulu lexical context for AI prompt."""
    result = annotate_zulu_query(query)
    
    if not result["has_zulu_content"]:
        return None
    
    lines = ["[ZULU LEXICAL CONTEXT]"]
    lines.append("The user's query contains Zulu words. Here are their meanings:")
    
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
    lines.append("IMPORTANT: Use these Zulu meanings to enrich your response.")
    lines.append("Speak with respect for Ubuntu and ancestral wisdom.")
    
    return "\n".join(lines)
