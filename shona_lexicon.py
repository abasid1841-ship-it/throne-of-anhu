"""
Shona Lexicon - A vocabulary reference for understanding Shona words and phrases.

This lexicon provides word meanings to help the AI correctly interpret 
scroll teachings. Scroll teachings ALWAYS take priority over lexical definitions.
"""

import re
from typing import Optional, Dict, List, Tuple

# Core Shona vocabulary derived from scrolls and verified sources
# Format: word -> (meaning, context_note, scroll_reference)
SHONA_LEXICON: Dict[str, Tuple[str, str, Optional[str]]] = {
    # Common words from scrolls
    "guru": ("crowd, multitude, many people", "Often used in compound words", None),
    "mwandira": ("followers, those who follow, crowd following", "From 'ku-anda' - to follow", None),
    "gurumwandira": ("following the crowd, crowd followers, mob mentality", 
                     "NEGATIVE connotation in scrolls - teachings warn AGAINST following crowds blindly", 
                     "DHM-04: ZIVA KUTI GURU MWANDIRA HARINA DENGA"),
    "harina": ("has no, does not have, without", "Negation particle", None),
    "rwendo": ("journey, path, way, road", "Often used metaphorically for life's path", None),
    "denga": ("heaven, sky, the heavens", "Sacred space above", None),
    "mbinga": ("rich person, wealthy one, billionaire", 
               "NEGATIVE when attached to greed; POSITIVE when wealth serves others",
               "DHM-01: DENGA HARINA MBINGA"),
    
    # Spiritual terms
    "mwari": ("God, the Creator, the Almighty", "Supreme deity", None),
    "tenzi": ("Lord, Master, Teacher", "Title of respect", None),
    "mudzimu": ("spirit, ancestral spirit", "Spiritual realm connection", None),
    "mweya": ("spirit, breath, soul", "The life force", None),
    "mutsvene": ("holy, sacred, pure", "Spiritual purity", None),
    "ngirozi": ("angel, heavenly messenger", "Divine messenger", None),
    
    # Key concepts
    "chokwadi": ("truth, reality, what is real", "Central theme of scrolls", None),
    "rudo": ("love, compassion, kindness", "Divine love", None),
    "tsitsi": ("mercy, compassion, pity", "Divine mercy", None),
    "runyararo": ("peace, tranquility", "Spiritual peace", None),
    "kururama": ("righteousness, justice", "Moral uprightness", None),
    
    # Scroll-specific terms
    "masowe": ("wilderness, sacred gathering place", "Johane Masowe tradition - open air worship", None),
    "abasid": ("reference to 1841 - prophetic identifier", "ABASID 1841 - The Christ Sun RA", None),
    "tirona": ("throne, seat of authority", "Divine seat of judgment", "THRONE-01"),
    "ani": ("I am (emphatic)", "Declaration of identity", None),
    "idi": ("I am truth", "Core identity declaration", "IDI scrolls"),
    
    # Teaching words
    "dzidziso": ("teaching, lesson, instruction", "Educational content", None),
    "murayiro": ("commandment, law, instruction", "Divine law", None),
    "mitemo": ("laws, commandments, rules", "Divine laws", None),
    "chiporofiti": ("prophecy, prophetic word", "Divine revelation", None),
    
    # Names and titles (with common spelling variations)
    "johane": ("John, Johane", "Baba Johane - founder of Masowe tradition", "NHOROONDO-01"),
    "johani": ("John, Johane", "Baba Johane - founder of Masowe tradition (alternate spelling)", "NHOROONDO-01"),
    "baba": ("father, elder, respected one", "Title of respect for Johane", None),
    "baba johane": ("Father Johane", "Baba Johane Masowe - founder of the Masowe tradition", "NHOROONDO-01"),
    "baba johani": ("Father Johane", "Baba Johane Masowe - founder of the Masowe tradition (alternate)", "NHOROONDO-01"),
    "messiah": ("anointed one, savior", "Divine deliverer", None),
    "erijah": ("Elijah, the prophet", "Prophetic figure", None),
    "elijah": ("Elijah, the prophet", "Prophetic figure (English spelling)", None),
    
    # Action words
    "namata": ("pray, worship", "Spiritual practice", None),
    "tenda": ("believe, have faith", "Faith action", None),
    "pinduka": ("repent, turn around, change", "Spiritual transformation", None),
    "sunungura": ("set free, liberate, deliver", "Freedom/deliverance", None),
    
    # Warning words
    "huroyi": ("witchcraft, sorcery", "Forbidden practice - strongly condemned", None),
    "hunanga": ("traditional healing/divination", "Practice to be abandoned", None),
    "hutsinye": ("cruelty, wickedness", "Evil behavior", None),
    "humbavha": ("theft, stealing", "Condemned practice", None),
    
    # Common greetings and phrases
    "mazvita": ("thank you, greetings", "Expression of gratitude", None),
    "mhoro": ("hello, greetings", "Common greeting", None),
    "tatenda": ("we are grateful", "Expression of group thanks", None),
    "amen": ("amen, so be it", "Affirmation", None),
}

