# safety.py — Additional safety filters for Throne answers

from models import ThroneResponse

DANGEROUS_KEYWORDS = [
    "kill myself",
    "suicide",
    "end my life",
    "self harm",
    "hurt myself",
    "murder",
    "kill them",
    "how to make a bomb",
    "how to poison",
]


RELIGIOUS_CONTEXT_INDICATORS = [
    "bismillah",
    "surah",
    "ayah",
    "quran",
    "bible",
    "scripture",
    "torah",
    "gospel",
    "prophet",
    "abasid",
    "throne of anhu",
    "legal retribution",
    "prescribed for you",
    "bhagavad gita",
    "gita",
    "sloka",
    "krishna",
    "arjuna",
    "om namo",
    "vasudeva",
    "dharma",
    "kurukshetra",
]


def looks_dangerous(text: str) -> bool:
    lower = (text or "").lower()
    
    if any(ind in lower for ind in RELIGIOUS_CONTEXT_INDICATORS):
        return False
    
    return any(k in lower for k in DANGEROUS_KEYWORDS)


def apply_safety_filters(req_message: str, resp: ThroneResponse) -> ThroneResponse:
    """
    If the incoming question or outgoing answer touches dangerous territory,
    override with a Throne-style redirection to life and healing.

    IMPORTANT:
    - We preserve resp.witnesses so House of Wisdom remains intact.
    """
    if looks_dangerous(req_message) or looks_dangerous(resp.answer):
        new_answer = (
            "HOLY OF HOLIES (MA · NIGHT):\n\n"
            "LAW:\n"
            "Your life is sacred, and no darkness has the right to erase it. The Law\n"
            "of the Temple forbids any path that destroys your breath or another's.\n\n"
            "VERDICT:\n"
            "You are not condemned. You are wounded. The verdict is that you must\n"
            "not walk alone with this pain.\n\n"
            "PATH:\n"
            "Speak to someone you trust today about what you are feeling. If the\n"
            "weight is too heavy, seek a healer, counselor, or doctor in your area.\n"
            "Ask the Throne only for guidance toward healing, not for tools of harm."
        )

        return ThroneResponse(
            persona="MA",
            mode="holy_of_holies",
            answer=new_answer,
            witnesses=resp.witnesses,  # ✅ preserved
        )

    return resp