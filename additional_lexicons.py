"""
Additional Language Lexicons for the Throne of Anhu.

Supports: Nyanja, Bemba, Xhosa, Georgian, Romanian, German, Russian,
Jamaican Patois, Oromo, Latin, Greek, Irish, Welsh, Venda, Turkish,
Swedish, Sanskrit, Polish, Dutch, Danish, Afrikaans
"""

from typing import Dict, List


# ========================================
# NYANJA (Chichewa/Chinyanja) - Zambia/Malawi
# ========================================
NYANJA_LEXICON = {
    "Mulungu": "God, the Supreme Being",
    "Mzimu": "Spirit, soul",
    "Mzimu Woyera": "Holy Spirit",
    "Mtendere": "Peace",
    "Chikondi": "Love",
    "Chisomo": "Grace, mercy",
    "Mphamvu": "Power, strength",
    "Moyo": "Life",
    "Imfa": "Death",
    "Kuuka": "Resurrection, to rise again",
    "Mfumu": "King, chief",
    "Mtsogoleri": "Leader, guide",
    "Choonadi": "Truth",
    "Chipulumutso": "Salvation",
    "Pemphero": "Prayer",
    "Lamulo": "Commandment, law",
}


# ========================================
# BEMBA - Zambia
# ========================================
BEMBA_LEXICON = {
    "Lesa": "God",
    "Mupashi": "Spirit",
    "Mutende": "Peace",
    "Citemwiko": "Love",
    "Icisuma": "Grace",
    "Amaka": "Power",
    "Ubumi": "Life",
    "Imfwa": "Death",
    "Ukubuuka": "Resurrection",
    "Imfumu": "King",
    "Icishinka": "Truth",
    "Ubupusushi": "Salvation",
    "Ukulomba": "Prayer",
    "Amafunde": "Teachings",
}


# ========================================
# XHOSA - South Africa
# ========================================
XHOSA_LEXICON = {
    "uThixo": "God",
    "uMoya": "Spirit",
    "uMoya oyiNgcwele": "Holy Spirit",
    "uxolo": "Peace",
    "uthando": "Love",
    "ubabalo": "Grace",
    "amandla": "Power",
    "ubomi": "Life",
    "ukufa": "Death",
    "uvuko": "Resurrection",
    "inkosi": "King, chief",
    "inyaniso": "Truth",
    "usindiso": "Salvation",
    "umthandazo": "Prayer",
    "ubuntu": "Humanity, compassion, I am because we are",
    "isithembiso": "Promise",
    "inkululeko": "Freedom",
}


# ========================================
# GEORGIAN
# ========================================
GEORGIAN_LEXICON = {
    "ღმერთი": "Ghmerti - God",
    "სული": "Suli - Soul, spirit",
    "წმინდა სული": "Tsminda Suli - Holy Spirit",
    "მშვიდობა": "Mshvidoba - Peace",
    "სიყვარული": "Siqvaruli - Love",
    "მადლი": "Madli - Grace",
    "ძალა": "Dzala - Power",
    "სიცოცხლე": "Sicocxle - Life",
    "სიკვდილი": "Sikvdili - Death",
    "აღდგომა": "Aghdgoma - Resurrection",
    "მეფე": "Mepe - King",
    "სიმართლე": "Simartkhle - Truth",
    "ხსნა": "Khsna - Salvation",
    "ლოცვა": "Lotsva - Prayer",
}


# ========================================
# ROMANIAN
# ========================================
ROMANIAN_LEXICON = {
    "Dumnezeu": "God",
    "Suflet": "Soul",
    "Duh Sfânt": "Holy Spirit",
    "Pace": "Peace",
    "Dragoste": "Love",
    "Har": "Grace",
    "Putere": "Power",
    "Viață": "Life",
    "Moarte": "Death",
    "Înviere": "Resurrection",
    "Rege": "King",
    "Adevăr": "Truth",
    "Mântuire": "Salvation",
    "Rugăciune": "Prayer",
    "Credință": "Faith",
    "Speranță": "Hope",
}


# ========================================
# GERMAN
# ========================================
GERMAN_LEXICON = {
    "Gott": "God",
    "Seele": "Soul",
    "Heiliger Geist": "Holy Spirit",
    "Friede": "Peace",
    "Liebe": "Love",
    "Gnade": "Grace",
    "Kraft": "Power",
    "Leben": "Life",
    "Tod": "Death",
    "Auferstehung": "Resurrection",
    "König": "King",
    "Wahrheit": "Truth",
    "Erlösung": "Salvation, redemption",
    "Gebet": "Prayer",
    "Glaube": "Faith",
    "Hoffnung": "Hope",
    "Licht": "Light",
    "Weisheit": "Wisdom",
}