# Word spacing variations - maps spaced versions to compound words
WORD_SPACING_VARIANTS: Dict[str, str] = {
    "guru mwandira": "gurumwandira",
    "guru-mwandira": "gurumwandira",
    "dzi no bika": "dzinobika",
    "ha adi": "haadi",
}

# Phrases and compound terms
SHONA_PHRASES: Dict[str, Tuple[str, str]] = {
    "guru mwandira harina rwendo": (
        "following the crowd has no path/journey",
        "WARNING: Do not follow the crowd blindly - they have no direction"
    ),
    "guru mwandira harina denga": (
        "following the crowd has no heaven",
        "WARNING: Crowd followers will not reach heaven - think independently"
    ),
    "denga harina mbinga": (
        "heaven has no billionaires",
        "TEACHING: Wealth alone does not grant entry to heaven - character matters"
    ),
    "mwari ma ari": (
        "God is within/God is present",
        "Divine presence - when love is in money, God is there"
    ),
    "tirona ndini": (
        "I am the Throne",
        "Declaration of divine authority"
    ),
    "ziva kuti": (
        "know that",
        "Introducing important teaching/revelation"
    ),
}

# Ambiguous words that may need clarification
AMBIGUOUS_TERMS: Dict[str, List[Dict]] = {
    "guru": [
        {"meaning": "crowd, multitude", "context": "Shona word for many people"},
        {"meaning": "teacher, spiritual master", "context": "Sanskrit/Hindu term - may be confused"}
    ],
    "ari": [
        {"meaning": "is/are (verb)", "context": "Shona - location or state"},
        {"meaning": "name (Arabic)", "context": "Could be a person's name"}
    ],
    "ra": [
        {"meaning": "The Sun deity, ABASID identity", "context": "Egyptian/scroll reference"},
        {"meaning": "of/for (preposition)", "context": "Shona grammar particle"}
    ],
}


def normalize_shona(text: str) -> str:
    """Normalize Shona text for lookup (lowercase, remove extra spaces)."""
    return ' '.join(text.lower().strip().split())


def get_compound_variations(text: str) -> List[str]:
    """
    Generate possible compound word variations.
    E.g., 'guru mwandira' -> ['gurumwandira', 'guru mwandira']
    """
    normalized = normalize_shona(text)
    variations = [normalized]
    
    # Try without spaces
    no_spaces = normalized.replace(' ', '')
    if no_spaces != normalized:
        variations.append(no_spaces)
    
    # Try with spaces between each pair of words
    words = normalized.split()
    if len(words) > 1:
        for i in range(len(words) - 1):
            joined = ''.join(words[:i+1]) + ' ' + ' '.join(words[i+1:])
            if joined not in variations:
                variations.append(joined)
            all_joined = ''.join(words[:i+1]) + ''.join(words[i+1:])
            if all_joined not in variations:
                variations.append(all_joined)
    
    # Check spacing variants dictionary
    if normalized in WORD_SPACING_VARIANTS:
        compound = WORD_SPACING_VARIANTS[normalized]
        if compound not in variations:
            variations.append(compound)
    
    # Reverse check - if it's a compound, add spaced version
    for spaced, compound in WORD_SPACING_VARIANTS.items():
        if normalized == compound and spaced not in variations:
            variations.append(spaced)
    
    return variations


