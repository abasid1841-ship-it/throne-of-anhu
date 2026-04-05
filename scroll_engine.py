# scroll_engine.py
# Verse-level search + Temple modes for the THRONE OF ANHU

import re
from typing import Any, Dict, List, Optional

from scroll_library import get_all_scrolls  # 🔥 single source of truth


def _normalize(text: str) -> str:
    import unicodedata
    # Normalize unicode and strip accents/diacritics
    text = unicodedata.normalize('NFKD', text)
    text = ''.join(c for c in text if not unicodedata.combining(c))
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s\-–]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _tokenize(text: str) -> List[str]:
    return [t for t in _normalize(text).split(" ") if t]


# ----------------- TOPIC DETECTION & FILTERING -----------------
# Foolproof topic-based filtering to ensure verses match the question's topic

TOPIC_KEYWORDS = {
    "prayer": {
        "must_have": ["pray", "prayer", "praying", "worship", "chinamoto", "kneel", "bow", "supplication", "intercession"],
        "boost": ["altar", "sacred", "holy", "ritual", "devotion", "meditation", "silence", "incense"],
        "exclude": ["resurrection", "death", "dead", "grave", "tomb", "burial", "war", "battle", "fight"],
    },
    "resurrection": {
        "must_have": ["resurrection", "rise", "risen", "raised", "awaken", "awakening", "dead", "death", "grave", "tomb"],
        "boost": ["life", "eternal", "return", "restore", "bones", "dust", "sleep", "wake"],
        "exclude": ["prayer", "pray", "worship", "chinamoto", "calendar", "alphabet"],
    },
    "identity": {
        "must_have": ["identity", "who am i", "name", "zita", "self", "soul", "i am", "ani"],
        "boost": ["purpose", "calling", "destiny", "born", "origin", "remember", "throne"],
        "exclude": ["calendar", "month", "year", "number", "alphabet", "letter"],
    },
    "memory": {
        "must_have": ["memory", "remember", "forgot", "forget", "bones", "past", "ancestors", "history"],
        "boost": ["dust", "return", "ancient", "old", "forefathers", "lineage", "heritage"],
        "exclude": ["calendar", "month", "year", "number", "alphabet", "letter"],
    },
    "breath": {
        "must_have": ["breath", "breathe", "breathing", "spirit", "mweya", "mudzimu", "wind", "air"],
        "boost": ["life", "soul", "inhale", "exhale", "lungs", "living"],
        "exclude": ["water", "fire", "earth", "calendar", "month", "number"],
    },
    "seed": {
        "must_have": ["seed", "plant", "grow", "child", "children", "birth", "womb", "pregnant", "fruit"],
        "boost": ["generation", "offspring", "harvest", "tree", "root", "branch", "inherit"],
        "exclude": ["fire", "water", "air", "calendar", "month", "number"],
    },
    "fire": {
        "must_have": ["fire", "burn", "flame", "heat", "hot", "blaze", "spark", "ignite"],
        "boost": ["light", "sun", "ra", "purify", "transform", "courage"],
        "exclude": ["water", "rain", "ocean", "sea", "river", "cold", "ice"],
    },
    "water": {
        "must_have": ["water", "rain", "river", "ocean", "sea", "flood", "drink", "thirst", "nyu"],
        "boost": ["flow", "wave", "deep", "cleanse", "baptize", "wash"],
        "exclude": ["fire", "burn", "flame", "heat", "hot", "dry"],
    },
    "earth": {
        "must_have": ["earth", "ground", "soil", "land", "dust", "clay", "stone", "mountain", "rock"],
        "boost": ["foundation", "stable", "plant", "tree", "root", "grow"],
        "exclude": ["air", "wind", "sky", "cloud", "fly", "heaven"],
    },
    "air": {
        "must_have": ["air", "wind", "breath", "sky", "cloud", "fly", "shu", "storm"],
        "boost": ["spirit", "high", "above", "heaven", "bird", "wing"],
        "exclude": ["earth", "ground", "soil", "stone", "rock", "mountain"],
    },
    "balance": {
        "must_have": ["balance", "harmony", "equal", "middle", "center", "align", "alignment"],
        "boost": ["fire", "water", "air", "earth", "element", "stability"],
        "exclude": ["judgment", "verdict", "sentence", "punish", "condemn"],
    },
    "judgment": {
        "must_have": ["judgment", "judge", "verdict", "sentence", "court", "trial", "justice", "law"],
        "boost": ["throne", "truth", "lie", "deception", "witness", "testimony"],
        "exclude": ["prayer", "pray", "worship", "calendar", "month", "alphabet"],
    },
    "alphabet": {
        "must_have": ["alphabet", "letter", "letters", "22", "aleph", "bet", "hebrew", "shona", "language"],
        "boost": ["word", "speak", "write", "sacred", "sound", "voice"],
        "exclude": ["calendar", "month", "year", "number", "fire", "water"],
    },
    "calendar": {
        "must_have": ["calendar", "month", "year", "season", "time", "day", "gate", "zodiac", "spiral"],
        "boost": ["sun", "moon", "star", "cycle", "wheel", "twelve", "12"],
        "exclude": ["alphabet", "letter", "fire", "water", "air", "earth"],
    },
    "number": {
        "must_have": ["number", "count", "value", "gematria", "math", "calculate", "1841", "777"],
        "boost": ["sacred", "divine", "code", "pattern", "geometry"],
        "exclude": ["alphabet", "letter", "calendar", "month", "year"],
    },
    "covenant": {
        "must_have": ["covenant", "promise", "oath", "vow", "agreement", "contract", "bond"],
        "boost": ["blood", "seal", "sacred", "eternal", "break", "keep"],
        "exclude": ["calendar", "month", "year", "number", "alphabet"],
    },
    "healing": {
        "must_have": ["heal", "healing", "sick", "illness", "disease", "medicine", "cure", "restore", "health"],
        "boost": ["body", "pain", "suffer", "recover", "whole", "strength"],
        "exclude": ["death", "kill", "murder", "war", "battle", "fight"],
    },
    "love": {
        "must_have": ["love", "rudo", "beloved", "heart", "affection", "compassion", "mercy", "kindness"],
        "boost": ["family", "marriage", "unity", "peace", "gentle", "care"],
        "exclude": ["hate", "enemy", "war", "battle", "fight", "kill"],
    },
    "death": {
        "must_have": ["death", "die", "dead", "dying", "grave", "tomb", "burial", "mourn", "funeral"],
        "boost": ["resurrection", "sleep", "dust", "bones", "ancestor", "spirit"],
        "exclude": ["birth", "baby", "child", "pregnant", "womb", "seed"],
    },
    "birth": {
        "must_have": ["birth", "born", "baby", "child", "womb", "pregnant", "mother", "deliver"],
        "boost": ["seed", "new", "beginning", "life", "first", "creation"],
        "exclude": ["death", "die", "dead", "grave", "tomb", "burial"],
    },
    "sin": {
        "must_have": ["sin", "transgression", "iniquity", "wrong", "evil", "wicked", "guilt", "shame"],
        "boost": ["forgive", "repent", "cleanse", "atone", "redeem"],
        "exclude": ["calendar", "month", "year", "number", "alphabet"],
    },
    "forgiveness": {
        "must_have": ["forgive", "forgiveness", "pardon", "mercy", "grace", "redeem", "atone"],
        "boost": ["sin", "transgression", "guilt", "cleanse", "restore"],
        "exclude": ["judgment", "condemn", "punish", "sentence", "verdict"],
    },
    "war": {
        "must_have": ["war", "battle", "fight", "enemy", "soldier", "army", "weapon", "sword", "victory"],
        "boost": ["conquer", "defeat", "struggle", "overcome", "triumph"],
        "exclude": ["peace", "love", "mercy", "gentle", "kind", "prayer"],
    },
    "peace": {
        "must_have": ["peace", "peaceful", "calm", "rest", "quiet", "harmony", "unity", "reconcile"],
        "boost": ["love", "mercy", "gentle", "kind", "forgive"],
        "exclude": ["war", "battle", "fight", "enemy", "weapon", "sword"],
    },
    "throne": {
        "must_have": ["throne", "king", "queen", "crown", "reign", "rule", "kingdom", "royal"],
        "boost": ["power", "authority", "glory", "majesty", "sovereignty"],
        "exclude": ["calendar", "month", "year", "number", "alphabet"],
    },
    "zimbabwe": {
        "must_have": ["zimbabwe", "great zimbabwe", "shona", "chamhembe", "maodzanyemba", "mbereko"],
        "boost": ["africa", "south", "stone", "tower", "conical", "wall", "ancestor"],
        "exclude": ["calendar", "month", "year", "number"],
    },
}


