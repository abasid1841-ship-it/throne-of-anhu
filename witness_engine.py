# witness_engine.py
# HOUSE OF WISDOM · Witness selector for the Throne of Anhu
# The 7 Planets orbit RA ☀️ like the Menorah before the Throne

from __future__ import annotations

from typing import List

from source_library import search_sources, SourceEntry

try:
    from semantic_witness import get_semantic_witnesses
    HAS_SEMANTIC_WITNESS = True
except ImportError:
    HAS_SEMANTIC_WITNESS = False
    get_semantic_witnesses = None

try:
    from planet_router import fetch_from_planets, get_planet_context, PLANETS
    HAS_PLANET_ROUTER = True
except ImportError:
    HAS_PLANET_ROUTER = False
    fetch_from_planets = None
    get_planet_context = None
    PLANETS = None


# -----------------------------
# NORMALISATION
# -----------------------------

def _normalise_question(q: str) -> str:
    """
    Normalise common sacred typos so House of Wisdom still hits.
    """
    q = (q or "").lower()

    replacements = {
        "ressurection": "resurrection",
        "resurection": "resurrection",
        "ressurrection": "resurrection",
        "ressurrect": "resurrect",
        "tge ": "the ",
        "judgement": "judgment",
    }
    for wrong, correct in replacements.items():
        if wrong in q:
            q = q.replace(wrong, correct)

    return q


STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "must", "shall", "can", "need", "dare",
    "to", "of", "in", "for", "on", "with", "at", "by", "from", "as",
    "into", "through", "during", "before", "after", "above", "below",
    "between", "under", "again", "further", "then", "once", "here",
    "there", "when", "where", "why", "how", "all", "each", "few",
    "more", "most", "other", "some", "such", "no", "nor", "not",
    "only", "own", "same", "so", "than", "too", "very", "just",
    "and", "but", "if", "or", "because", "until", "while", "about",
    "against", "between", "into", "through", "during", "before",
    "after", "above", "below", "up", "down", "out", "off", "over",
    "under", "again", "further", "then", "once", "what", "which",
    "who", "whom", "this", "that", "these", "those", "am", "it",
    "its", "itself", "they", "them", "their", "theirs", "themselves",
    "we", "us", "our", "ours", "ourselves", "you", "your", "yours",
    "yourself", "yourselves", "he", "him", "his", "himself", "she",
    "her", "hers", "herself", "i", "me", "my", "mine", "myself",
    "tell", "about", "say", "said", "speak", "know", "think",
    "does", "scrolls", "scroll", "throne", "abasid", "1841",
}


