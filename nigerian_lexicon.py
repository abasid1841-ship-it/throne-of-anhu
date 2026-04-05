"""
Nigerian Lexicon - A vocabulary reference for understanding Nigerian languages.

This lexicon covers the three major Nigerian languages:
- Yoruba (spoken in Southwest Nigeria)
- Hausa (spoken in Northern Nigeria)
- Igbo (spoken in Southeast Nigeria)

Provides word meanings to help the AI correctly interpret Nigerian spiritual terms.
"""

from typing import Optional, Dict, List, Tuple

YORUBA_LEXICON: Dict[str, Tuple[str, str, Optional[str]]] = {
    "olodumare": ("Supreme God, Creator", "The Almighty, source of all existence", None),
    "olorun": ("God, Owner of Heaven", "The Lord of the Sky", None),
    "olofi": ("God, the Divine", "Another name for the Supreme Being", None),
    "orisha": ("deity, divine spirit", "Intermediary spirits between God and humans", None),
    "ori": ("head, inner consciousness, destiny", "The personal god within each person", None),
    "ase": ("power, authority, life force", "The power to make things happen - divine energy", None),
    "ashe": ("power, authority, so be it", "Same as ase - spiritual power and affirmation", None),
    "emi": ("spirit, breath, life", "The vital force of life", None),
    "egun": ("ancestors", "The ancestral spirits", None),
    "egbe": ("community, society", "Spiritual community of souls", None),
    "ifa": ("divination system, oracle", "Sacred wisdom tradition and oracle", None),
    "babalawo": ("father of secrets, diviner", "Priest of Ifa divination", None),
    "iwa": ("character, moral behavior", "Character is the essence of being", None),
    "iwa pele": ("good character, gentle character", "The foundation of all virtue", None),
    "ire": ("blessings, good fortune", "Positive destiny and good things", None),
    "ibi": ("misfortune, negative", "Obstacles and challenges", None),
    "odu": ("sacred verses, chapters of Ifa", "The holy scriptures of Ifa", None),
    "ese": ("verses, poetry", "Sacred poetry and verses", None),
    "ebo": ("sacrifice, offering", "Ritual offering to restore balance", None),
    "awo": ("mystery, secret wisdom", "Hidden spiritual knowledge", None),
    "alafia": ("peace, wellbeing, health", "Complete wellness and harmony", None),
    "ase o": ("so be it, amen", "Affirmation of power and agreement", None),
    "modupe": ("I am grateful, thank you", "Expression of deep gratitude", None),
    "e ku": ("greetings", "General greeting prefix", None),
    "e kaaro": ("good morning", "Morning greeting", None),
    "e kaasan": ("good afternoon", "Afternoon greeting", None),
    "e kale": ("good evening", "Evening greeting", None),
    "oluwa": ("Lord, master", "Title for God or respected person", None),
    "baba": ("father", "Father or elder man", None),
    "iya": ("mother", "Mother or elder woman", None),
    "omo": ("child", "Child or offspring", None),
    "ile": ("house, home, earth", "One's dwelling or homeland", None),
    "orun": ("heaven, sky", "The spiritual realm above", None),
    "aye": ("world, earth", "The physical world", None),
    "iku": ("death", "Transition from physical life", None),
    "atunwa": ("reincarnation", "Return to the physical world", None),
    "kadara": ("destiny, fate", "One's predetermined path", None),
    "ayanmo": ("destiny chosen before birth", "Pre-birth destiny selection", None),
    "adura": ("prayer", "Communication with the divine", None),
    "iyin": ("praise", "Giving honor and glory", None),
    "orin": ("song", "Sacred songs and hymns", None),
    "agbara": ("power, strength", "Spiritual and physical power", None),
    "ogo": ("glory, honor", "Divine glory", None),
    "ife": ("love", "Deep affection", None),
    "alaanu": ("mercy, compassion", "Divine mercy", None),
    "idajo": ("judgment", "Divine judgment", None),
    "otito": ("truth", "What is real and genuine", None),
    "ododo": ("righteousness, justice", "Right conduct", None),
    "igbagbo": ("faith, belief", "Trust in the divine", None),
    "ireti": ("hope", "Expectation of good", None),
    "suuru": ("patience", "Enduring with calm", None),
    "oye": ("wisdom, understanding", "Deep comprehension", None),
    "imo": ("knowledge", "Acquired understanding", None),
}