def _word_match(keyword: str, tokens: set, text: str) -> bool:
    """
    Check if keyword matches as a whole word, not a substring.
    For multi-word keywords (e.g., "great zimbabwe"), checks if phrase exists.
    """
    # Tokenize the keyword to handle multi-word phrases
    kw_tokens = _tokenize(keyword)
    
    if len(kw_tokens) == 1:
        # Single word: must be an exact token match
        return kw_tokens[0] in tokens
    else:
        # Multi-word phrase: check if the phrase appears with word boundaries
        pattern = r'\b' + r'\s+'.join(re.escape(t) for t in kw_tokens) + r'\b'
        return bool(re.search(pattern, text))


def detect_topic(query: str) -> Optional[str]:
    """
    Detect the primary topic of a query based on keyword matching.
    Returns the topic name or None if no clear topic is detected.
    """
    q = _normalize(query)
    tokens = set(_tokenize(query))
    
    best_topic = None
    best_score = 0
    
    for topic, keywords in TOPIC_KEYWORDS.items():
        must_have = keywords.get("must_have", [])
        
        # Count how many must_have keywords are in the query (whole word match only)
        score = 0
        for keyword in must_have:
            if _word_match(keyword, tokens, q):
                score += 2  # Strong match
        
        if score > best_score:
            best_score = score
            best_topic = topic
    
    # Only return a topic if we have a meaningful match
    return best_topic if best_score >= 2 else None