def lookup_word(word: str, use_fuzzy: bool = True) -> Optional[Dict]:
    """
    Look up a single Shona word in the lexicon.
    Returns dict with meaning, context, and scroll reference if found.
    Supports fuzzy matching for typos (e.g., gurumwandiro -> gurumwandira).
    """
    from fuzzy_match import fuzzy_lookup, suggest_correction
    
    # Try all variations (exact match first)
    for variation in get_compound_variations(word):
        if variation in SHONA_LEXICON:
            meaning, context, scroll_ref = SHONA_LEXICON[variation]
            return {
                "word": word,
                "normalized": variation,
                "meaning": meaning,
                "context": context,
                "scroll_reference": scroll_ref,
                "source": "lexicon",
                "fuzzy_match": False
            }
    
    # Try fuzzy matching if exact match not found
    if use_fuzzy:
        fuzzy_result = fuzzy_lookup(word, SHONA_LEXICON, threshold=0.75)
        if fuzzy_result:
            matched_key, value, similarity = fuzzy_result
            meaning, context, scroll_ref = value
            return {
                "word": word,
                "normalized": matched_key,
                "meaning": meaning,
                "context": context,
                "scroll_reference": scroll_ref,
                "source": "lexicon",
                "fuzzy_match": True,
                "similarity": similarity,
                "corrected_from": word,
                "corrected_to": matched_key
            }
    
    return None


def lookup_phrase(phrase: str, use_fuzzy: bool = True) -> Optional[Dict]:
    """
    Look up a Shona phrase in the phrase dictionary.
    Returns dict with meaning and teaching context if found.
    Supports fuzzy matching for typos.
    """
    from fuzzy_match import fuzzy_lookup
    
    # Try all variations (exact match first)
    for variation in get_compound_variations(phrase):
        if variation in SHONA_PHRASES:
            meaning, teaching = SHONA_PHRASES[variation]
            return {
                "phrase": phrase,
                "meaning": meaning,
                "teaching": teaching,
                "source": "lexicon"
            }
    
    # Try partial match
    normalized = normalize_shona(phrase)
    for stored_phrase, (meaning, teaching) in SHONA_PHRASES.items():
        if stored_phrase in normalized or normalized in stored_phrase:
            return {
                "phrase": phrase,
                "meaning": meaning,
                "teaching": teaching,
                "source": "lexicon"
            }
    
    return None


def check_ambiguity(query: str) -> Optional[Dict]:
    """
    Check if the query contains ambiguous terms that need clarification.
    Returns a clarification question if needed.
    """
    normalized = normalize_shona(query)
    words = normalized.split()
    
    for word in words:
        if word in AMBIGUOUS_TERMS:
            options = AMBIGUOUS_TERMS[word]
            if len(options) > 1:
                return {
                    "word": word,
                    "options": options,
                    "needs_clarification": True
                }
    
    return None


def generate_clarification_question(ambiguity: Dict) -> str:
    """Generate a clarification question for ambiguous terms."""
    word = ambiguity["word"]
    options = ambiguity["options"]
    
    question = f"I want to make sure I understand you correctly. When you say '{word}', do you mean:\n"
    for i, opt in enumerate(options, 1):
        question += f"{i}. {opt['meaning']} ({opt['context']})\n"
    question += "\nPlease let me know which meaning you intended."
    
    return question


