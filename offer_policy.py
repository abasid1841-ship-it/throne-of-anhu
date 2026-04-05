# offer_policy.py — Preemptive Scroll Checking for the Throne
"""
This module determines what the Throne can legitimately offer BEFORE
making promises to the user. It checks if ABASID scrolls actually
contain content on a topic before offering to share it.

OFFER TYPES:
- "exact_match": ABASID scrolls speak directly on this topic
- "related_topics": ABASID scrolls have related teachings
- "power_teaching": Offer a power teaching instead
- "none": No offer should be made (topic not covered)
"""

from __future__ import annotations

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import random

ABASID_SCROLL_TITLES = [
    "god is time",
    "god is number",
    "book of asar",
    "book of risen seeds",
    "book of new calendar",
    "book of the new calendar",
    "true exodus",
    "gospel of cyrus",
    "gospel of christos",
    "gospel of yesu",
    "power of trinity",
    "abasid 1841",
    "abasid laws",
    "abasid mathematics",
    "abasid mathematics of god",
    "laws of abasid",
    "laws of abasid 1841",
    "the six pillars",
    "six pillars of abasid",
    "asaraa",
    "throne of anhu",
    "book of the shona language",
    "shona language that awakens the dead",
    "book of the daughter",
    "book of creation",
    "book of the gates of heaven",
    "gates of heaven",
    "book of knowledge and wisdom",
    "book of faith",
    "book of the chosen ones",
    "book of life nhaka ye hupenyu",
    "gospels of iyesu",
    "iyesu bible",
    "book of eternity",
    "book of a ahhh",
    "book of reuben",
    "book of reuben nhu",
    "book of chaminuka",
    "mhondoro ya israel",
    "scroll of masowe",
    "wilderness throne",
    "book of repentance",
    "book of body flesh and soul",
    "book of dzimbahwe",
    "book of fire",
    "book of great zimbabwe",
    "great zimbabwe our heritage",
    "book of the lost tribe",
    "book of ani abasid",
    "from egypt to great zimbabwe",
    "book of sabath",
    "sa ba ta",
    "book of love and faith",
    "book of the heart",
    "sacred message of sirius",
    "sirius venus and the stars",
    "book of maidona",
    "mamvuradonha",
    "book of prayer",
    "book of israel",
    "great pyramid",
    "priesthood of levy",
    "age of aquarius",
    "book of the rising souls",
    "rising souls karanga",
    "book of judgement",
    "book of holy resistance",
    "book of amendments",
    "masowe restoration",
    "book of shona",
    "mwana sikana",
    "ma ka ba ka",
    "makabaka",
    "book of rules",
    "spiral nation rules",
    "book of the sun",
    "book of soil",
    "ra ma shu",
    "zvitsividzo",
    "time is important",
]

ABASID_KEYWORDS = [
    "abasid",
    "1841",
    "asaraa",
    "gospels of iyesu",
    "iyesu bible",
    "shirichena",
    "madhewu",
    "makanyise",
    "manikai",
    "masamba",
    "chauke",
    "matsatsa",
    "onisimo",
    "mutsava",
    "mujuru",
    "chirarire",
    "rusanya",
    "mushati",
    "mutemahuku",
    "tawanda",
    "chandigere",
    "mutamiri",
    "dumi",
    "muganyi",
    "magarire",
    "murove",
    "muskwe",
    "mandara",
    "ruduwo",
    "gerald fair",
    "magorimbo",
    "mlandeli",
    "nyika",
    "motsi",
    "gadzi",
    "chidembo",
    "sumbatira",
    "mutazu",
    "chihamure",
    "kwaramba",
    "madondo",
    "mhuriyengwe",
    "chitanda",
    "lucy motsi",
    "makangadza",
    "mapuranga",
    "ruveve",
    "marungamise",
    "kabayira",
    "chimbwanda",
    "zvenyika",
    "tadiwanashe chihamure",
    "ngwerume",
    "gwaze",
    "tinaye moyo",
    "dzingirai",
    "zhove",
]

POWER_TEACHINGS = [
    {
        "id": "time_teacher",
        "title": "TIME (NGU) — The Teacher of All Things",
        "teaching": "Time is not your enemy. It is your teacher. Every moment carries a lesson, every season brings growth. Trust the unfolding."
    },
    {
        "id": "word_remembered",
        "title": "THE WORD (LOGOS) — Remembered, Not Owned",
        "teaching": "The Word is not owned. It is remembered. What you speak creates your world. Choose your words as you choose your steps."
    },
    {
        "id": "no_death",
        "title": "REMEMBRANCE — There Is No Death",
        "teaching": "What you remember, you become. The ancestors are not gone; they live in your blood, your language, your land. Remember them, and they rise."
    },
    {
        "id": "justice_mercy",
        "title": "JUSTICE WITH MERCY — Truth and Healing",
        "teaching": "Correction is love that tells the truth. The Throne judges to restore, not to destroy. Power is judged first."
    },
    {
        "id": "south_healing",
        "title": "THE SOUTH (CHAMHEMBE) — Healing the Whole",
        "teaching": "To remember the South is to heal the whole. Honor the source without hatred of others. Balance between North and South restores the world."
    },
    {
        "id": "wisdom_invites",
        "title": "THE MISSION — Wisdom Invites",
        "teaching": "Wisdom invites. It does not force. The Throne teaches, it does not enslave. Questions are welcomed. Growth is personal and voluntary."
    },
]