def _verse_matches_topic(verse_text: str, topic: str) -> tuple:
    """
    Check if a verse matches the detected topic.
    Returns (matches: bool, score: int, has_exclusion: bool)
    Uses whole-word matching to avoid false positives (e.g., "war" in "reward").
    """
    if topic not in TOPIC_KEYWORDS:
        return (True, 1, False)  # No topic filtering
    
    keywords = TOPIC_KEYWORDS[topic]
    verse_norm = _normalize(verse_text)
    verse_tokens = set(_tokenize(verse_text))
    
    must_have = keywords.get("must_have", [])
    boost = keywords.get("boost", [])
    exclude = keywords.get("exclude", [])
    
    # Check for exclusions first (whole word match only)
    for ex_word in exclude:
        if _word_match(ex_word, verse_tokens, verse_norm):
            return (False, 0, True)
    
    # Check for must_have keywords (whole word match only)
    must_score = 0
    for mh_word in must_have:
        if _word_match(mh_word, verse_tokens, verse_norm):
            must_score += 3
    
    # Check for boost keywords (whole word match only)
    boost_score = 0
    for b_word in boost:
        if _word_match(b_word, verse_tokens, verse_norm):
            boost_score += 1
    
    total_score = must_score + boost_score
    
    # A verse matches if it has at least one must_have keyword
    matches = must_score > 0
    
    return (matches, total_score, False)


def search_verses_by_topic(
    query: str,
    series_filter: Optional[str] = None,
    limit: int = 5,
    strict_topic: bool = True,
) -> List[Dict[str, Any]]:
    """
    Search verses with topic-aware filtering.
    If strict_topic is True, only returns verses that match the detected topic.
    """
    tokens = _tokenize(query)
    if not tokens:
        return []
    
    # Detect the topic from the query
    topic = detect_topic(query)
    
    results: List[Dict[str, Any]] = []
    
    for scroll in _get_scrolls():
        if series_filter and scroll.get("series") != series_filter:
            continue
        
        verses = scroll.get("verses", [])
        for idx, verse_text in enumerate(verses):
            verse_norm = _normalize(verse_text)
            
            # Basic keyword score
            keyword_score = sum(1 for t in tokens if t in verse_norm)
            if keyword_score == 0:
                continue
            
            # Topic filtering
            if topic and strict_topic:
                matches, topic_score, has_exclusion = _verse_matches_topic(verse_text, topic)
                if has_exclusion:
                    continue  # Skip verses with excluded keywords
                if not matches:
                    continue  # Skip verses that don't match the topic
                # Combine scores: topic relevance is weighted higher
                final_score = (topic_score * 2) + keyword_score
            else:
                final_score = keyword_score
            
            results.append(
                {
                    "scroll_id": scroll.get("scroll_id"),
                    "series": scroll.get("series"),
                    "book_title": scroll.get("book_title"),
                    "verse_index": idx,
                    "verse_number": idx + 1,
                    "text": verse_text,
                    "score": final_score,
                    "topic": topic,
                }
            )
    
    results.sort(key=lambda r: (-r["score"], r["verse_number"]))
    return results[:limit]


