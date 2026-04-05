# semantic_witness.py
"""
SEMANTIC WITNESS SELECTOR · AI-Powered Witness Matching

Uses OpenAI to understand the question's true meaning and find witnesses
that are genuinely relevant to the topic, not just keyword matches.
"""

from __future__ import annotations

import json
import os
from typing import List, Dict, Any, Optional

from openai import OpenAI

from source_library import load_all_sources, SourceEntry


_client: Optional[OpenAI] = None


def _get_client() -> OpenAI:
    global _client
    if _client is not None:
        return _client

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")

    _client = OpenAI(api_key=api_key)
    return _client


def analyze_question_intent(question: str) -> Dict[str, Any]:
    """
    Use AI to understand what the question is truly about.
    Returns the main topic, related concepts, and what kind of witness would be relevant.
    """
    client = _get_client()

    system_prompt = """You analyze questions about spiritual/religious topics to find their TRUE SEMANTIC MEANING.

Your job is to understand what the person is REALLY asking about, then expand it to ALL related concepts.

CRITICAL RULES:
1. PRESERVE ALL PROPER NAMES AND PLACES - If the question mentions "Baba Johani", "Gandanzara", "Mugwambi", etc., these MUST appear in the main_topic or related_topics.
2. Expand concepts to their semantic equivalents:
   - "tithe" → giving to God, offering, first fruits
   - "marriage" → husband, wife, covenant, union
   - "Baba Johani" → Johane Masowe, Shoniwa, prophet, Masowe, 1914
   - "birth" → born, childhood, early life, signs before birth
   - "Gandanzara" → Mugwambi, Zimbabwe, birthplace

Given a question, extract:
1. main_topic: Include the SPECIFIC names/places from the question (e.g., "birth of Baba Johani at Gandanzara")
2. related_topics: ALL semantically related concepts INCLUDING proper names and their variations
3. desired_witness_type: What kind of scripture/scroll would be relevant
4. exclude_topics: Topics that might share keywords but are NOT what this person is asking about

Return ONLY valid JSON, no explanation."""

    user_message = f"Question: {question}"

    try:
        resp = client.chat.completions.create(
            model="gpt-4.1-mini",
            temperature=0.1,
            max_tokens=300,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        )

        content = resp.choices[0].message.content or "{}"
        content = content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()

        return json.loads(content)
    except Exception as e:
        print(f"[SEMANTIC WITNESS] analyze_question_intent error: {e}")
        return {
            "main_topic": question.lower(),
            "related_topics": [],
            "desired_witness_type": "general",
            "exclude_topics": [],
        }


def score_witness_relevance(
    question: str,
    question_intent: Dict[str, Any],
    witnesses: List[SourceEntry],
    max_to_score: int = 100,
) -> List[Dict[str, Any]]:
    """
    Use AI to score how relevant each witness is to the question's true intent.
    Returns witnesses with relevance scores.
    """
    if not witnesses:
        return []

    client = _get_client()

    witness_texts = []
    for i, w in enumerate(witnesses[:max_to_score]):
        ref = w.ref or w.tradition
        text = w.text[:200] if len(w.text) > 200 else w.text
        witness_texts.append(f"{i}. [{w.tradition}] {ref}: {text}")

    witnesses_block = "\n".join(witness_texts)

    main_topic = question_intent.get("main_topic", "")
    related = ", ".join(question_intent.get("related_topics", []))
    exclude = ", ".join(question_intent.get("exclude_topics", []))

    system_prompt = f"""You are evaluating witness/source relevance for a spiritual question.

Question: {question}
Main topic: {main_topic}
Related topics: {related}
Topics to EXCLUDE (not relevant even if keywords match): {exclude}

For each witness below, rate its RELEVANCE to the question on a scale of 0-10.
Only rate 7+ if the witness is DIRECTLY about the same topic as the question.
Rate 0 if the witness is about a completely different topic despite sharing keywords.

Return ONLY a JSON array of objects: [{{"index": 0, "score": 8, "reason": "brief reason"}}]
No explanation, just the JSON array."""

    try:
        resp = client.chat.completions.create(
            model="gpt-4.1-mini",
            temperature=0.1,
            max_tokens=2000,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Witnesses to evaluate:\n{witnesses_block}"},
            ],
        )

        content = resp.choices[0].message.content or "[]"
        content = content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()

        scores = json.loads(content)

        scored_witnesses = []
        for item in scores:
            idx = item.get("index", -1)
            score = item.get("score", 0)
            if 0 <= idx < len(witnesses) and score >= 5:
                scored_witnesses.append({
                    "witness": witnesses[idx],
                    "score": score,
                    "reason": item.get("reason", ""),
                })

        scored_witnesses.sort(key=lambda x: x["score"], reverse=True)
        return scored_witnesses

    except Exception as e:
        print(f"[SEMANTIC WITNESS] score_witness_relevance error: {e}")
        return [{"witness": w, "score": 5, "reason": ""} for w in witnesses[:8]]


ULTRA_GENERIC_TERMS = {
    "god", "lord", "spirit", "truth", "law", "laws", "light", "life", "love",
    "man", "men", "woman", "women", "people", "soul", "heart", "word", "words",
    "heaven", "earth", "day", "days", "time", "world", "name", "power",
    "thou", "thy", "thee", "shalt", "not", "shall", "unto", "upon",
}