HAUSA_LEXICON: Dict[str, Tuple[str, str, Optional[str]]] = {
    "allah": ("God", "The One God - Arabic/Islamic term used in Hausa", None),
    "ubangiji": ("God, Lord", "The Supreme Lord", None),
    "ruhu": ("spirit, soul", "The inner being", None),
    "mala'iku": ("angels", "Heavenly messengers", None),
    "shaidan": ("satan, devil", "The evil one", None),
    "zunubi": ("sin", "Transgression against God", None),
    "tsira": ("salvation, escape", "Being saved", None),
    "imani": ("faith", "Belief and trust", None),
    "soyayya": ("love", "Deep affection", None),
    "salama": ("peace", "Tranquility and safety", None),
    "adalci": ("justice", "Fairness and right", None),
    "gaskiya": ("truth", "What is genuine", None),
    "alheri": ("grace, goodness", "Divine favor", None),
    "albarka": ("blessing", "Divine blessing", None),
    "jinkai": ("mercy, compassion", "Tender care", None),
    "amana": ("trust, faithfulness", "Being trustworthy", None),
    "hakuri": ("patience", "Enduring calmly", None),
    "bege": ("hope", "Expectation of good", None),
    "farin ciki": ("joy, happiness", "Inner gladness", None),
    "hikima": ("wisdom", "Deep understanding", None),
    "ilimi": ("knowledge, education", "Learning", None),
    "salla": ("prayer", "Ritual prayer", None),
    "addu'a": ("supplication, prayer", "Asking from God", None),
    "ibada": ("worship", "Devotion to God", None),
    "tuba": ("repentance", "Turning from wrong", None),
    "gafara": ("forgiveness", "Pardoning wrongs", None),
    "baftisma": ("baptism", "Water ceremony", None),
    "coci": ("church", "Place of worship", None),
    "gicciye": ("cross", "Christian symbol", None),
    "bishara": ("gospel, good news", "Message of salvation", None),
    "littafi mai tsarki": ("Holy Bible", "Sacred scriptures", None),
    "alqur'ani": ("Quran", "Holy book of Islam", None),
    "annabi": ("prophet", "One who speaks for God", None),
    "manzo": ("apostle, messenger", "One sent with message", None),
    "yesu": ("Jesus", "The Messiah", None),
    "almasihu": ("Messiah, Christ", "The Anointed One", None),
    "musa": ("Moses", "The lawgiver", None),
    "ibrahim": ("Abraham", "Father of faith", None),
    "muhammadu": ("Muhammad", "Prophet of Islam", None),
    "sannu": ("hello, greetings", "Common greeting", None),
    "sannu da zuwa": ("welcome", "Greeting for arrivals", None),
    "yaya": ("how", "Used in greetings - how are you", None),
    "lafiya": ("health, wellbeing", "State of wellness", None),
    "lafiya lau": ("fine, well", "I am well", None),
    "na gode": ("thank you", "Expression of gratitude", None),
    "nagode sosai": ("thank you very much", "Deep gratitude", None),
    "sai anjima": ("see you later", "Farewell", None),
    "baba": ("father", "Male parent or elder", None),
    "mama": ("mother", "Female parent", None),
    "dan'uwa": ("brother", "Male sibling", None),
    "yar'uwa": ("sister", "Female sibling", None),
    "iyali": ("family", "Family unit", None),
    "al'umma": ("community, nation", "Group of people", None),
    "yara": ("children", "Young ones", None),
    "tsoho": ("elder, old person", "Respected elder", None),
    "sama": ("heaven, sky", "The realm above", None),
    "duniya": ("world", "The physical world", None),
    "ruwa": ("water", "Life-giving element", None),
    "wuta": ("fire", "Transformative element", None),
    "rana": ("sun, day", "Source of light", None),
    "wata": ("moon", "Night light", None),
    "taurari": ("star", "Celestial light", None),
    "rai": ("life, soul", "Living existence", None),
    "mutuwa": ("death", "End of physical life", None),
    "har abada": ("forever", "Without end", None),
    "yau": ("today", "This day", None),
    "gobe": ("tomorrow", "The coming day", None),
    "jiya": ("yesterday", "The past day", None),
    "amin": ("amen", "So be it", None),
}