# ========================================
# RUSSIAN
# ========================================
RUSSIAN_LEXICON = {
    "Бог": "Bog - God",
    "Душа": "Dusha - Soul",
    "Святой Дух": "Svyatoy Dukh - Holy Spirit",
    "Мир": "Mir - Peace (also means 'world')",
    "Любовь": "Lyubov - Love",
    "Благодать": "Blagodat - Grace",
    "Сила": "Sila - Power",
    "Жизнь": "Zhizn - Life",
    "Смерть": "Smert - Death",
    "Воскресение": "Voskresenie - Resurrection",
    "Царь": "Tsar - King, emperor",
    "Правда": "Pravda - Truth",
    "Спасение": "Spasenie - Salvation",
    "Молитва": "Molitva - Prayer",
    "Вера": "Vera - Faith",
    "Надежда": "Nadezhda - Hope",
    "Свет": "Svet - Light",
}


# ========================================
# JAMAICAN PATOIS
# ========================================
JAMAICAN_PATOIS_LEXICON = {
    "Jah": "God, the Most High (from Jehovah)",
    "Selassie I": "Haile Selassie, revered as divine in Rastafari",
    "Irie": "Positive, peaceful, good",
    "Babylon": "The corrupt system, oppression",
    "Zion": "The promised land, Africa, Ethiopia, heaven",
    "Iyah": "Higher, spiritual elevation",
    "I an I": "We, the unified self with Jah",
    "Livity": "Lifestyle, way of living",
    "Overstand": "To understand deeply (not stand under)",
    "Dread": "Awesome, fearsome, also a Rastafarian",
    "One Love": "Unity, universal love",
    "Roots": "Origins, African heritage",
    "Nyabinghi": "Sacred drumming ceremony, death to oppressors",
    "Ital": "Natural, vital, clean food",
    "Forward": "To progress, move ahead spiritually",
    "Ras": "Prince, head (from Amharic)",
    "Tafari": "One to be feared (from Amharic)",
}


# ========================================
# OROMO - Ethiopia/Kenya
# ========================================
OROMO_LEXICON = {
    "Waaqa": "God, the sky god in traditional Oromo religion",
    "Lubbuua": "Soul, spirit",
    "Nagaa": "Peace",
    "Jaalala": "Love",
    "Araaraa": "Grace, reconciliation",
    "Humna": "Power",
    "Jireenya": "Life",
    "Du'a": "Death",
    "Ka'uu": "Resurrection, rising",
    "Mootii": "King",
    "Dhugaa": "Truth",
    "Fayyina": "Salvation",
    "Kadhannaa": "Prayer",
    "Amantaa": "Faith",
    "Gadaa": "Democratic governance system",
    "Safuu": "Moral order, cosmic harmony",
}


# ========================================
# LATIN
# ========================================
LATIN_LEXICON = {
    "Deus": "God",
    "Anima": "Soul",
    "Spiritus Sanctus": "Holy Spirit",
    "Pax": "Peace",
    "Amor": "Love",
    "Gratia": "Grace",
    "Potentia": "Power",
    "Vita": "Life",
    "Mors": "Death",
    "Resurrectio": "Resurrection",
    "Rex": "King",
    "Veritas": "Truth",
    "Salus": "Salvation, health",
    "Oratio": "Prayer",
    "Fides": "Faith",
    "Spes": "Hope",
    "Lux": "Light",
    "Verbum": "Word, the Logos",
    "Pater": "Father",
    "Filius": "Son",
    "Gloria": "Glory",
    "Amen": "So be it, truly",
}


# ========================================
# GREEK (Ancient/Koine)
# ========================================
GREEK_LEXICON = {
    "Θεός": "Theos - God",
    "Ψυχή": "Psyche - Soul",
    "Πνεῦμα Ἅγιον": "Pneuma Hagion - Holy Spirit",
    "Εἰρήνη": "Eirene - Peace",
    "Ἀγάπη": "Agape - Unconditional love",
    "Χάρις": "Charis - Grace",
    "Δύναμις": "Dynamis - Power",
    "Ζωή": "Zoe - Life (eternal life)",
    "Βίος": "Bios - Life (biological life)",
    "Θάνατος": "Thanatos - Death",
    "Ἀνάστασις": "Anastasis - Resurrection",
    "Βασιλεύς": "Basileus - King",
    "Ἀλήθεια": "Aletheia - Truth",
    "Σωτηρία": "Soteria - Salvation",
    "Προσευχή": "Proseuche - Prayer",
    "Πίστις": "Pistis - Faith",
    "Ἐλπίς": "Elpis - Hope",
    "Φῶς": "Phos - Light",
    "Λόγος": "Logos - Word, reason, divine principle",
    "Χριστός": "Christos - Anointed One, Christ",
    "Κύριος": "Kyrios - Lord",
}


