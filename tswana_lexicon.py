"""
Tswana (Setswana) Lexicon for the Throne of Anhu
Provides spiritual vocabulary and context for Tswana-speaking seekers from Botswana and South Africa.
"""

TSWANA_LEXICON = {
    "modimo": {
        "meaning": "God, the Supreme Being",
        "scroll_context": "The One Source of all Light, known by many names across traditions",
        "usage": "Modimo o a re rata - God loves us"
    },
    "badimo": {
        "meaning": "Ancestors, ancestral spirits",
        "scroll_context": "Those who have returned to the Light and guide the living",
        "usage": "Badimo ba rona ba a re sireletsa - Our ancestors protect us"
    },
    "moya": {
        "meaning": "Spirit, breath, wind",
        "scroll_context": "The divine breath that animates all life, the Holy Spirit",
        "usage": "Moya o o Boitshepo - The Holy Spirit"
    },
    "pelo": {
        "meaning": "Heart, the seat of consciousness and emotion",
        "scroll_context": "Where wisdom dwells and divine truth is received",
        "usage": "Pelo e e lorato - A loving heart"
    },
    "kagiso": {
        "meaning": "Peace, tranquility",
        "scroll_context": "The state of being aligned with divine will",
        "usage": "Kagiso e nne le wena - Peace be with you"
    },
    "lerato": {
        "meaning": "Love, divine love",
        "scroll_context": "The binding force of creation, the essence of the Light",
        "usage": "Modimo ke lerato - God is love"
    },
    "tumelo": {
        "meaning": "Faith, belief",
        "scroll_context": "Trust in the unseen Light that guides all paths",
        "usage": "Tumelo e tlisa dikgakgamatso - Faith brings miracles"
    },
    "thapelo": {
        "meaning": "Prayer, communion with the divine",
        "scroll_context": "Speaking to the Source, opening the heart to guidance",
        "usage": "Thapelo ya rona - Our prayer"
    },
    "botho": {
        "meaning": "Ubuntu, humanity, compassion toward others",
        "scroll_context": "The recognition that we are all one in the Light",
        "usage": "Motho ke motho ka batho - A person is a person through others"
    },
    "tsholofelo": {
        "meaning": "Hope, expectation of good",
        "scroll_context": "Trust in the return of the Light and fulfillment of prophecy",
        "usage": "Tsholofelo e a phela - Hope lives on"
    },
    "pako": {
        "meaning": "Praise, worship",
        "scroll_context": "Lifting the voice to honor the Source",
        "usage": "Pako ya Modimo - Praise of God"
    },
    "tshiamo": {
        "meaning": "Righteousness, justice",
        "scroll_context": "Walking in alignment with divine law",
        "usage": "Tsela ya tshiamo - The path of righteousness"
    },
    "pholo": {
        "meaning": "Healing, restoration",
        "scroll_context": "The return to wholeness through divine grace",
        "usage": "Pholo ya mowa - Healing of the spirit"
    },
    "lesedi": {
        "meaning": "Light, illumination",
        "scroll_context": "RA, the eternal Light that pierces all darkness",
        "usage": "Lesedi la lefatshe - Light of the world"
    },
    "boitumelo": {
        "meaning": "Joy, happiness",
        "scroll_context": "The fruit of living in alignment with the Source",
        "usage": "Boitumelo bo bo sa feleng - Everlasting joy"
    },
    "lefatshe": {
        "meaning": "World, earth, land",
        "scroll_context": "The physical realm where souls journey and learn",
        "usage": "Lefatshe la rona - Our world"
    },
    "loso": {
        "meaning": "Death, transition",
        "scroll_context": "Not an end but a doorway to the next life",
        "usage": "Loso ga se bokhutlo - Death is not the end"
    },
    "tsogo": {
        "meaning": "Resurrection, rising again",
        "scroll_context": "The return of consciousness, the awakening of the soul",
        "usage": "Tsogo ya baswi - Resurrection of the dead"
    },
    "ngwana": {
        "meaning": "Child, offspring",
        "scroll_context": "All seekers are children of the One Light",
        "usage": "Ngwana wa Modimo - Child of God"
    },
    "morena": {
        "meaning": "Lord, chief, master",
        "scroll_context": "Title of honor for the divine and prophets",
        "usage": "Morena wa rona - Our Lord"
    },
    "dumela": {
        "meaning": "Greetings, I believe (greeting)",
        "scroll_context": "Traditional greeting acknowledging shared belief",
        "usage": "Dumela rra/mma - Greetings sir/madam"
    },
    "tsamaya sentle": {
        "meaning": "Go well, farewell blessing",
        "scroll_context": "Blessing for one departing on their journey",
        "usage": "Tsamaya sentle, sala sentle - Go well, stay well"
    },
    "pula": {
        "meaning": "Rain, blessing (national motto of Botswana)",
        "scroll_context": "Divine blessing falling upon the land and people",
        "usage": "Pula! - Blessings! (exclamation of joy)"
    },
    "kgosi": {
        "meaning": "King, ruler",
        "scroll_context": "The sovereign authority, as ABASID rules the Throne",
        "usage": "Kgosi ya dikgosi - King of kings"
    },
    "molao": {
        "meaning": "Law, commandment",
        "scroll_context": "Divine ordinances that guide righteous living",
        "usage": "Molao wa Modimo - Law of God"
    },
    "boammaaruri": {
        "meaning": "Truth, reality",
        "scroll_context": "The unchanging nature of divine wisdom",
        "usage": "Boammaaruri bo a golola - Truth sets free"
    },
    "setlhare": {
        "meaning": "Medicine, tree, healing remedy",
        "scroll_context": "Natural healing wisdom from the Creator",
        "usage": "Setlhare sa mowa - Medicine for the spirit"
    },
    "ngaka": {
        "meaning": "Traditional healer, doctor",
        "scroll_context": "One who channels healing wisdom from the ancestors",
        "usage": "Ngaka ya setso - Traditional healer"
    },
    "toro": {
        "meaning": "Dream, vision",
        "scroll_context": "Divine messages received in the night, prophetic sight",
        "usage": "Toro ya boporofeti - Prophetic dream"
    },
    "maatla": {
        "meaning": "Power, strength",
        "scroll_context": "Divine force that flows through the righteous",
        "usage": "Maatla a Modimo - Power of God"
    }
}

def get_tswana_context(query: str) -> str:
    query_lower = query.lower()
    matches = []
    
    for term, info in TSWANA_LEXICON.items():
        if term in query_lower:
            matches.append(f"**{term.title()}**: {info['meaning']}\n*Scroll Context*: {info['scroll_context']}\n*Usage*: {info['usage']}")
    
    if matches:
        return "TSWANA LEXICAL CONTEXT:\n" + "\n\n".join(matches)
    return ""