IGBO_LEXICON: Dict[str, Tuple[str, str, Optional[str]]] = {
    "chukwu": ("God, the Great Spirit", "The Supreme Being", None),
    "chineke": ("God the Creator", "The God who creates", None),
    "chi": ("personal god, spirit, destiny", "Guardian spirit of each person", None),
    "mmuo": ("spirit", "Spiritual beings", None),
    "ndi ichie": ("ancestors", "The ancestral spirits", None),
    "ala": ("earth goddess, land", "Mother Earth - goddess of morality", None),
    "amadioha": ("god of thunder and justice", "Sky deity who enforces justice", None),
    "ikenga": ("god of achievement, strength", "Horned god of human endeavor", None),
    "agwu": ("spirit of divination and healing", "Spirit of diviners and healers", None),
    "ofo": ("symbol of truth and justice", "Sacred staff of authority", None),
    "ihu": ("life force, vital principle", "The animating force", None),
    "ndu": ("life", "Living existence", None),
    "onwu": ("death", "Transition from life", None),
    "reincarnation": ("ilo uwa", "Coming back to the world", None),
    "ilo uwa": ("reincarnation", "Returning to earthly life", None),
    "ekpere": ("prayer", "Communication with God", None),
    "aja": ("sacrifice, offering", "Ritual offering", None),
    "dibia": ("healer, diviner, priest", "Traditional spiritual practitioner", None),
    "eze": ("king, ruler", "Traditional ruler", None),
    "obi": ("heart", "Seat of emotions and soul", None),
    "udo": ("peace", "Tranquility and harmony", None),
    "ihunanya": ("love", "Deep affection", None),
    "ezi okwu": ("truth", "What is genuine", None),
    "obi oma": ("good heart, kindness", "Benevolence", None),
    "aka nri aka ekpe": ("left and right hand, balance", "Complementary duality", None),
    "igwe": ("sky, heaven", "The realm above", None),
    "uwa": ("world", "The physical world", None),
    "mmiri": ("water", "Life-giving element", None),
    "oku": ("fire", "Transformative element", None),
    "anyanwu": ("sun", "Source of light - also a deity", None),
    "onwa": ("moon", "Night light", None),
    "kpakpando": ("star", "Celestial light", None),
    "nna": ("father", "Male parent", None),
    "nne": ("mother", "Female parent", None),
    "nwanne": ("sibling", "Brother or sister", None),
    "nwanne nwoke": ("brother", "Male sibling", None),
    "nwanne nwanyi": ("sister", "Female sibling", None),
    "ezinulo": ("family", "Family unit", None),
    "obodo": ("community, town", "Settlement", None),
    "umu": ("children", "Offspring", None),
    "okenye": ("elder", "Respected elder", None),
    "nno": ("welcome", "Greeting for guests", None),
    "kedu": ("how are you, hello", "Common greeting", None),
    "o di mma": ("it is good, fine", "Response to greeting", None),
    "daalu": ("thank you", "Expression of gratitude", None),
    "ndewo": ("greetings", "Formal greeting", None),
    "ka omesia": ("goodbye, see you later", "Farewell", None),
    "isee": ("amen, so be it", "Affirmation", None),
    "ogini": ("oneness, unity", "Being one", None),
    "umunna": ("kinship, brotherhood", "Patrilineal relatives", None),
    "ubuntu igbo": ("nkwurịta ọnụ", "Unity in diversity", None),
    "omenala": ("tradition, custom", "Traditional ways", None),
    "odinani": ("traditional religion", "Indigenous spiritual practice", None),
    "akwukwo nso": ("Holy Bible", "Sacred scriptures", None),
    "jesu kristi": ("Jesus Christ", "The Messiah", None),
    "mmuo nso": ("Holy Spirit", "The divine Spirit", None),
}

NIGERIAN_PHRASES: Dict[str, Tuple[str, str]] = {
    "ase o": (
        "so be it, amen (Yoruba)",
        "TEACHING: Affirmation of divine power"
    ),
    "modupe o": (
        "I give thanks, thank you (Yoruba)",
        "Expression of deep gratitude"
    ),
    "oluwa a bukun fun o": (
        "may God bless you (Yoruba)",
        "Blessing spoken to another"
    ),
    "allah ya ba da albarka": (
        "may God bless (Hausa)",
        "Blessing spoken to another"
    ),
    "allah ya kiyaye": (
        "may God protect (Hausa)",
        "Prayer for protection"
    ),
    "na gode wa allah": (
        "thank God (Hausa)",
        "Expression of gratitude to God"
    ),
    "chukwu gozie gi": (
        "God bless you (Igbo)",
        "Blessing spoken to another"
    ),
    "chineke dalu": (
        "thank God, God be praised (Igbo)",
        "Expression of gratitude to God"
    ),
    "iwa lewa": (
        "character is beauty (Yoruba)",
        "TEACHING: Good character is true beauty"
    ),
    "ori ire": (
        "blessed destiny (Yoruba)",
        "TEACHING: A head/consciousness aligned with good fortune"
    ),
    "igwe ka ala": (
        "heaven is greater than earth (Igbo)",
        "TEACHING: Spiritual realm supersedes physical"
    ),
    "onye aghala nwanne ya": (
        "be your brother's keeper (Igbo)",
        "TEACHING: Look after your community"
    ),
    "egbe bere ugo bere": (
        "let the kite perch, let the eagle perch (Igbo)",
        "TEACHING: Live and let live - tolerance proverb"
    ),
    "aiki shi ne ibada": (
        "work is worship (Hausa)",
        "TEACHING: Honest labor is sacred"
    ),
}


def normalize_nigerian(text: str) -> str:
    """Normalize Nigerian text for lookup."""
    return ' '.join(text.lower().strip().split())


