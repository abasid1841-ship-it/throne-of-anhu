"""
Hindi Lexicon - A vocabulary reference for understanding Hindi spiritual terms.

This lexicon covers Hindi/Sanskrit spiritual vocabulary commonly used in:
- Hindu traditions (Vedic, Bhakti, Yoga)
- Buddhist terms used in India
- General spiritual discourse in Hindi

Provides word meanings to help the AI correctly interpret Hindi spiritual terms.
"""

from typing import Optional, Dict, List, Tuple

HINDI_LEXICON: Dict[str, Tuple[str, str, Optional[str]]] = {
    "bhagwan": ("God, Lord", "The Supreme Being, the Blessed One", None),
    "ishwar": ("God, Supreme Lord", "The controller of all, God", None),
    "prabhu": ("Lord, Master", "Term of reverence for God or guru", None),
    "paramatma": ("Supreme Soul", "The universal soul, God within all", None),
    "brahman": ("Ultimate Reality", "The absolute, infinite consciousness", None),
    "atman": ("soul, self", "The individual soul, inner self", None),
    "jivatma": ("living soul", "The embodied soul in a body", None),
    "moksha": ("liberation, freedom", "Release from the cycle of rebirth", None),
    "mukti": ("liberation, salvation", "Freedom from bondage", None),
    "nirvana": ("liberation, extinction of ego", "Complete freedom and peace", None),
    "samsara": ("cycle of rebirth", "The wheel of birth and death", None),
    "karma": ("action, deed", "The law of cause and effect", None),
    "dharma": ("duty, righteousness, cosmic order", "One's sacred duty and path", None),
    "punarjanma": ("rebirth, reincarnation", "Taking birth again", None),
    "avatar": ("incarnation, descent", "Divine being taking human form", None),
    "deva": ("god, divine being", "Celestial beings, deities", None),
    "devi": ("goddess", "Divine feminine, goddess", None),
    "shakti": ("power, energy", "Divine feminine energy, cosmic power", None),
    "prana": ("life force, breath", "Vital energy that sustains life", None),
    "kundalini": ("serpent energy", "Spiritual energy at base of spine", None),
    "chakra": ("wheel, energy center", "Energy centers in the body", None),
    "mantra": ("sacred sound, hymn", "Sacred words or phrases for meditation", None),
    "om": ("sacred syllable", "The primordial sound of creation", None),
    "aum": ("sacred syllable", "Same as Om, the cosmic vibration", None),
    "namaste": ("I bow to you", "Greeting honoring the divine in another", None),
    "namaskar": ("salutation", "Respectful greeting and bow", None),
    "pranam": ("prostration, bow", "Deep respectful greeting", None),
    "guru": ("teacher, spiritual master", "One who leads from darkness to light", None),
    "sadguru": ("true teacher", "An enlightened spiritual master", None),
    "shishya": ("disciple, student", "A devoted student of a guru", None),
    "ashram": ("hermitage, spiritual community", "Place of spiritual practice", None),
    "satsang": ("company of truth", "Gathering for spiritual discourse", None),
    "bhakti": ("devotion, love", "Loving devotion to God", None),
    "puja": ("worship, ritual", "Devotional worship ceremony", None),
    "aarti": ("light offering", "Ritual of waving light before deity", None),
    "darshan": ("sacred seeing", "Beholding the divine or a holy person", None),
    "prasad": ("blessed food", "Food offered to deity then shared", None),
    "seva": ("selfless service", "Service without expectation of reward", None),
    "yoga": ("union, discipline", "Path of union with the divine", None),
    "dhyana": ("meditation", "Deep contemplation and focus", None),
    "samadhi": ("absorption, enlightenment", "State of deep meditative union", None),
    "tapas": ("austerity, spiritual heat", "Disciplined spiritual practice", None),
    "vairagya": ("detachment, renunciation", "Freedom from worldly attachments", None),
    "ahimsa": ("non-violence", "The principle of not harming any being", None),
    "satya": ("truth", "Truthfulness in thought, word, and deed", None),
    "karuna": ("compassion", "Deep empathy and kindness", None),
    "prema": ("divine love", "Pure, unconditional love", None),
    "shanti": ("peace", "Inner and outer peace", None),
    "ananda": ("bliss, joy", "Spiritual bliss and happiness", None),
    "sukha": ("happiness, comfort", "Worldly happiness", None),
    "dukha": ("suffering, pain", "Worldly suffering and sorrow", None),
    "maya": ("illusion", "The illusory nature of the world", None),
    "leela": ("divine play", "The cosmic play of God", None),
    "kripa": ("grace, mercy", "Divine grace and blessing", None),
    "ashirwad": ("blessing", "Blessing from elder or guru", None),
    "swami": ("master, lord", "Title for a renunciate or master", None),
    "rishi": ("sage, seer", "Ancient enlightened seer", None),
    "muni": ("sage, silent one", "A contemplative sage", None),
    "sadhu": ("holy man", "A renunciate dedicated to God", None),
    "sant": ("saint", "A holy person, devotee of God", None),
    "yogi": ("practitioner of yoga", "One who practices yoga", None),
    "bhagavad": ("divine, blessed", "Of or relating to God", None),
    "gita": ("song", "Sacred song, often refers to Bhagavad Gita", None),
    "veda": ("knowledge", "Sacred scriptures, divine knowledge", None),
    "upanishad": ("sitting near, secret teaching", "Philosophical scriptures", None),
    "purana": ("ancient tales", "Ancient mythological scriptures", None),
    "stotra": ("hymn of praise", "Devotional hymns", None),
    "sloka": ("verse", "A verse from scripture", None),
    "sutra": ("thread, aphorism", "Concise spiritual teachings", None),
    "japa": ("repetition", "Repetition of mantra or divine name", None),
    "kirtan": ("devotional singing", "Group singing of God's names", None),
    "bhajan": ("devotional song", "Spiritual song of praise", None),
    "hari": ("Lord Vishnu/Krishna", "Name of God, remover of sins", None),
    "ram": ("Lord Rama", "Avatar of Vishnu, ideal man", None),
    "krishna": ("Lord Krishna", "Avatar of Vishnu, divine cowherd", None),
    "shiva": ("Lord Shiva", "The auspicious one, destroyer/transformer", None),
    "vishnu": ("Lord Vishnu", "The preserver, all-pervading", None),
    "brahma": ("Lord Brahma", "The creator", None),
    "ganesh": ("Lord Ganesha", "Remover of obstacles", None),
    "hanuman": ("Lord Hanuman", "Devotee of Rama, symbol of devotion", None),
    "lakshmi": ("Goddess Lakshmi", "Goddess of wealth and fortune", None),
    "saraswati": ("Goddess Saraswati", "Goddess of knowledge and arts", None),
    "durga": ("Goddess Durga", "The invincible goddess", None),
    "kali": ("Goddess Kali", "Goddess of time and transformation", None),
    "maa": ("mother", "Mother, often refers to Divine Mother", None),
    "pitaji": ("father", "Father, also used for God as Father", None),
    "janam": ("birth", "Taking birth in the world", None),
    "mrityu": ("death", "Death of the physical body", None),
    "swarga": ("heaven", "The celestial realm", None),
    "narak": ("hell", "Lower realms of suffering", None),
    "lok": ("world, realm", "A plane of existence", None),
    "pap": ("sin", "Wrong action that brings karma", None),
    "punya": ("merit, virtue", "Good action that brings positive karma", None),
    "jai": ("victory, hail", "Exclamation of victory or praise", None),
    "har har mahadev": ("hail Lord Shiva", "Invocation to Lord Shiva", None),
    "om namah shivaya": ("I bow to Shiva", "Sacred mantra to Lord Shiva", None),
    "hare krishna": ("O Lord Krishna", "Invocation to Lord Krishna", None),
    "ram ram": ("greeting using Ram's name", "Common greeting invoking Lord Rama", None),
    "radhe radhe": ("O Radha", "Greeting invoking Radha, beloved of Krishna", None),
}