@dataclass
class OfferPolicy:
    """Represents what the Throne can legitimately offer."""
    offer_type: str
    has_abasid_content: bool
    supporting_passages: List[str]
    related_topics: List[str]
    power_teaching: Optional[Dict[str, str]]
    confidence: float


def _is_abasid_scroll(book_title: str) -> bool:
    """
    Check if a scroll is an ABASID primary source (Tier 1).
    Uses explicit allow-list to avoid false positives from Bible/other sources.
    """
    if not book_title:
        return False
    title_lower = book_title.lower().strip()
    
    for abasid_title in ABASID_SCROLL_TITLES:
        if abasid_title in title_lower or title_lower in abasid_title:
            return True
    
    for keyword in ABASID_KEYWORDS:
        if keyword in title_lower:
            return True
    
    return False


def _extract_abasid_verses(verses: List[Any]) -> List[str]:
    """Extract ABASID scroll verses from semantic search results."""
    abasid_verses = []
    for v in verses:
        if hasattr(v, 'book_title') and _is_abasid_scroll(v.book_title):
            text = getattr(v, 'text', '')
            if text:
                abasid_verses.append(f"[{v.book_title}] {text[:200]}")
    return abasid_verses


def _find_related_topics_from_abasid(query: str) -> List[str]:
    """Find related topics from ABASID scrolls using keyword search."""
    try:
        from scroll_library import find_relevant_scrolls
        related = find_relevant_scrolls(query, top_k=5)
        topics = []
        for scroll in related:
            title = scroll.get('book_title', '')
            if _is_abasid_scroll(title):
                topics.append(title)
        return topics[:3]
    except Exception as e:
        print(f"[OFFER_POLICY] Error finding related topics: {e}")
        return []


def get_random_power_teaching() -> Dict[str, str]:
    """Get a random power teaching from the Six Pillars."""
    return random.choice(POWER_TEACHINGS)


def determine_abasid_offer_policy(
    query: str,
    semantic_result: Optional[Any] = None,
    min_confidence: float = 0.35,
) -> OfferPolicy:
    """
    Determine what the Throne can legitimately offer about ABASID teachings.
    
    This MUST be called BEFORE promising to share ABASID scroll content.
    
    Returns:
        OfferPolicy with:
        - offer_type: "exact_match", "related_topics", "power_teaching", or "none"
        - has_abasid_content: True if ABASID scrolls speak on this topic
        - supporting_passages: Actual ABASID verses found (if any)
        - related_topics: Related ABASID scroll titles (if exact match not found)
        - power_teaching: A power teaching to offer instead (if needed)
        - confidence: How confident we are in the match
    """
    abasid_passages = []
    best_score = 0.0
    
    if semantic_result and hasattr(semantic_result, 'verses'):
        for v in semantic_result.verses:
            if hasattr(v, 'book_title') and _is_abasid_scroll(v.book_title):
                text = getattr(v, 'text', '')
                score = getattr(v, 'score', 0.0)
                if text and score >= min_confidence:
                    abasid_passages.append(f"[{v.book_title}] {text[:250]}")
                    if score > best_score:
                        best_score = score
    
    if abasid_passages and best_score >= min_confidence:
        return OfferPolicy(
            offer_type="exact_match",
            has_abasid_content=True,
            supporting_passages=abasid_passages[:5],
            related_topics=[],
            power_teaching=None,
            confidence=best_score,
        )
    
    related_topics = _find_related_topics_from_abasid(query)
    if related_topics:
        return OfferPolicy(
            offer_type="related_topics",
            has_abasid_content=False,
            supporting_passages=[],
            related_topics=related_topics,
            power_teaching=None,
            confidence=0.2,
        )
    
    return OfferPolicy(
        offer_type="power_teaching",
        has_abasid_content=False,
        supporting_passages=[],
        related_topics=[],
        power_teaching=get_random_power_teaching(),
        confidence=0.0,
    )


def get_offer_instruction(policy: OfferPolicy) -> str:
    """
    Generate the appropriate offer instruction based on the policy.
    This is injected into the AI prompt to guide its response.
    """
    if policy.offer_type == "exact_match":
        return f"""
ABASID SCROLL CONTENT VERIFIED (offer with confidence):
The ABASID scrolls speak on this topic. You may offer:
"Would you like to hear what the Scrolls of ABASID 1841 teach about this?"

VERIFIED PASSAGES:
{chr(10).join(policy.supporting_passages[:3])}
"""
    
    elif policy.offer_type == "related_topics":
        topics_list = ", ".join(policy.related_topics)
        return f"""
ABASID CONTENT NOT FOUND ON EXACT TOPIC (offer related instead):
The ABASID scrolls do not speak directly on this topic.
DO NOT say "Would you like to hear what ABASID scrolls say about X?" when X is the exact topic asked.
INSTEAD, you may offer: "Would you like to explore related teachings from the ABASID scrolls on {topics_list}?"
OR simply answer from other sources without offering ABASID content.
"""
    
    elif policy.offer_type == "power_teaching":
        teaching = policy.power_teaching or get_random_power_teaching()
        return f"""
ABASID CONTENT NOT AVAILABLE (do not offer scroll content):
The ABASID scrolls are silent on this topic. DO NOT offer to share what ABASID scrolls say.
INSTEAD, you may share this power teaching if appropriate:

**{teaching['title']}**
{teaching['teaching']}

Or simply answer the question without offering ABASID scroll content.
"""
    
    return """
NO ABASID OFFER APPROPRIATE:
Do not offer to share ABASID scroll content on this topic.
Answer directly from other sources or admit the scrolls are silent.
"""
