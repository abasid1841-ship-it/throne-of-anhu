"""
Tigrinya Lexicon for the Throne of Anhu
Provides spiritual vocabulary and context for Tigrinya-speaking seekers from Eritrea and Ethiopia.
"""

TIGRINYA_LEXICON = {
    "egziabher": {
        "meaning": "God, the Lord of the Universe",
        "scroll_context": "The One Source of all Light, Creator and Sustainer",
        "usage": "ኣግዚኣብሔር (Egziabher) - God is great"
    },
    "amlak": {
        "meaning": "God, deity",
        "scroll_context": "The divine presence that governs all",
        "usage": "ኣምላኽ (Amlak) - Our God"
    },
    "menfes": {
        "meaning": "Spirit, the Holy Spirit",
        "scroll_context": "The divine breath, the animating force",
        "usage": "መንፈስ ቅዱስ (Menfes Qidus) - Holy Spirit"
    },
    "birhan": {
        "meaning": "Light, illumination",
        "scroll_context": "RA, the eternal Light of truth",
        "usage": "ብርሃን (Birhan) - Light of the world"
    },
    "fiqri": {
        "meaning": "Love, divine love",
        "scroll_context": "The binding force of creation",
        "usage": "ፍቕሪ (Fiqri) - The love of God"
    },
    "selam": {
        "meaning": "Peace, greeting",
        "scroll_context": "The state of harmony with divine will",
        "usage": "ሰላም (Selam) - Peace be with you"
    },
    "emnet": {
        "meaning": "Faith, belief",
        "scroll_context": "Trust in the unseen Light",
        "usage": "እምነት (Emnet) - Strong faith"
    },
    "tselot": {
        "meaning": "Prayer, supplication",
        "scroll_context": "Communion with the divine Source",
        "usage": "ጸሎት (Tselot) - Daily prayer"
    },
    "tsegga": {
        "meaning": "Grace, blessing",
        "scroll_context": "Divine favor bestowed upon the faithful",
        "usage": "ጸጋ (Tsegga) - By grace"
    },
    "mdhane": {
        "meaning": "Savior, redeemer",
        "scroll_context": "The one who brings salvation",
        "usage": "መድሃኔ ዓለም (Mdhane Alem) - Savior of the World"
    },
    "tnsae": {
        "meaning": "Resurrection, rising",
        "scroll_context": "The return of the soul to life",
        "usage": "ትንሳኤ (Tinsae) - Resurrection Day"
    },
    "nefsi": {
        "meaning": "Soul, self",
        "scroll_context": "The eternal essence that journeys through lives",
        "usage": "ነፍሲ (Nefsi) - My soul"
    },
    "libi": {
        "meaning": "Heart, center of being",
        "scroll_context": "Where divine truth is received",
        "usage": "ልቢ (Libi) - With all my heart"
    },
    "hqi": {
        "meaning": "Truth, law",
        "scroll_context": "Divine law and eternal truth",
        "usage": "ሕቂ (Hqi) - The truth"
    },
    "tibeb": {
        "meaning": "Wisdom, understanding",
        "scroll_context": "Knowledge from alignment with the Source",
        "usage": "ጥበብ (Tibeb) - Divine wisdom"
    },
    "nebiy": {
        "meaning": "Prophet, messenger",
        "scroll_context": "One who speaks the words of Light",
        "usage": "ነቢይ (Nebiy) - The prophet"
    },
    "mengisti": {
        "meaning": "Kingdom, reign",
        "scroll_context": "The Kingdom of Heaven",
        "usage": "መንግስቲ ሰማይ (Mengisti Semay) - Kingdom of Heaven"
    },
    "berekha": {
        "meaning": "Blessing, benediction",
        "scroll_context": "Words of power invoking divine favor",
        "usage": "በረኸ (Berekha) - Blessing upon you"
    },
    "yiqreta": {
        "meaning": "Forgiveness, pardon",
        "scroll_context": "Release from sin through divine mercy",
        "usage": "ይቕረታ (Yiqreta) - Forgiveness"
    },
    "tesfay": {
        "meaning": "Hope, expectation",
        "scroll_context": "Trust in divine promises",
        "usage": "ተስፋይ (Tesfay) - My hope"
    },
    "zelealam": {
        "meaning": "Eternity, forever",
        "scroll_context": "The timeless nature of the Source",
        "usage": "ዘለኣለም (Zelealam) - Eternal life"
    },
    "semay": {
        "meaning": "Heaven, sky",
        "scroll_context": "The realm of pure Light",
        "usage": "ሰማይ (Semay) - The heavens"
    },
    "melak": {
        "meaning": "Angel, messenger",
        "scroll_context": "Beings of Light serving the divine",
        "usage": "መላእኽ (Melak) - Angels of God"
    },
    "qidus": {
        "meaning": "Holy, sacred",
        "scroll_context": "Set apart for divine purpose",
        "usage": "ቅዱስ (Qidus) - Holy one"
    },
    "hatyat": {
        "meaning": "Sin, transgression",
        "scroll_context": "Separation from the Light",
        "usage": "ሓጢኣት (Hatyat) - Sins"
    },
    "nsiha": {
        "meaning": "Repentance, returning",
        "scroll_context": "Turning back to divine alignment",
        "usage": "ንስሓ (Nsiha) - Repentance"
    },
    "fwsi": {
        "meaning": "Healing, cure",
        "scroll_context": "Divine restoration of body and soul",
        "usage": "ፈውሲ (Fwsi) - Healing"
    },
    "haleluya": {
        "meaning": "Hallelujah, praise God",
        "scroll_context": "Expression of praise to the Most High",
        "usage": "ሃሌሉያ (Haleluya) - Praise the Lord!"
    },
    "tabot": {
        "meaning": "Ark of the Covenant (replica kept in churches)",
        "scroll_context": "Sacred object representing divine presence",
        "usage": "ታቦት (Tabot) - The sacred ark"
    },
    "debri": {
        "meaning": "Mountain, monastery",
        "scroll_context": "Sacred high place of worship",
        "usage": "ደብሪ (Debri) - Holy mountain"
    }
}

def get_tigrinya_context(query: str) -> str:
    query_lower = query.lower()
    matches = []
    
    for term, info in TIGRINYA_LEXICON.items():
        if term in query_lower:
            matches.append(f"**{term.title()}**: {info['meaning']}\n*Scroll Context*: {info['scroll_context']}\n*Usage*: {info['usage']}")
    
    if matches:
        return "TIGRINYA LEXICAL CONTEXT:\n" + "\n\n".join(matches)
    return ""