def _extract_raw_keywords(question: str) -> List[str]:
    """
    Extract raw keywords from the question for combined search.
    These are used IN ADDITION to semantic terms, not as replacements.
    Filters out ultra-generic terms that match everything.
    """
    import re
    
    stopwords = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "must", "shall", "can", "need", "dare",
        "to", "of", "in", "for", "on", "with", "at", "by", "from", "as",
        "into", "through", "during", "before", "after", "above", "below",
        "and", "but", "if", "or", "because", "until", "while", "about",
        "what", "which", "who", "whom", "this", "that", "these", "those",
        "it", "its", "they", "them", "their", "we", "us", "our", "you",
        "your", "he", "him", "his", "she", "her", "i", "me", "my",
        "tell", "say", "said", "speak", "know", "think", "does",
    }
    
    q_lower = question.lower()
    tokens = re.split(r"[^a-zA-Z0-9]+", q_lower)
    keywords = [t for t in tokens if t and len(t) > 2 and t not in stopwords and t not in ULTRA_GENERIC_TERMS]
    
    return keywords[:8]


def _stratified_sample(candidates: List[SourceEntry], max_per_tradition: int = 25) -> List[SourceEntry]:
    """
    Sample candidates evenly from all traditions/sources to ensure
    newer scroll collections are represented fairly in scoring.
    """
    from collections import defaultdict
    
    by_tradition: Dict[str, List[SourceEntry]] = defaultdict(list)
    for c in candidates:
        by_tradition[c.tradition].append(c)
    
    result: List[SourceEntry] = []
    for tradition, entries in by_tradition.items():
        result.extend(entries[:max_per_tradition])
    
    print(f"[SEMANTIC WITNESS] Stratified: {len(by_tradition)} traditions, {len(result)} total candidates")
    return result


def get_semantic_witnesses(question: str, max_witnesses: int = 6) -> List[str]:
    """
    Main entry point: Get semantically relevant witnesses for a question.
    
    COMBINES semantic understanding with keyword matching:
    1. AI analyzes the question's true meaning (semantic intent)
    2. Raw keywords are also extracted from the question
    3. Candidates are gathered using BOTH semantic terms AND keywords
    4. AI scores all candidates based on semantic relevance
    5. Only witnesses that are truly relevant to the meaning are returned
    
    PRIORITY: Semantic understanding > Keywords
    If semantic analysis fails, keywords are used but scoring still applies.
    """
    if not question or not question.strip():
        return []

    # Step 1: Get semantic understanding of the question
    try:
        intent = analyze_question_intent(question)
        print(f"[SEMANTIC WITNESS] Intent: {intent.get('main_topic', 'unknown')}")
        print(f"[SEMANTIC WITNESS] Related: {intent.get('related_topics', [])}")
    except Exception as e:
        print(f"[SEMANTIC WITNESS] Intent analysis failed: {e}")
        intent = {"main_topic": question.lower(), "related_topics": []}

    all_sources = load_all_sources()
    if not all_sources:
        return []

    # Step 2: Build combined search terms (semantic + keywords)
    main_topic = (intent.get("main_topic") or "").lower()
    related_topics = [t.lower() for t in intent.get("related_topics", [])]
    semantic_terms = [main_topic] + related_topics
    
    # Also extract raw keywords from the question
    raw_keywords = _extract_raw_keywords(question)
    
    # Combine: semantic terms first (priority), then keywords
    # Deduplicate while preserving order
    all_search_terms: List[str] = []
    seen_terms = set()
    for term in semantic_terms + raw_keywords:
        term_clean = term.strip().lower()
        if term_clean and term_clean not in seen_terms:
            all_search_terms.append(term_clean)
            seen_terms.add(term_clean)
    
    print(f"[SEMANTIC WITNESS] Search terms: {all_search_terms[:10]}")

    # Step 3: Gather candidates using ALL search terms
    candidates: List[SourceEntry] = []
    seen_texts = set()

    for source in all_sources:
        text_lower = source.text.lower()
        ref_lower = (source.ref or "").lower()

        for term in all_search_terms:
            if term and (term in text_lower or term in ref_lower):
                text_key = source.text[:100]
                if text_key not in seen_texts:
                    candidates.append(source)
                    seen_texts.add(text_key)
                break

    # Fallback: if no candidates found, take first 50 sources
    if not candidates:
        print("[SEMANTIC WITNESS] No keyword matches, using fallback sources")
        for source in all_sources[:50]:
            text_key = source.text[:100]
            if text_key not in seen_texts:
                candidates.append(source)
                seen_texts.add(text_key)

    print(f"[SEMANTIC WITNESS] Found {len(candidates)} raw candidates")

    # Step 4: Stratified sampling to ensure ALL traditions are represented
    # This prevents the original 34 scrolls from dominating
    if len(candidates) > 50:
        candidates = _stratified_sample(candidates, max_per_tradition=25)

    # Step 5: If few candidates, return them all
    if len(candidates) <= max_witnesses:
        return [_format_witness(w) for w in candidates]

    # Step 6: AI scores candidates based on SEMANTIC RELEVANCE
    # This is where semantic understanding takes priority over keywords
    try:
        scored = score_witness_relevance(question, intent, candidates)
        if scored:
            top_witnesses = [item["witness"] for item in scored[:max_witnesses]]
            print(f"[SEMANTIC WITNESS] Returning {len(top_witnesses)} semantically scored witnesses")
            return [_format_witness(w) for w in top_witnesses]
        else:
            # Scoring returned nothing - use semantic-matched candidates first
            print("[SEMANTIC WITNESS] No high-scoring witnesses, using semantic matches")
            return [_format_witness(w) for w in candidates[:max_witnesses]]
    except Exception as e:
        print(f"[SEMANTIC WITNESS] Scoring failed: {e}")
        return [_format_witness(w) for w in candidates[:max_witnesses]]


def _format_witness(entry: SourceEntry) -> str:
    label = entry.tradition
    if entry.ref:
        label = f"{entry.tradition} – {entry.ref}"

    snippet = entry.text.strip().replace("\n", " ")
    if len(snippet) > 180:
        snippet = snippet[:177].rstrip() + "…"

    return f"{label}: {snippet}"
