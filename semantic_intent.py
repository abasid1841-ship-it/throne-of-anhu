# semantic_intent.py
"""
SEMANTIC INTENT · Understanding Question Context for the Throne of Anhu

Uses existing embedding infrastructure (knowledge_store, third_mind) to understand
what a question is ABOUT, not just what keywords it contains.

Example: "Is it bad to cry" → understands this is about emotions/balance/tears,
not just looking for the word "cry" in verses.
"""

from __future__ import annotations

from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict

# Use existing semantic search infrastructure
try:
    from knowledge_store import search_similar_verses
    HAS_KNOWLEDGE_STORE = True
except ImportError:
    HAS_KNOWLEDGE_STORE = False
    search_similar_verses = None

try:
    from third_mind import search_third_mind
    HAS_THIRD_MIND = True
except ImportError:
    HAS_THIRD_MIND = False
    search_third_mind = None


# Law scroll mappings for semantic matching
LAW_SCROLL_TOPICS = {
    "LOT-01-01": ["identity", "self", "purpose", "calling", "who am i", "name", "soul"],
    "LOT-02-01": ["balance", "emotion", "feeling", "cry", "tears", "anger", "fear", "fire", "water", "air", "earth", "pain", "hurt", "sad", "grief"],
    "LOT-03-01": ["judgment", "truth", "lie", "deception", "justice", "verdict", "witness"],
    "LOT-04-01": ["return", "karma", "consequence", "reap", "sow", "action", "reaction"],
    "LOT-05-01": ["worship", "prayer", "pray", "sacred", "ritual", "devotion", "chinamoto"],
    "LOT-06-01": ["covenant", "promise", "oath", "agreement", "blood", "seal", "vow"],
    "LOT-07-01": ["name", "zita", "power", "naming", "word", "speak", "declare"],
    "LOT-08-01": ["temple", "body", "dwelling", "house", "vessel", "flesh", "spirit"],
    "LOT-09-01": ["seed", "child", "children", "inherit", "lineage", "generation", "offspring"],
    "LOT-10-01": ["crown", "king", "queen", "throne", "glory", "reign", "kingdom", "royal"],
}


def get_semantic_verses(question: str, top_k: int = 12) -> List[Dict[str, Any]]:
    """
    Get semantically similar verses using embedding search.
    Returns verses that are contextually relevant to the question's meaning.
    """
    if not HAS_KNOWLEDGE_STORE or not search_similar_verses:
        return []
    
    try:
        results = search_similar_verses(question, top_k=top_k)
        return results or []
    except Exception as e:
        print(f"[SEMANTIC INTENT] knowledge_store error: {e}")
        return []


def get_semantic_context(question: str, top_k: int = 8) -> Tuple[List[Any], List[Any]]:
    """
    Get both scroll verses and vault notes semantically related to the question.
    Uses third_mind if available.
    """
    scroll_hits = []
    vault_hits = []
    
    if HAS_THIRD_MIND and search_third_mind:
        try:
            scroll_hits, vault_hits = search_third_mind(
                question,
                top_k_scroll=top_k,
                top_k_vault=4,
                min_score=0.25,
            )
        except Exception as e:
            print(f"[SEMANTIC INTENT] third_mind error: {e}")
    
    return scroll_hits, vault_hits


def extract_topics_from_verses(verses: List[Dict[str, Any]]) -> List[str]:
    """
    Extract dominant topics/themes from semantically matched verses.
    Analyzes the text of matched verses to identify key concepts.
    """
    if not verses:
        return []
    
    topic_keywords = {
        "tears": ["tear", "cry", "weep", "crying", "weeping"],
        "water": ["water", "rain", "river", "ocean", "sea", "nyu"],
        "heart": ["heart", "moyo", "soul"],
        "balance": ["balance", "harmony", "element", "fire", "water", "air", "earth"],
        "memory": ["memory", "remember", "bones", "ancestor"],
        "identity": ["identity", "name", "who am i", "self", "soul"],
        "prayer": ["pray", "prayer", "worship", "sacred"],
        "spirit": ["spirit", "mweya", "breath", "ruach"],
        "seed": ["seed", "child", "birth", "womb", "offspring"],
        "judgment": ["judge", "judgment", "verdict", "law", "throne"],
        "mercy": ["mercy", "compassion", "forgive", "grace"],
        "peace": ["peace", "calm", "rest", "quiet", "harmony"],
    }
    
    topic_counts = defaultdict(int)
    
    for verse in verses:
        text = (verse.get("text") or "").lower()
        for topic, keywords in topic_keywords.items():
            for kw in keywords:
                if kw in text:
                    topic_counts[topic] += verse.get("score", 1.0)
                    break
    
    # Sort by score and return top topics
    sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
    return [topic for topic, _ in sorted_topics[:5]]