def _extract_keywords(q: str) -> List[str]:
    """
    Pick a small set of strong keywords/phrases to feed into search functions.
    Uses semantic understanding when available, falls back to keyword heuristics.
    """
    # Try semantic keyword extraction first
    try:
        from semantic_intent import get_witness_topics
        semantic_keywords = get_witness_topics(q)
        if semantic_keywords and len(semantic_keywords) >= 2:
            return semantic_keywords
    except Exception as e:
        print(f"[WITNESS] Semantic intent fallback: {e}")
    
    q = _normalise_question(q)
    q_lower = q.lower()

    keywords: List[str] = []

    # ---------------------------------
    # THEMATIC TRIGGERS (specific topics)
    # ---------------------------------

    # PRIORITY: Shona Alphabet / 22 Letters of Heaven
    if any(w in q_lower for w in ["shona alphabet", "22 letters", "letters of heaven", "alphabet of baba", "sacred letters", "language of grace"]):
        keywords.extend(["shona alphabet", "22 letters", "letters of heaven", "sacred sounds", "language of grace", "a se mwari", "nga se denga"])
        return list(set(keywords))  # Priority return for alphabet queries

    # Individual Shona letters
    if any(w in q_lower for w in ["letter a ", "letter ba", "letter ka", "letter ra", "letter ma", "letter da", "letter na", "letter sa", "letter zi", "letter ta", "letter va", "letter ngu", "letter nda", "letter pa", "letter ha", "letter ga", "letter shu", "letter mba", "letter nyu", "letter chi", "letter to", "letter nga"]):
        keywords.extend(["shona alphabet", "22 letters", "sacred sounds"])

    # Sheba / Queen of the South / Ethiopia / Africa
    if any(w in q_lower for w in ["sheba", "queen of the south", "makeda", "ethiopia", "axum"]):
        keywords.extend(["sheba", "queen", "solomon", "ethiopia", "africa", "wisdom", "throne"])

    # Zimbabwe / Rhodesia / Great Zimbabwe / Southern Africa
    if any(w in q_lower for w in ["zimbabwe", "rhodesia", "great zimbabwe", "dzimbabwe"]):
        keywords.extend(["zimbabwe", "africa", "land", "sheba", "kingdom", "stone", "ancestors"])

    # Menelik / Lion of Judah / Ark
    if any(w in q_lower for w in ["menelik", "lion of judah", "ark of the covenant", "ark"]):
        keywords.extend(["menelik", "lion", "judah", "ark", "covenant", "solomon", "sheba", "throne"])

    # Solomon / wisdom / temple
    if any(w in q_lower for w in ["solomon", "temple", "king solomon"]):
        keywords.extend(["solomon", "wisdom", "temple", "throne", "sheba", "judgment"])

    # Saturn / Chiron / celestial cycles
    if any(w in q_lower for w in ["saturn", "chiron", "planet", "cycle", "return"]):
        keywords.extend(["saturn", "cycle", "return", "time", "years", "chiron", "planet"])

    # Balance / law of balance / equilibrium
    if any(w in q_lower for w in ["balance", "equilibrium", "scales", "maat"]):
        keywords.extend(["balance", "law", "scales", "fire", "water", "judgment", "maat"])

    # PAPYRUS OF ANI / EGYPTIAN BOOK OF THE DEAD
    if any(w in q_lower for w in ["papyrus", "book of the dead", "book of dead", "per em hru", "coming forth by day"]):
        keywords.extend(["papyrus", "ani", "osiris", "judgment", "weighing heart", "duat", "maat"])

    # Egyptian gods and concepts
    if any(w in q_lower for w in ["osiris", "isis", "horus", "anubis", "thoth", "ptah", "atum", "nun"]):
        keywords.extend(["osiris", "isis", "horus", "anubis", "thoth", "ptah", "atum", "egyptian", "gods"])

    # Weighing of the Heart / Egyptian Judgment
    if any(w in q_lower for w in ["weighing of the heart", "weighing heart", "negative confession", "forty-two gods", "42 gods", "hall of two truths"]):
        keywords.extend(["weighing heart", "judgment", "maat", "osiris", "confession", "tribunal", "feather"])

    # Egyptian afterlife / Duat
    if any(w in q_lower for w in ["duat", "underworld", "egyptian afterlife", "sekhem", "abydos", "heliopolis"]):
        keywords.extend(["duat", "underworld", "osiris", "afterlife", "egyptian", "sekhem", "abydos"])

    # Egyptian transformations
    if any(w in q_lower for w in ["benu bird", "phoenix", "transformation into", "shabti", "ba soul", "ka soul"]):
        keywords.extend(["benu", "phoenix", "transformation", "shabti", "ba", "ka", "falcon"])

    # Ancient Egypt / Kemet
    if any(w in q_lower for w in ["ancient egypt", "kemet", "egyptian", "pharaoh", "thebes", "memphis"]):
        keywords.extend(["egypt", "kemet", "pharaoh", "ra", "osiris", "pyramid", "nile"])

    # Resurrection / dead rising theme
    if any(w in q_lower for w in ["resurrection", "rise from the dead", "dead rise", "dead rising", "rise from the grave"]):
        keywords.extend(["resurrection", "rise from the dead", "dead will rise", "bones live", "bones remember"])

    # Throne + rainbow vision
    if "throne" in q_lower and "rainbow" in q_lower:
        keywords.extend(["throne", "rainbow", "throne of god", "vision of the throne"])

    # Bones theme
    if "dry bones" in q_lower or "bones live" in q_lower or "bones remember" in q_lower:
        keywords.extend(["dry bones", "bones live", "bones remember", "breath entered"])

    # PRIORITY: Seven Nations / Dare ra Petros / Dare ra Jakopo / Two Courts
    if any(w in q_lower for w in ["seven nations", "7 nations", "dare ra petros", "dare ra jakopo", "two courts", "twelve men", "seven men"]):
        keywords.extend(["seven nations", "germany", "america", "britain", "ethiopia", "israel", "australia", "india", "dare ra petros", "dare ra jakopo", "kenya", "zimbabwe"])
        return list(set(keywords))
    
    # PRIORITY: RANGA / Sacred Locations
    if any(w in q_lower for w in ["ranga", "sacred location", "kenya ranga", "zimbabwe ranga"]):
        keywords.extend(["ranga", "kenya", "zimbabwe", "sacred location", "nairobi", "mutare", "baba johani"])
        return list(set(keywords))
    
    # PRIORITY: Imba ya Mwari / Temple of God / House of God
    if any(w in q_lower for w in ["imba ya mwari", "imba yamwari", "house of god", "temple of god", "church of god"]):
        keywords.extend(["imba ya mwari", "temple", "church", "house of god", "sacred place", "abasid 1841", "six pillars"])
        return list(set(keywords))
    
    # PRIORITY: Ring of Solomon / Menelik / Sidhi
    if any(w in q_lower for w in ["ring of solomon", "solomon ring", "menelik", "sidhi"]):
        keywords.extend(["ring of solomon", "menelik", "sidhi", "sheba", "ethiopia", "ark", "covenant", "abasid 1841"])
        return list(set(keywords))
    
    # PRIORITY: Shekinah / Eve / Mother themes from Gospel of God
    if any(w in q_lower for w in ["shekinah", "eve", "mother earth", "imba yechirangano", "virgins of heaven"]):
        keywords.extend(["shekinah", "eve", "mother", "imba yechirangano", "virgins", "sacred feminine", "creation"])
        return list(set(keywords))
    
    # PRIORITY: Germany / H. Germany and Co / Bank Street India
    if any(w in q_lower for w in ["germany", "h. germany", "bank street", "india journey", "leading carts"]):
        keywords.extend(["germany", "h. germany", "bank street", "india", "eight months", "carts", "baba johani", "journey"])
        return list(set(keywords))

    # Baba Johani / Johane Masowe theme (comprehensive)
    if any(w in q_lower for w in ["baba johani", "baba johane", "baba johanne", "johane masowe", "johani masowe", "gandanzara", "mugwambi", "shoniwa"]):
        keywords.extend(["baba johani", "baba johanne", "johane masowe", "birth", "gandanzara", "mugwambi", "1914", "signs", "portents", "ministry", "masowe", "nhoroondo"])

    # Birth of Baba Johanne
    if any(w in q_lower for w in ["born 1914", "october 1914", "birth of baba", "when was baba born", "baba birth"]):
        keywords.extend(["birth", "1914", "october 1", "gandanzara", "mugwambi", "shoniwa", "earthquake", "mai efi"])

    # Holy Spirit descent / spiritual birth
    if any(w in q_lower for w in ["1932", "1933", "holy spirit", "spiritual birth", "norton", "marimba", "lightning", "chipukutu"]):
        keywords.extend(["holy spirit", "1932", "norton", "marimba", "lightning", "spiritual birth", "chipukutu", "sixpence"])

    # Death of Baba Johanne
    if any(w in q_lower for w in ["death of baba", "baba died", "when did baba die", "1973", "ndola", "zambia", "september 1973"]):
        keywords.extend(["death", "1973", "september", "ndola", "zambia", "departure", "completion"])

    # Baba Johanne miracles
    if any(w in q_lower for w in ["baba miracle", "eagle", "flying", "zaka", "blind policeman", "singing staff", "tsvimbo"]):
        keywords.extend(["miracle", "eagle", "flying", "zaka", "blind", "policeman", "singing staff", "tsvimbo"])

    # Baba Johanne teachings and laws
    if any(w in q_lower for w in ["four laws", "mitemo", "mitemo mina", "baba teaching", "white garments", "white robes"]):
        keywords.extend(["laws", "mitemo", "four laws", "teaching", "white garments", "purity", "commandments"])

    # Port Elizabeth ministry
    if any(w in q_lower for w in ["port elizabeth", "south africa ministry", "1951"]):
        keywords.extend(["port elizabeth", "1951", "south africa", "migration", "church growth"])

    # Prophecies of Baba Johanne
    if any(w in q_lower for w in ["baba prophecy", "baba prophec", "bulls", "liberation war", "chimurenga", "new land", "nyika itsva"]):
        keywords.extend(["prophecy", "bulls", "liberation", "war", "new land", "nyika itsva", "vision"])

    # Mother Efi / Mai Efi
    if any(w in q_lower for w in ["mai efi", "mother efi", "saziso", "baba mother"]):
        keywords.extend(["mai efi", "mother", "saziso", "pregnancy", "visions", "angel", "dish"])

    # Joshua 1:8 vision
    if any(w in q_lower for w in ["joshua 1:8", "joshua vision", "ten commandments", "book of life"]):
        keywords.extend(["joshua 1:8", "vision", "mutare", "1967", "ten commandments", "book of life", "salvation"])

    # East Africa ministry
    if any(w in q_lower for w in ["kenya", "nairobi", "tanzania", "arusha", "dar es salaam", "east africa"]):
        keywords.extend(["kenya", "nairobi", "tanzania", "arusha", "dar es salaam", "1963", "1964", "east africa", "ministry"])

    # Zambia ministry and death
    if any(w in q_lower for w in ["zambia", "lusaka", "ndola", "copper belt"]):
        keywords.extend(["zambia", "lusaka", "ndola", "1973", "death", "departure", "funeral"])

    # Botswana ministry
    if any(w in q_lower for w in ["botswana", "moroka", "gaborone"]):
        keywords.extend(["botswana", "moroka", "ministry", "border", "travel"])

    # Liberation war / Chimurenga prophecy
    if any(w in q_lower for w in ["liberation", "chimurenga", "independence", "rhodesia", "war prophecy"]):
        keywords.extend(["liberation", "chimurenga", "bulls", "prophecy", "rhodesia", "independence", "mozambique"])

    # 1973 events / funeral / transition
    if any(w in q_lower for w in ["funeral", "burial", "1973", "transition", "succession"]):
        keywords.extend(["1973", "funeral", "burial", "ndola", "september", "death", "transition"])

    # Nhoroondo chronicle specific
    if any(w in q_lower for w in ["nhoroondo", "chronicle", "history of baba", "life story"]):
        keywords.extend(["nhoroondo", "chronicle", "history", "baba johanne", "masowe", "life events"])

    # Judgment day general
    if any(w in q_lower for w in ["day of judgment", "day of judgement", "qiyamah", "yawm al-qiyamah"]):
        keywords.extend(["day of judgment", "raising of the dead"])

    if "prayer" in q_lower:
        keywords.append("prayer")

    if "identity" in q_lower or "who am i" in q_lower:
        keywords.append("identity")

    # Crying / tears / emotions theme
    if any(w in q_lower for w in ["cry", "crying", "tears", "weep", "weeping", "sad", "sadness", "grief", "mourn", "mourning"]):
        keywords.extend(["tears", "weep", "cry", "water", "heart", "sorrow", "comfort", "mercy"])

    # Emotions / feelings / balance theme
    if any(w in q_lower for w in ["emotion", "feeling", "angry", "anger", "fear", "afraid", "anxiety", "depressed", "pain", "hurt"]):
        keywords.extend(["balance", "heart", "spirit", "fire", "water", "mercy", "peace"])

    # Memory / ancestors / history
    if any(w in q_lower for w in ["memory", "remember", "ancestors", "history", "past"]):
        keywords.extend(["memory", "remember", "ancestors", "bones", "spirit", "return"])

    # Creation / beginning / genesis
    if any(w in q_lower for w in ["creation", "beginning", "genesis", "first", "origin"]):
        keywords.extend(["creation", "beginning", "first", "light", "darkness", "word"])

    # ---------------------------------
    # FALLBACK: Extract meaningful words from question
    # ---------------------------------
    if not keywords:
        import re
        tokens = re.split(r"[^a-zA-Z0-9]+", q_lower)
        meaningful = [
            t for t in tokens 
            if t and len(t) > 2 and t not in STOPWORDS
        ]
        keywords.extend(meaningful[:6])

    # Deduplicate
    seen = set()
    out: List[str] = []
    for k in keywords:
        k = (k or "").strip().lower()
        if not k:
            continue
        if k not in seen:
            seen.add(k)
            out.append(k)

    return out