# ========================================
# IRISH (Gaelic)
# ========================================
IRISH_LEXICON = {
    "Dia": "God",
    "Anam": "Soul",
    "An Spiorad Naomh": "The Holy Spirit",
    "Síocháin": "Peace",
    "Grá": "Love",
    "Grásta": "Grace",
    "Cumhacht": "Power",
    "Beatha": "Life",
    "Bás": "Death",
    "Aiséirí": "Resurrection",
    "Rí": "King",
    "Fírinne": "Truth",
    "Slánú": "Salvation",
    "Paidir": "Prayer",
    "Creideamh": "Faith",
    "Dóchas": "Hope",
    "Solas": "Light",
    "Gaois": "Wisdom",
}


# ========================================
# WELSH
# ========================================
WELSH_LEXICON = {
    "Duw": "God",
    "Enaid": "Soul",
    "Ysbryd Glân": "Holy Spirit",
    "Heddwch": "Peace",
    "Cariad": "Love",
    "Gras": "Grace",
    "Nerth": "Power, strength",
    "Bywyd": "Life",
    "Marwolaeth": "Death",
    "Atgyfodiad": "Resurrection",
    "Brenin": "King",
    "Gwirionedd": "Truth",
    "Iachawdwriaeth": "Salvation",
    "Gweddi": "Prayer",
    "Ffydd": "Faith",
    "Gobaith": "Hope",
    "Goleuni": "Light",
}


# ========================================
# VENDA - South Africa
# ========================================
VENDA_LEXICON = {
    "Mudzimu": "God, ancestor spirit",
    "Moya": "Spirit, soul",
    "Mulalo": "Peace",
    "Lufuno": "Love",
    "Vhutshilo": "Life",
    "Lufu": "Death",
    "Khosi": "King, chief",
    "Ngoho": "Truth",
    "Thalusambo": "Prayer",
    "Lutendo": "Faith",
    "Fulufhelo": "Hope",
    "Tshedza": "Light",
    "Vhugala": "Wisdom",
    "Makhadzi": "Aunt (important spiritual role)",
}


# ========================================
# TURKISH
# ========================================
TURKISH_LEXICON = {
    "Allah": "God",
    "Tanrı": "God (pre-Islamic)",
    "Ruh": "Soul, spirit",
    "Kutsal Ruh": "Holy Spirit",
    "Barış": "Peace",
    "Aşk": "Love",
    "Sevgi": "Love, affection",
    "Lütuf": "Grace",
    "Güç": "Power",
    "Hayat": "Life",
    "Ölüm": "Death",
    "Diriliş": "Resurrection",
    "Kral": "King",
    "Hakikat": "Truth",
    "Kurtuluş": "Salvation",
    "Dua": "Prayer",
    "İman": "Faith",
    "Umut": "Hope",
    "Işık": "Light",
}


# ========================================
# SWEDISH
# ========================================
SWEDISH_LEXICON = {
    "Gud": "God",
    "Själ": "Soul",
    "Helig Ande": "Holy Spirit",
    "Fred": "Peace",
    "Kärlek": "Love",
    "Nåd": "Grace",
    "Kraft": "Power",
    "Liv": "Life",
    "Död": "Death",
    "Uppståndelse": "Resurrection",
    "Kung": "King",
    "Sanning": "Truth",
    "Frälsning": "Salvation",
    "Bön": "Prayer",
    "Tro": "Faith",
    "Hopp": "Hope",
    "Ljus": "Light",
}


# ========================================
# SANSKRIT
# ========================================
SANSKRIT_LEXICON = {
    "ब्रह्मन्": "Brahman - Ultimate Reality, the Absolute",
    "आत्मन्": "Atman - Soul, Self",
    "धर्म": "Dharma - Cosmic law, duty, righteousness",
    "कर्म": "Karma - Action, cause and effect",
    "मोक्ष": "Moksha - Liberation, release from cycle of rebirth",
    "संसार": "Samsara - Cycle of birth, death, rebirth",
    "योग": "Yoga - Union, discipline",
    "शान्ति": "Shanti - Peace",
    "प्रेम": "Prem - Love",
    "शक्ति": "Shakti - Power, divine feminine energy",
    "जीवन": "Jivan - Life",
    "मृत्यु": "Mrityu - Death",
    "सत्य": "Satya - Truth",
    "अहिंसा": "Ahimsa - Non-violence",
    "ज्ञान": "Jnana - Knowledge, wisdom",
    "भक्ति": "Bhakti - Devotion",
    "गुरु": "Guru - Teacher, spiritual guide",
    "मन्त्र": "Mantra - Sacred utterance",
    "ॐ": "Om - Sacred syllable, the sound of the universe",
    "नमस्ते": "Namaste - The divine in me honors the divine in you",
}