def infer_law_scroll_semantic(question: str, threshold: float = 0.3) -> Optional[str]:
    """
    Use semantic search to infer which Law scroll best matches the question's intent.
    Returns scroll_id if confidence is high enough, None otherwise.
    """
    verses = get_semantic_verses(question, top_k=16)
    if not verses:
        return None
    
    # Score each law scroll based on how well matched verses align with its topics
    scroll_scores = defaultdict(float)
    
    for verse in verses:
        text = (verse.get("text") or "").lower()
        verse_score = verse.get("score", 0.5)
        scroll_id = verse.get("scroll_id", "")
        
        # Direct match: if verse is from a law scroll
        if scroll_id.startswith("LOT-"):
            scroll_scores[scroll_id] += verse_score * 2
        
        # Topic match: check verse content against law scroll topics
        for law_id, topics in LAW_SCROLL_TOPICS.items():
            topic_matches = sum(1 for t in topics if t in text)
            if topic_matches > 0:
                scroll_scores[law_id] += verse_score * topic_matches * 0.5
    
    if not scroll_scores:
        return None
    
    best_scroll = max(scroll_scores, key=lambda k: scroll_scores[k])
    best_score = scroll_scores[best_scroll]
    
    # Return only if confidence is above threshold
    if best_score >= threshold:
        return best_scroll
    
    return None


def get_semantic_keywords(question: str, max_keywords: int = 8) -> List[str]:
    """
    Extract semantically-informed keywords by analyzing matched verses.
    These keywords reflect what the question is ABOUT, not just what words it contains.
    """
    verses = get_semantic_verses(question, top_k=12)
    if not verses:
        return []
    
    # Extract topics from matched verses
    topics = extract_topics_from_verses(verses)
    
    # Also extract key single words from high-scoring verse texts
    word_scores = defaultdict(float)
    stop_words = {
        "the", "and", "of", "to", "in", "a", "is", "that", "for", "it",
        "with", "as", "was", "on", "are", "be", "this", "which", "or",
        "an", "by", "from", "at", "not", "but", "have", "has", "had",
        "will", "would", "could", "should", "may", "might", "must",
        "i", "you", "he", "she", "they", "we", "who", "what", "when",
        "where", "why", "how", "all", "each", "every", "both", "few",
        "more", "most", "other", "some", "such", "no", "nor", "only",
        "own", "same", "so", "than", "too", "very", "just", "can",
    }
    
    for verse in verses[:8]:
        text = (verse.get("text") or "").lower()
        score = verse.get("score", 0.5)
        
        # Extract meaningful words
        words = [w.strip(".,;:!?\"'()[]{}") for w in text.split()]
        for word in words:
            if len(word) > 3 and word not in stop_words:
                word_scores[word] += score
    
    # Combine topics and high-scoring words
    sorted_words = sorted(word_scores.items(), key=lambda x: x[1], reverse=True)
    top_words = [w for w, _ in sorted_words[:max_keywords - len(topics)]]
    
    return topics + top_words


def get_witness_topics(question: str) -> List[str]:
    """
    Get topics for witness/source searching based on semantic understanding.
    Returns keywords that reflect the question's true intent.
    """
    semantic_keywords = get_semantic_keywords(question, max_keywords=8)
    
    if semantic_keywords:
        return semantic_keywords
    
    # Fallback: return normalized question
    return [question.lower().strip()]