def lookup_nigerian_word(word: str, use_fuzzy: bool = True) -> Optional[Dict]:
    """Look up a Nigerian word in the lexicon."""
    from fuzzy_match import fuzzy_lookup
    
    normalized = normalize_nigerian(word)
    
    for lang_name, lexicon in [("yoruba", YORUBA_LEXICON), ("hausa", HAUSA_LEXICON), ("igbo", IGBO_LEXICON)]:
        if normalized in lexicon:
            meaning, context, scroll_ref = lexicon[normalized]
            return {
                "word": word,
                "meaning": meaning,
                "context": context,
                "scroll_reference": scroll_ref,
                "source": f"nigerian_lexicon_{lang_name}",
                "language": lang_name,
                "fuzzy_match": False
            }
        
        no_spaces = normalized.replace(' ', '')
        if no_spaces in lexicon:
            meaning, context, scroll_ref = lexicon[no_spaces]
            return {
                "word": word,
                "meaning": meaning,
                "context": context,
                "scroll_reference": scroll_ref,
                "source": f"nigerian_lexicon_{lang_name}",
                "language": lang_name,
                "fuzzy_match": False
            }
    
    if use_fuzzy:
        for lang_name, lexicon in [("yoruba", YORUBA_LEXICON), ("hausa", HAUSA_LEXICON), ("igbo", IGBO_LEXICON)]:
            fuzzy_result = fuzzy_lookup(word, lexicon, threshold=0.75)
            if fuzzy_result:
                matched_key, value, similarity = fuzzy_result
                meaning, context, scroll_ref = value
                return {
                    "word": word,
                    "meaning": meaning,
                    "context": context,
                    "scroll_reference": scroll_ref,
                    "source": f"nigerian_lexicon_{lang_name}",
                    "language": lang_name,
                    "fuzzy_match": True,
                    "corrected_to": matched_key
                }
    
    return None


def lookup_nigerian_phrase(phrase: str) -> Optional[Dict]:
    """Look up a Nigerian phrase."""
    normalized = normalize_nigerian(phrase)
    
    if normalized in NIGERIAN_PHRASES:
        meaning, teaching = NIGERIAN_PHRASES[normalized]
        return {
            "phrase": phrase,
            "meaning": meaning,
            "teaching": teaching,
            "source": "nigerian_lexicon"
        }
    
    for stored_phrase, (meaning, teaching) in NIGERIAN_PHRASES.items():
        if stored_phrase in normalized or normalized in stored_phrase:
            return {
                "phrase": phrase,
                "meaning": meaning,
                "teaching": teaching,
                "source": "nigerian_lexicon"
            }
    
    return None


def annotate_nigerian_query(query: str) -> Dict:
    """Analyze a query for Nigerian words/phrases."""
    annotations = []
    normalized_query = normalize_nigerian(query)
    
    phrase_result = lookup_nigerian_phrase(query)
    if phrase_result:
        annotations.append(phrase_result)
    
    full_word_result = lookup_nigerian_word(query)
    if full_word_result:
        annotations.append(full_word_result)
    
    words = normalized_query.split()
    for word in words:
        clean_word = word.strip('.,!?;:')
        word_result = lookup_nigerian_word(clean_word)
        if word_result:
            annotations.append(word_result)
    
    return {
        "original_query": query,
        "annotations": annotations,
        "has_nigerian_content": len(annotations) > 0
    }


def get_nigerian_context_for_prompt(query: str) -> Optional[str]:
    """Generate Nigerian lexical context for AI prompt."""
    result = annotate_nigerian_query(query)
    
    if not result["has_nigerian_content"]:
        return None
    
    lines = ["[NIGERIAN LEXICAL CONTEXT]"]
    lines.append("The user's query contains Nigerian words (Yoruba/Hausa/Igbo). Here are their meanings:")
    
    seen = set()
    for ann in result["annotations"]:
        word = ann.get("word") or ann.get("phrase", "")
        if word.upper() in seen:
            continue
        seen.add(word.upper())
        
        meaning = ann.get("meaning", "")
        lang = ann.get("language", "").upper()
        lang_tag = f" [{lang}]" if lang else ""
        lines.append(f"• {word.upper()}{lang_tag}: {meaning}")
        
        if ann.get("teaching"):
            lines.append(f"  TEACHING: {ann['teaching']}")
        elif ann.get("context"):
            lines.append(f"  CONTEXT: {ann['context']}")
        
        if ann.get("scroll_reference"):
            lines.append(f"  REFERENCE: {ann['scroll_reference']}")
    
    lines.append("")
    lines.append("IMPORTANT: Use these Nigerian language meanings to enrich your response.")
    lines.append("Embrace the rich spiritual traditions of Nigeria - Yoruba, Hausa, and Igbo wisdom.")
    
    return "\n".join(lines)