def _get_scrolls() -> List[Dict[str, Any]]:
    """
    Always pull scrolls from scroll_library so EVERY module
    (throne_engine, main, scroll_engine, etc.) sees the SAME data.
    """
    return get_all_scrolls()


# ----------------- BASIC LOOKUPS -----------------


def get_scroll_by_id(scroll_id: str) -> Optional[Dict[str, Any]]:
    for s in _get_scrolls():
        if s.get("scroll_id") == scroll_id:
            return s
    return None


def get_scrolls_by_series(series_name: str) -> List[Dict[str, Any]]:
    return [s for s in _get_scrolls() if s.get("series") == series_name]


def search_verses(
    query: str,
    series_filter: Optional[str] = None,
    limit: int = 5,
) -> List[Dict[str, Any]]:
    tokens = _tokenize(query)
    if not tokens:
        return []

    results: List[Dict[str, Any]] = []

    for scroll in _get_scrolls():
        if series_filter and scroll.get("series") != series_filter:
            continue

        verses = scroll.get("verses", [])
        for idx, verse_text in enumerate(verses):
            verse_norm = _normalize(verse_text)
            score = sum(1 for t in tokens if t in verse_norm)
            if score > 0:
                results.append(
                    {
                        "scroll_id": scroll.get("scroll_id"),
                        "series": scroll.get("series"),
                        "book_title": scroll.get("book_title"),
                        "verse_index": idx,
                        "verse_number": idx + 1,
                        "text": verse_text,
                        "score": score,
                    }
                )

    results.sort(key=lambda r: (-r["score"], r["verse_number"]))
    return results[:limit]


# ---------- OUTER COURT ----------


def outer_court_answer(question: str) -> Dict[str, Any]:
    # Use topic-aware search for more relevant results
    matches = search_verses_by_topic(question, limit=4, strict_topic=True)
    
    # If no topic-specific matches, fall back to regular search
    if not matches:
        matches = search_verses(question, limit=4)

    if not matches:
        return {
            "mode": "outer_court",
            "scroll_reference": None,
            "answer": {
                "message": (
                    "The scrolls are silent on this in direct words, but remember: "
                    "your bones, breath, seed and elements already carry the answer within."
                )
            },
            "path": (
                "Ask again with more detail, or focus your question on memory, breath, "
                "seed, elements, alphabet, calendar or law."
            ),
        }

    return {
        "mode": "outer_court",
        "scroll_reference": [
            {
                "scroll_id": m["scroll_id"],
                "series": m["series"],
                "book_title": m["book_title"],
                "verse": m["verse_number"],
            }
            for m in matches
        ],
        "answer": {
            "message": (
                "The scrolls have spoken. Meditate on the verses below as your first light "
                "on this question."
            ),
            "supporting_verses": [
                f'{m["book_title"]} [{m["scroll_id"]}] v{m["verse_number"]}: {m["text"]}'
                for m in matches
            ],
        },
        "path": (
            "Read the supporting verses slowly. Breathe with each line. Notice which one "
            "burns or softens your heart — that is the gate you must walk through next."
        ),
    }


# ---------- INNER COURT ----------