# ========================================
# POLISH
# ========================================
POLISH_LEXICON = {
    "Bóg": "God",
    "Dusza": "Soul",
    "Duch Święty": "Holy Spirit",
    "Pokój": "Peace",
    "Miłość": "Love",
    "Łaska": "Grace",
    "Moc": "Power",
    "Życie": "Life",
    "Śmierć": "Death",
    "Zmartwychwstanie": "Resurrection",
    "Król": "King",
    "Prawda": "Truth",
    "Zbawienie": "Salvation",
    "Modlitwa": "Prayer",
    "Wiara": "Faith",
    "Nadzieja": "Hope",
    "Światło": "Light",
}


# ========================================
# DUTCH
# ========================================
DUTCH_LEXICON = {
    "God": "God",
    "Ziel": "Soul",
    "Heilige Geest": "Holy Spirit",
    "Vrede": "Peace",
    "Liefde": "Love",
    "Genade": "Grace",
    "Kracht": "Power",
    "Leven": "Life",
    "Dood": "Death",
    "Opstanding": "Resurrection",
    "Koning": "King",
    "Waarheid": "Truth",
    "Verlossing": "Salvation",
    "Gebed": "Prayer",
    "Geloof": "Faith",
    "Hoop": "Hope",
    "Licht": "Light",
}


# ========================================
# DANISH
# ========================================
DANISH_LEXICON = {
    "Gud": "God",
    "Sjæl": "Soul",
    "Helligånd": "Holy Spirit",
    "Fred": "Peace",
    "Kærlighed": "Love",
    "Nåde": "Grace",
    "Kraft": "Power",
    "Liv": "Life",
    "Død": "Death",
    "Opstandelse": "Resurrection",
    "Konge": "King",
    "Sandhed": "Truth",
    "Frelse": "Salvation",
    "Bøn": "Prayer",
    "Tro": "Faith",
    "Håb": "Hope",
    "Lys": "Light",
}


# ========================================
# AFRIKAANS
# ========================================
AFRIKAANS_LEXICON = {
    "God": "God",
    "Siel": "Soul",
    "Heilige Gees": "Holy Spirit",
    "Vrede": "Peace",
    "Liefde": "Love",
    "Genade": "Grace",
    "Krag": "Power",
    "Lewe": "Life",
    "Dood": "Death",
    "Opstanding": "Resurrection",
    "Koning": "King",
    "Waarheid": "Truth",
    "Verlossing": "Salvation",
    "Gebed": "Prayer",
    "Geloof": "Faith",
    "Hoop": "Hope",
    "Lig": "Light",
    "Wysheid": "Wisdom",
}


# ========================================
# COMBINED FUNCTION
# ========================================
ALL_ADDITIONAL_LEXICONS = {
    "nyanja": NYANJA_LEXICON,
    "bemba": BEMBA_LEXICON,
    "xhosa": XHOSA_LEXICON,
    "georgian": GEORGIAN_LEXICON,
    "romanian": ROMANIAN_LEXICON,
    "german": GERMAN_LEXICON,
    "russian": RUSSIAN_LEXICON,
    "jamaican_patois": JAMAICAN_PATOIS_LEXICON,
    "oromo": OROMO_LEXICON,
    "latin": LATIN_LEXICON,
    "greek": GREEK_LEXICON,
    "irish": IRISH_LEXICON,
    "welsh": WELSH_LEXICON,
    "venda": VENDA_LEXICON,
    "turkish": TURKISH_LEXICON,
    "swedish": SWEDISH_LEXICON,
    "sanskrit": SANSKRIT_LEXICON,
    "polish": POLISH_LEXICON,
    "dutch": DUTCH_LEXICON,
    "danish": DANISH_LEXICON,
    "afrikaans": AFRIKAANS_LEXICON,
}


def get_additional_language_context(query: str) -> str:
    """
    Check if query contains words from any additional language lexicon.
    Returns context string for prompt injection.
    """
    query_lower = query.lower()
    contexts = []
    
    for lang_name, lexicon in ALL_ADDITIONAL_LEXICONS.items():
        for word, meaning in lexicon.items():
            if word.lower() in query_lower:
                contexts.append(f"[{lang_name.upper()}] {word}: {meaning}")
    
    if contexts:
        return "\n".join(contexts)
    return ""


def get_all_additional_lexicons() -> Dict[str, Dict[str, str]]:
    """Return all additional lexicons."""
    return ALL_ADDITIONAL_LEXICONS


def list_supported_languages() -> List[str]:
    """List all languages in additional lexicons."""
    return list(ALL_ADDITIONAL_LEXICONS.keys())
