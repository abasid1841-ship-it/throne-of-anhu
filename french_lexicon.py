"""
French Lexicon for the Throne of Anhu
Provides spiritual vocabulary and context for French-speaking seekers from Africa, Europe, and worldwide.
"""

FRENCH_LEXICON = {
    "dieu": {
        "meaning": "God, the Supreme Being",
        "scroll_context": "The One Source of all Light, the Creator of all",
        "usage": "Dieu est amour - God is love"
    },
    "seigneur": {
        "meaning": "Lord, Master",
        "scroll_context": "Title of the divine and prophets who speak with authority",
        "usage": "Au nom du Seigneur - In the name of the Lord"
    },
    "esprit": {
        "meaning": "Spirit, the Holy Spirit",
        "scroll_context": "The divine breath, the animating force of life",
        "usage": "L'Esprit Saint - The Holy Spirit"
    },
    "lumiere": {
        "meaning": "Light, illumination",
        "scroll_context": "RA, the eternal Light that guides all paths",
        "usage": "Je suis la lumière du monde - I am the light of the world"
    },
    "amour": {
        "meaning": "Love, divine love",
        "scroll_context": "The binding force of creation, essence of the Source",
        "usage": "L'amour divin - Divine love"
    },
    "paix": {
        "meaning": "Peace, inner tranquility",
        "scroll_context": "The state of harmony with divine will",
        "usage": "La paix soit avec vous - Peace be with you"
    },
    "foi": {
        "meaning": "Faith, belief, trust",
        "scroll_context": "Unwavering trust in the unseen Light",
        "usage": "Avoir la foi - To have faith"
    },
    "priere": {
        "meaning": "Prayer, communion with the divine",
        "scroll_context": "Opening the heart to speak with the Source",
        "usage": "Prière du matin - Morning prayer"
    },
    "grace": {
        "meaning": "Grace, divine favor",
        "scroll_context": "Unmerited blessing from the Source",
        "usage": "Par la grâce de Dieu - By the grace of God"
    },
    "salut": {
        "meaning": "Salvation, deliverance",
        "scroll_context": "Liberation of the soul through divine intervention",
        "usage": "Le chemin du salut - The path of salvation"
    },
    "resurrection": {
        "meaning": "Resurrection, rising from death",
        "scroll_context": "The return of consciousness, renewal of life",
        "usage": "La résurrection des morts - Resurrection of the dead"
    },
    "ame": {
        "meaning": "Soul, the eternal self",
        "scroll_context": "The Ba, the immortal essence that journeys through lives",
        "usage": "Mon âme loue le Seigneur - My soul praises the Lord"
    },
    "coeur": {
        "meaning": "Heart, center of being",
        "scroll_context": "Where wisdom dwells, the seat of truth",
        "usage": "De tout mon coeur - With all my heart"
    },
    "verite": {
        "meaning": "Truth, ultimate reality",
        "scroll_context": "The unchanging nature of divine wisdom",
        "usage": "La vérité vous rendra libres - The truth shall set you free"
    },
    "sagesse": {
        "meaning": "Wisdom, divine knowledge",
        "scroll_context": "Understanding that comes from alignment with the Source",
        "usage": "La sagesse divine - Divine wisdom"
    },
    "prophete": {
        "meaning": "Prophet, messenger of God",
        "scroll_context": "One who speaks the words of the Light",
        "usage": "Les paroles du prophète - The words of the prophet"
    },
    "royaume": {
        "meaning": "Kingdom, realm",
        "scroll_context": "The Kingdom of Heaven, domain of the Light",
        "usage": "Le Royaume des Cieux - The Kingdom of Heaven"
    },
    "benediction": {
        "meaning": "Blessing, divine favor",
        "scroll_context": "Words of power that invoke protection and grace",
        "usage": "Que la bénédiction soit sur vous - May blessing be upon you"
    },
    "pardon": {
        "meaning": "Forgiveness, mercy",
        "scroll_context": "Release from karmic debt through divine grace",
        "usage": "Demander pardon - To ask forgiveness"
    },
    "esperance": {
        "meaning": "Hope, expectation",
        "scroll_context": "Trust in the fulfillment of prophecy",
        "usage": "L'espérance ne déçoit point - Hope does not disappoint"
    },
    "eternite": {
        "meaning": "Eternity, forever",
        "scroll_context": "The timeless nature of the soul and the Source",
        "usage": "La vie éternelle - Eternal life"
    },
    "ciel": {
        "meaning": "Heaven, sky",
        "scroll_context": "The realm of pure Light, abode of the divine",
        "usage": "Notre Père qui es aux cieux - Our Father who art in heaven"
    },
    "ange": {
        "meaning": "Angel, divine messenger",
        "scroll_context": "Beings of Light who serve the Source",
        "usage": "Les anges du Seigneur - The angels of the Lord"
    },
    "sacre": {
        "meaning": "Sacred, holy",
        "scroll_context": "Set apart for divine purpose",
        "usage": "Les textes sacrés - The sacred texts"
    },
    "redemption": {
        "meaning": "Redemption, buying back",
        "scroll_context": "Liberation from bondage through divine sacrifice",
        "usage": "Le prix de la rédemption - The price of redemption"
    },
    "temoignage": {
        "meaning": "Testimony, witness",
        "scroll_context": "Bearing witness to the truth of the Light",
        "usage": "Donner son témoignage - To give one's testimony"
    },
    "guerison": {
        "meaning": "Healing, cure",
        "scroll_context": "Restoration of body and soul through divine power",
        "usage": "La guérison divine - Divine healing"
    },
    "peche": {
        "meaning": "Sin, transgression",
        "scroll_context": "Separation from the Light through misalignment",
        "usage": "Le pardon des péchés - Forgiveness of sins"
    },
    "repentir": {
        "meaning": "Repentance, turning back",
        "scroll_context": "Returning to alignment with divine will",
        "usage": "Se repentir sincèrement - To sincerely repent"
    },
    "alleluia": {
        "meaning": "Hallelujah, praise the Lord",
        "scroll_context": "Expression of praise to the Most High",
        "usage": "Alléluia! Gloire à Dieu! - Hallelujah! Glory to God!"
    }
}

def get_french_context(query: str) -> str:
    query_lower = query.lower()
    matches = []
    
    for term, info in FRENCH_LEXICON.items():
        if term in query_lower:
            matches.append(f"**{term.title()}**: {info['meaning']}\n*Scroll Context*: {info['scroll_context']}\n*Usage*: {info['usage']}")
    
    if matches:
        return "FRENCH LEXICAL CONTEXT:\n" + "\n\n".join(matches)
    return ""