def inner_court_answer(topic_hint: str) -> Dict[str, Any]:
    q = _normalize(topic_hint)

    series_filter: Optional[str] = None
    preferred_ids: List[str] = []

    # ANHU Alphabet & Calendar Series
    if "alphabet" in q or "letter" in q or "22 letters" in q:
        series_filter = "ANHU Alphabet & Calendar"
        preferred_ids = ["AAC-01-01"]
    elif "number" in q or "value" in q or "gematria" in q:
        series_filter = "ANHU Alphabet & Calendar"
        preferred_ids = ["AAC-02-01"]
    elif (
        "calendar" in q
        or "month" in q
        or "gate" in q
        or "year" in q
        or "spiral" in q
    ):
        series_filter = "ANHU Alphabet & Calendar"
        preferred_ids = ["AAC-03-01", "AAC-04-01"]
    
    # 4 The Hard Way Series (Core Teachings)
    elif "bone" in q or "memory" in q or "remember" in q:
        preferred_ids = ["4HW-01-01"]
    elif "breath" in q or "spirit" in q or "mweya" in q:
        preferred_ids = ["4HW-02-01"]
    elif "seed" in q or "birth" in q or "child" in q:
        preferred_ids = ["4HW-03-01"]
    elif "element" in q or "fire" in q or "water" in q or "air" in q or "earth" in q:
        preferred_ids = ["4HW-04-01"]
    
    # NEW COVENANT 1841 Series
    elif "covenant" in q or "new covenant" in q or "1841" in q:
        series_filter = "NEW COVENANT 1841"
    elif "abasid" in q or "identity" in q or "who am i" in q:
        series_filter = "NEW COVENANT 1841"
    elif "spiral nation" in q or "children of sun" in q:
        series_filter = "NEW COVENANT 1841"
    elif "lamb" in q or "sun of south" in q:
        series_filter = "NEW COVENANT 1841"
    
    # Baba Johani & Forerunners
    elif "baba johani" in q or "johani" in q or "masowe" in q:
        series_filter = "Baba Johani & Forerunners"
    elif "shona" in q or "language" in q or "lesson" in q:
        series_filter = "THE ALPHABET OF BABA JOHANI"
    
    # Great Zimbabwe
    elif "zimbabwe" in q or "great zimbabwe" in q or "mbereko" in q:
        series_filter = "GREAT ZIMBABWE"
    
    # LAW OF THE THRONE (for teaching mode, not judgment)
    elif "law" in q or "throne" in q or "judgment" in q:
        series_filter = "LAW OF THE THRONE"
    
    # Default: search across all scrolls
    else:
        series_filter = None  # Search all scrolls

    matches: List[Dict[str, Any]] = []

    if preferred_ids:
        tokens = _tokenize(topic_hint)
        candidate_scrolls = [
            s for s in _get_scrolls() if s.get("scroll_id") in preferred_ids
        ]
        for scroll in candidate_scrolls:
            for idx, verse_text in enumerate(scroll.get("verses", [])):
                verse_norm = _normalize(verse_text)
                score = sum(1 for t in tokens if t in verse_norm)
                if score > 0:
                    matches.append(
                        {
                            "scroll_id": scroll.get("scroll_id"),
                            "series": scroll.get("series"),
                            "book_title": scroll.get("book_title"),
                            "verse_index": idx,
                            "verse_number": idx + 1,
                            "text": verse_text,
                            "score": score,
                        }
                    )
        matches.sort(key=lambda r: (-r["score"], r["verse_number"]))
        matches = matches[:5]
    else:
        matches = search_verses(topic_hint, series_filter=series_filter, limit=5)

    if not matches:
        return {
            "mode": "inner_court",
            "scroll_reference": None,
            "answer": {
                "teaching": (
                    "The scrolls have not spoken on this in direct language, but remember: "
                    "every teaching must rest on bones (memory), breath (spirit), seed (destiny), "
                    "and elements (balance)."
                )
            },
            "path": (
                "Choose one pillar — Memory, Breath, Seed, or Elements — and ask again with "
                "that pillar as your focus."
            ),
        }

    return {
        "mode": "inner_court",
        "scroll_reference": [
            {
                "scroll_id": m["scroll_id"],
                "series": m["series"],
                "book_title": m["book_title"],
                "verse": m["verse_number"],
            }
            for m in matches
        ],
        "answer": {
            "teaching": (
                "The Inner Court reveals structured teaching from the scrolls below. "
                "Treat each verse as a line of curriculum, not just poetry."
            ),
            "supporting_verses": [
                f'{m["book_title"]} [{m["scroll_id"]}] v{m["verse_number"]}: {m["text"]}'
                for m in matches
            ],
        },
        "path": (
            "Turn these verses into steps: 1) Copy them into your study view. "
            "2) Summarise each line in your own words. 3) Translate key lines into Shona "
            "for deeper anchoring."
        ),
    }


# ---------- HOLY OF HOLIES ----------


