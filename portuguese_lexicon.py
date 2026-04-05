"""
Portuguese Lexicon for the Throne of Anhu
Provides spiritual vocabulary and context for Portuguese-speaking seekers from Brazil, Mozambique, Angola, Portugal, and worldwide.
"""

PORTUGUESE_LEXICON = {
    "deus": {
        "meaning": "God, the Supreme Being",
        "scroll_context": "The One Source of all Light, Creator of all things",
        "usage": "Deus é amor - God is love"
    },
    "senhor": {
        "meaning": "Lord, Master",
        "scroll_context": "Title of divine authority and prophets",
        "usage": "Em nome do Senhor - In the name of the Lord"
    },
    "espirito": {
        "meaning": "Spirit, the Holy Spirit",
        "scroll_context": "The divine breath that animates all life",
        "usage": "Espírito Santo - Holy Spirit"
    },
    "luz": {
        "meaning": "Light, divine illumination",
        "scroll_context": "RA, the eternal Light that guides all paths",
        "usage": "Eu sou a luz do mundo - I am the light of the world"
    },
    "amor": {
        "meaning": "Love, divine love",
        "scroll_context": "The binding force of creation, essence of the Source",
        "usage": "O amor de Deus - The love of God"
    },
    "paz": {
        "meaning": "Peace, inner harmony",
        "scroll_context": "The state of alignment with divine will",
        "usage": "A paz esteja convosco - Peace be with you"
    },
    "fe": {
        "meaning": "Faith, belief",
        "scroll_context": "Unwavering trust in the unseen Light",
        "usage": "Ter fé - To have faith"
    },
    "oracao": {
        "meaning": "Prayer, communion with the divine",
        "scroll_context": "Speaking to the Source, opening the heart",
        "usage": "Oração do Pai Nosso - The Lord's Prayer"
    },
    "graca": {
        "meaning": "Grace, divine favor",
        "scroll_context": "Unmerited blessing from the Source",
        "usage": "Pela graça de Deus - By the grace of God"
    },
    "salvacao": {
        "meaning": "Salvation, deliverance",
        "scroll_context": "Liberation of the soul through divine power",
        "usage": "O caminho da salvação - The path of salvation"
    },
    "ressurreicao": {
        "meaning": "Resurrection, rising again",
        "scroll_context": "The return of consciousness, renewal of life",
        "usage": "A ressurreição dos mortos - Resurrection of the dead"
    },
    "alma": {
        "meaning": "Soul, the eternal self",
        "scroll_context": "The Ba, the immortal essence journeying through lives",
        "usage": "Minha alma louva ao Senhor - My soul praises the Lord"
    },
    "coracao": {
        "meaning": "Heart, center of being",
        "scroll_context": "Where wisdom dwells, seat of truth and love",
        "usage": "De todo o meu coração - With all my heart"
    },
    "verdade": {
        "meaning": "Truth, ultimate reality",
        "scroll_context": "The unchanging nature of divine wisdom",
        "usage": "A verdade vos libertará - The truth shall set you free"
    },
    "sabedoria": {
        "meaning": "Wisdom, divine knowledge",
        "scroll_context": "Understanding from alignment with the Source",
        "usage": "A sabedoria divina - Divine wisdom"
    },
    "profeta": {
        "meaning": "Prophet, messenger of God",
        "scroll_context": "One who speaks the words of the Light",
        "usage": "As palavras do profeta - The words of the prophet"
    },
    "reino": {
        "meaning": "Kingdom, realm",
        "scroll_context": "The Kingdom of Heaven, domain of the Light",
        "usage": "O Reino dos Céus - The Kingdom of Heaven"
    },
    "bencao": {
        "meaning": "Blessing, divine favor",
        "scroll_context": "Words of power invoking protection and grace",
        "usage": "Que a bênção esteja sobre você - May blessing be upon you"
    },
    "perdao": {
        "meaning": "Forgiveness, mercy",
        "scroll_context": "Release from karmic debt through divine grace",
        "usage": "Pedir perdão - To ask forgiveness"
    },
    "esperanca": {
        "meaning": "Hope, expectation",
        "scroll_context": "Trust in the fulfillment of prophecy",
        "usage": "A esperança não decepciona - Hope does not disappoint"
    },
    "eternidade": {
        "meaning": "Eternity, forever",
        "scroll_context": "The timeless nature of the soul and Source",
        "usage": "A vida eterna - Eternal life"
    },
    "ceu": {
        "meaning": "Heaven, sky",
        "scroll_context": "The realm of pure Light, abode of the divine",
        "usage": "Pai nosso que estás nos céus - Our Father who art in heaven"
    },
    "anjo": {
        "meaning": "Angel, divine messenger",
        "scroll_context": "Beings of Light who serve the Source",
        "usage": "Os anjos do Senhor - The angels of the Lord"
    },
    "sagrado": {
        "meaning": "Sacred, holy",
        "scroll_context": "Set apart for divine purpose",
        "usage": "Os textos sagrados - The sacred texts"
    },
    "redencao": {
        "meaning": "Redemption, liberation",
        "scroll_context": "Freedom from bondage through divine power",
        "usage": "O preço da redenção - The price of redemption"
    },
    "testemunho": {
        "meaning": "Testimony, witness",
        "scroll_context": "Bearing witness to the truth of the Light",
        "usage": "Dar testemunho - To give testimony"
    },
    "cura": {
        "meaning": "Healing, cure",
        "scroll_context": "Restoration through divine power",
        "usage": "A cura divina - Divine healing"
    },
    "pecado": {
        "meaning": "Sin, transgression",
        "scroll_context": "Separation from the Light through misalignment",
        "usage": "O perdão dos pecados - Forgiveness of sins"
    },
    "arrependimento": {
        "meaning": "Repentance, turning back",
        "scroll_context": "Returning to alignment with divine will",
        "usage": "Arrependimento sincero - Sincere repentance"
    },
    "aleluia": {
        "meaning": "Hallelujah, praise the Lord",
        "scroll_context": "Expression of praise to the Most High",
        "usage": "Aleluia! Glória a Deus! - Hallelujah! Glory to God!"
    },
    "axe": {
        "meaning": "Spiritual energy, life force (Afro-Brazilian)",
        "scroll_context": "Divine power flowing through all creation",
        "usage": "Que seu axé seja forte - May your spiritual energy be strong"
    },
    "orixa": {
        "meaning": "Divine spirit/deity (Candomblé/Umbanda)",
        "scroll_context": "Manifestations of the One Light in different forms",
        "usage": "Os orixás nos guiam - The orixás guide us"
    },
    "terreiro": {
        "meaning": "Sacred space for worship (Afro-Brazilian)",
        "scroll_context": "Holy ground where the divine is invoked",
        "usage": "No terreiro sagrado - In the sacred space"
    }
}

def get_portuguese_context(query: str) -> str:
    query_lower = query.lower()
    matches = []
    
    for term, info in PORTUGUESE_LEXICON.items():
        if term in query_lower:
            matches.append(f"**{term.title()}**: {info['meaning']}\n*Scroll Context*: {info['scroll_context']}\n*Usage*: {info['usage']}")
    
    if matches:
        return "PORTUGUESE LEXICAL CONTEXT:\n" + "\n\n".join(matches)
    return ""