# -----------------------------
# FORMATTING
# -----------------------------

def _format_entry(entry: SourceEntry) -> str:
    """
    Turn a SourceEntry into a single line for the House of Wisdom panel.
    """
    label = entry.tradition
    if entry.ref:
        label = f"{entry.tradition} – {entry.ref}"

    snippet = entry.text.strip().replace("\n", " ")
    if len(snippet) > 180:
        snippet = snippet[:177].rstrip() + "…"

    return f"{label}: {snippet}"


def _filter_by_tradition(entries: List[SourceEntry], trad: str) -> List[SourceEntry]:
    """
    Pick only entries from a given tradition (case-insensitive).
    """
    t = trad.upper()
    return [e for e in entries if (e.tradition or "").upper() == t]


# -----------------------------
# MAIN ENTRYPOINT
# -----------------------------

def gather_witnesses(question: str, max_sources: int = 8) -> List[str]:
    """
    Build witness lines for the UI Sources panel.

    Uses AI-powered semantic understanding to find witnesses that are
    genuinely relevant to the question's meaning, not just keyword matches.

    Falls back to keyword matching if semantic search fails.

    ORDER (strict):
      1) SCROLL
      2) MASOWE
      3) PAPYRUS OF ANI
      4) BIBLE
      5) TORAH
      6) QURAN
      7) ASTRONOMY / ECLIPSES

    If nothing is found, returns a small fallback list.
    """
    q_raw = (question or "").strip()
    if not q_raw:
        return []

    # ═══════════════════════════════════════════════════════════════════
    # PRIMARY: Try the 7 Planets router first (most organized source)
    # ═══════════════════════════════════════════════════════════════════
    if HAS_PLANET_ROUTER and fetch_from_planets:
        try:
            planet_result = fetch_from_planets(q_raw)
            planet_witnesses = []
            
            if planet_result.get("math_result"):
                planet_witnesses.append(f"VENUS (SCIENCE): {planet_result['math_result']}")
            
            if planet_result.get("science_search"):
                science_data = planet_result["science_search"]
                if isinstance(science_data, str):
                    planet_witnesses.append(f"VENUS (SCIENCE): {science_data}")
                else:
                    planet_witnesses.append("VENUS (SCIENCE): This is a factual/scientific question. Answer with known facts.")
            
            for scroll in planet_result.get("scrolls", [])[:max_sources - len(planet_witnesses)]:
                planet_name = scroll.get("planet", "UNKNOWN")
                text = scroll.get("text", "")[:400]
                if text:
                    planet_witnesses.append(f"{planet_name}: {text}")
            
            if planet_witnesses:
                if planet_result.get("math_result") or planet_result.get("science_search"):
                    print(f"[WITNESS] Using Planet Router (math/science): {len(planet_witnesses)} witnesses")
                    return planet_witnesses
                elif len(planet_witnesses) >= 2:
                    print(f"[WITNESS] Using Planet Router: {len(planet_witnesses)} witnesses from {[PLANETS[p]['name'] for p in planet_result.get('planets_consulted', [])]}")
                    return planet_witnesses
        except Exception as e:
            print(f"[WITNESS] Planet router error, falling back: {e}")

    # ═══════════════════════════════════════════════════════════════════
    # FALLBACK: Try semantic witness selection (AI-powered understanding)
    # ═══════════════════════════════════════════════════════════════════
    if HAS_SEMANTIC_WITNESS and get_semantic_witnesses:
        try:
            semantic_witnesses = get_semantic_witnesses(q_raw, max_witnesses=max_sources)
            if semantic_witnesses and len(semantic_witnesses) >= 2:
                print(f"[WITNESS] Using semantic witnesses: {len(semantic_witnesses)} found")
                return semantic_witnesses
        except Exception as e:
            print(f"[WITNESS] Semantic witness error, falling back: {e}")

    # Fallback to keyword-based matching
    q_norm = _normalise_question(q_raw)
    keywords = _extract_keywords(q_norm)

    witnesses: List[str] = []
    seen_lines = set()

    # Strict display hierarchy
    layers = [
        "ABASID 1841 SCROLL",
        "MASOWE",
        "PAPYRUS OF ANI",
        "BIBLE",
        "TORAH",
        "QURAN",
        "ASTRONOMY / ECLIPSES",
    ]

    # We query multiple keywords, but we always add in strict layer order.
    for kw in keywords:
        try:
            # Important: cap per tradition prevents MASOWE dominating.
            results = search_sources(kw, max_results=60, per_tradition_cap=3)
        except Exception:
            continue

        for layer in layers:
            filtered = _filter_by_tradition(results, layer)
            for e in filtered:
                line = _format_entry(e)
                if line in seen_lines:
                    continue
                seen_lines.add(line)
                witnesses.append(line)
                if len(witnesses) >= max_sources:
                    return witnesses

    # ---------------------------------
    # FALLBACKS (if nothing found)
    # ---------------------------------
    if not witnesses:
        q_lower = q_norm.lower()

        if "memory" in q_lower or "bones" in q_lower:
            generic = [
                "ABASID 1841 SCROLL – Book of Memory: speaks of bones remembering truth and identity returning before the dust claims the body.",
                "MASOWE: teaches that the grave is the body and the spirit returns to God before burial.",
                "BIBLE: speaks of the raising of the dead and the spiritual body.",
                "QURAN: teaches that God gathers and raises the dead for judgment.",
            ]
            return generic[:max_sources]

        generic = [
            "ABASID 1841 SCROLL: the Scrolls of ABASID 1841 are consulted as the first witness.",
            "MASOWE: Baba Johani memory is consulted as ancestral witness.",
            "BIBLE / TORAH / QURAN: scripture witnesses are consulted when relevant.",
        ]
        return generic[:max_sources]

    return witnesses