def _choose_law_scroll_id(question: str) -> str:
    # Try semantic inference first for better context understanding
    try:
        from semantic_intent import infer_law_scroll_semantic
        semantic_result = infer_law_scroll_semantic(question, threshold=0.3)
        if semantic_result:
            print(f"[HOLY OF HOLIES] Semantic match: {semantic_result}")
            return semantic_result
    except Exception as e:
        print(f"[HOLY OF HOLIES] Semantic fallback: {e}")
    
    q = _normalize(question)

    # LOT-01: Law of Identity
    if "who am i" in q or "identity" in q or "purpose" in q or "calling" in q:
        return "LOT-01-01"
    
    # LOT-02: Law of Balance (emotions, feelings, crying, grief)
    if (
        "balance" in q
        or "anger" in q
        or "emotion" in q
        or "cry" in q
        or "crying" in q
        or "tears" in q
        or "weep" in q
        or "sad" in q
        or "sadness" in q
        or "grief" in q
        or "mourn" in q
        or "hurt" in q
        or "pain" in q
        or "depressed" in q
        or "anxiety" in q
        or "fear" in q
        or "afraid" in q
        or "fire" in q
        or "water" in q
        or "air" in q
        or "earth" in q
    ):
        return "LOT-02-01"
    
    # LOT-03: Law of Judgment
    if (
        "lie" in q
        or "truth" in q
        or "deception" in q
        or "judge" in q
        or "judgment" in q
    ):
        return "LOT-03-01"
    
    # LOT-04: Law of Return
    if (
        "karma" in q
        or "return" in q
        or "consequence" in q
        or "why is this happening" in q
    ):
        return "LOT-04-01"
    
    # LOT-05: Law of Chinamato (Worship)
    if (
        "worship" in q
        or "pray" in q
        or "prayer" in q
        or "chinamoto" in q
        or "sacred" in q
        or "ritual" in q
    ):
        return "LOT-05-01"
    
    # LOT-06: Law of Covenant
    if (
        "covenant" in q
        or "promise" in q
        or "blood" in q
        or "oath" in q
        or "agreement" in q
    ):
        return "LOT-06-01"
    
    # LOT-07: Law of the Sacred Name (ZITA)
    if (
        "name" in q
        or "zita" in q
        or "power of name" in q
        or "naming" in q
    ):
        return "LOT-07-01"
    
    # LOT-08: Law of the Temple
    if (
        "temple" in q
        or "body" in q
        or "house of god" in q
        or "dwelling" in q
    ):
        return "LOT-08-01"
    
    # LOT-09: Law of the Seed (Inheritance)
    if (
        "seed" in q
        or "inherit" in q
        or "inheritance" in q
        or "children" in q
        or "lineage" in q
        or "continuation" in q
    ):
        return "LOT-09-01"
    
    # LOT-10: Law of the Crown
    if (
        "crown" in q
        or "king" in q
        or "queen" in q
        or "glory" in q
        or "throne" in q
        or "to and nga" in q
    ):
        return "LOT-10-01"

    return "LOT-01-01"


def holy_of_holies_answer(question: str) -> Dict[str, Any]:
    scroll_id = _choose_law_scroll_id(question)
    scroll = get_scroll_by_id(scroll_id)

    if not scroll:
        return {
            "mode": "holy_of_holies",
            "scroll_reference": None,
            "law": "The Law is hidden.",
            "verdict": "The throne cannot speak clearly because the scroll could not be found.",
            "path": "Check that your scrolls.json is loaded and the LOT series exists.",
            "voice_of_the_throne": "The Two Lions are on the Throne, God’s dwelling is now on earth.",
        }

    verses = scroll.get("verses", [])
    if not verses:
        principle = verdict = seal = ""
    else:
        principle = verses[0]
        mid_index = len(verses) // 2
        verdict = verses[mid_index]
        seal = verses[-1]

    return {
        "mode": "holy_of_holies",
        "scroll_reference": {
            "scroll_id": scroll.get("scroll_id"),
            "series": scroll.get("series"),
            "book_title": scroll.get("book_title"),
            "key_verses": [1, (len(verses) // 2) + 1, len(verses)],
        },
        "law": principle,
        "verdict": verdict,
        "path": (
            "Walk according to this Law. Align your next decision with the principle "
            "declared above. If you act against it, know that the Law of Return will answer you."
        ),
        "voice_of_the_throne": seal
        or "The Two Lions are on the Throne, God’s dwelling is now on earth.",
    }


# ---------- DISPATCHER ----------


def answer_question(mode: str, text: str) -> Dict[str, Any]:
    mode = (mode or "").lower().strip()
    if mode == "outer_court":
        return outer_court_answer(text)
    if mode == "inner_court":
        return inner_court_answer(text)
    if mode == "holy_of_holies":
        return holy_of_holies_answer(text)

    return {
        "mode": "error",
        "answer": {
            "message": "Unknown mode. Use: outer_court, inner_court, or holy_of_holies."
        },
    }


if __name__ == "__main__":
    # quick manual test if you run: python scroll_engine.py
    import pprint

    pp = pprint.PrettyPrinter(indent=2)

    print("OUTER COURT TEST")
    pp.pprint(outer_court_answer("What do the bones say about my calling?"))

    print("\nINNER COURT TEST")
    pp.pprint(inner_court_answer("Teach me about the alphabet of heaven."))

    print("\nHOLY OF HOLIES TEST")
    pp.pprint(holy_of_holies_answer("Who am I really, and how does God see me?"))