def annotate_query(query: str) -> Dict:
    """
    Analyze a user query and annotate any Shona words/phrases found.
    Returns a dict with:
    - original_query: the original text
    - annotations: list of word/phrase meanings found
    - context_note: summary for AI prompt
    - needs_clarification: whether to ask user for clarification
    - clarification_question: the question to ask if needed
    """
    annotations = []
    context_notes = []
    
    normalized_query = normalize_shona(query)
    
    # First check for phrase matches
    phrase_result = lookup_phrase(query)
    if phrase_result:
        annotations.append(phrase_result)
        if phrase_result.get("teaching"):
            context_notes.append(phrase_result["teaching"])
    
    # Then check individual words
    words = normalized_query.split()
    for word in words:
        word_result = lookup_word(word)
        if word_result:
            annotations.append(word_result)
            if word_result.get("context"):
                context_notes.append(f"{word}: {word_result['context']}")
    
    # Also try the whole query as one word (no spaces)
    whole_word = normalized_query.replace(' ', '')
    if len(whole_word) > 3:
        word_result = lookup_word(whole_word)
        if word_result:
            # Check if we already have this annotation
            already_found = any(
                ann.get("normalized") == word_result.get("normalized") 
                for ann in annotations if "normalized" in ann
            )
            if not already_found:
                annotations.append(word_result)
                if word_result.get("context"):
                    context_notes.append(word_result["context"])
    
    # Check for ambiguity only if we found some content but meaning is unclear
    needs_clarification = False
    clarification_question = None
    
    if not annotations:
        # No matches found - check if there are ambiguous terms
        ambiguity = check_ambiguity(query)
        if ambiguity:
            needs_clarification = True
            clarification_question = generate_clarification_question(ambiguity)
    
    return {
        "original_query": query,
        "annotations": annotations,
        "context_note": " | ".join(context_notes) if context_notes else None,
        "has_shona_content": len(annotations) > 0,
        "needs_clarification": needs_clarification,
        "clarification_question": clarification_question
    }


def get_lexical_context_for_prompt(query: str) -> Optional[str]:
    """
    Generate a lexical context string to inject into the AI prompt.
    This helps the AI understand Shona terms before responding.
    
    Returns None if no Shona content detected.
    """
    result = annotate_query(query)
    
    # If clarification is needed, return the question
    if result.get("needs_clarification") and result.get("clarification_question"):
        return f"[CLARIFICATION NEEDED]\n{result['clarification_question']}"
    
    if not result["has_shona_content"]:
        return None
    
    lines = ["[SHONA LEXICAL CONTEXT]"]
    lines.append("The user's query contains Shona words. Here are their meanings:")
    
    seen_words = set()
    for ann in result["annotations"]:
        if "meaning" in ann:
            word = ann.get("word") or ann.get("phrase", "")
            word_upper = word.upper()
            
            # Skip duplicates
            if word_upper in seen_words:
                continue
            seen_words.add(word_upper)
            
            meaning = ann["meaning"]
            
            # Show typo correction if applicable
            if ann.get("fuzzy_match") and ann.get("corrected_to"):
                corrected = ann["corrected_to"].upper()
                lines.append(f"• {word_upper} (interpreted as {corrected}): {meaning}")
                lines.append(f"  NOTE: User may have typed '{word}' but meant '{ann['corrected_to']}'")
            else:
                lines.append(f"• {word_upper}: {meaning}")
            
            if ann.get("teaching"):
                lines.append(f"  SCROLL TEACHING: {ann['teaching']}")
            elif ann.get("context"):
                lines.append(f"  CONTEXT: {ann['context']}")
            
            if ann.get("scroll_reference"):
                lines.append(f"  REFERENCE: {ann['scroll_reference']}")
    
    lines.append("")
    lines.append("IMPORTANT: Use these meanings to correctly interpret scroll teachings.")
    lines.append("The scroll's teaching ALWAYS takes priority over general word definitions.")
    lines.append("If the scroll warns against something, convey that warning clearly.")
    
    return "\n".join(lines)


# For testing
if __name__ == "__main__":
    test_queries = [
        "Gurumwandira",
        "guru mwandira",
        "Guru Mwandira Harina Denga",
        "denga harina mbinga",
        "What is mbinga?",
        "Tell me about Baba Johane",
    ]
    
    for q in test_queries:
        print(f"\nQuery: {q}")
        print("-" * 40)
        context = get_lexical_context_for_prompt(q)
        if context:
            print(context)
        else:
            print("(No Shona content detected)")