def get_hindi_context(text: str) -> str:
    """
    Analyze text for Hindi/Sanskrit spiritual terms and return context.
    """
    if not text:
        return ""
    
    lower_text = text.lower()
    found_terms = []
    
    for term, (meaning, explanation, _) in HINDI_LEXICON.items():
        if term in lower_text:
            found_terms.append(f"• {term}: {meaning} — {explanation}")
    
    if found_terms:
        context = "HINDI LEXICON CONTEXT:\n"
        context += "The following Hindi/Sanskrit spiritual terms appear in the query:\n"
        context += "\n".join(found_terms[:10])
        context += "\n\nUse these meanings to understand the spiritual context of the question."
        return context
    
    return ""


def get_hindi_greeting() -> str:
    """Return appropriate Hindi greeting."""
    return "Namaste, pyare sadhak (beloved seeker)"


def format_hindi_response_style() -> str:
    """Return style guide for Hindi responses."""
    return """
When responding in Hindi:
- Use Devanagari script when possible, or romanized Hindi
- Begin with "Namaste" or "Pranam"
- Use respectful forms like "aap" (आप) not "tum"
- Include terms like Prabhu (Lord), Bhagwan (God), Atma (soul)
- Reference concepts like karma, dharma, moksha naturally
- End with blessings like "Bhagwan aapko ashirwad de" (God bless you)
- Speak with the warmth of a loving guru
"""
