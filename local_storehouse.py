# -*- coding: utf-8 -*-
"""
LOCAL STOREHOUSE OF THE THRONE - zero-token answers
"""

from __future__ import annotations

from typing import List, Optional

from models import ThroneResponse
from scroll_library import find_scroll_by_title_like


# -----------------------------
# HELPERS
# -----------------------------

def _match(msg: str, patterns: List[str]) -> bool:
    """Simple substring matcher (case-insensitive)."""
    msg = (msg or "").lower()
    return any(p in msg for p in patterns)


def _is_shona(language: str) -> bool:
    """Detect Shona from language code or label."""
    if not language:
        return False
    lang = language.strip().lower()
    return lang.startswith("sn") or "shona" in lang or lang.startswith("sho")


def normalize_misspellings(msg: str) -> str:
    """
    Fix a few sacred typos so queries still hit:
    chinyamatamna -> chinyamatamba, mudwedzo -> mudewedzo, etc.
    """
    q = (msg or "").lower()

    replacements = {
        "chinyamatamna": "chinyamatamba",
        "chinyamatama": "chinyamatamba",
        "mudwedzo": "mudewedzo",
        "john of masowe": "john masowe",
        "johanne masowe": "johane masowe",
    }

    for wrong, correct in replacements.items():
        if wrong in q:
            q = q.replace(wrong, correct)

    return q


# -----------------------------
# MAIN ENTRYPOINT
# -----------------------------

def match_local_storehouse(
    user_message: str,
    language: str = "en",
) -> Optional[ThroneResponse]:
    """
    Try to answer the question directly from the local storehouse.
    If no match is found, return None and let the Temple Engine handle it.
    """
    msg_raw = user_message or ""
    low = msg_raw.strip().lower()

    # ============================================================
    # 0. VIEW SCROLLS - OPENING A SCROLL (NO OPENAI)
    # ============================================================
    if low.startswith("opening scroll:"):
        title = msg_raw.split(":", 1)[1].strip() if ":" in msg_raw else ""
        if not title:
            return ThroneResponse(
                persona="RA",
                mode="outer_court",
                answer="The Scrolls tried to open, but the title was empty.",
            )

        scroll = find_scroll_by_title_like(title)
        if not scroll:
            return ThroneResponse(
                persona="RA",
                mode="outer_court",
                answer=f"The Scrolls could not find a book named '{title}'.",
            )

        verses = scroll.get("verses") or []
        body = "\n".join(str(v) for v in verses)

        text = (
            f"Opening scroll: {scroll.get('book_title') or title}\n\n"
            f"{body}"
        )

        return ThroneResponse(
            persona="RA",
            mode="outer_court",
            answer=text,
        )

    # Ignore other system/UI meta messages so they pass to Temple Engine
    if low.startswith("pin scroll:") or low.startswith("system:") or low.startswith("meta:"):
        return None

    # Normal semantic handling from here
    msg = normalize_misspellings(msg_raw)
    lang_is_shona = _is_shona(language)

    # ============================================================
    # 1. CHINYAMATAMBA · MUDEWEDZO 1933
    # ============================================================
    if _match(
        msg,
        [
            "chinyamatamba",
            "mudewedzo",
            "mudewedzo 1933",
            "1933 event",
            "tongues of fire",
            "mvura nerimi",
        ],
    ):
        if lang_is_shona:
            text = (
                "OUTER COURT (RA · ZUVA):\n"
                "Chinyamatamba, Mudewedzo, mugore ra1933, Mwari akatenderera zvakare "
                "kuvanhu vake. Zuva rakanga rakanyarara, asi pakapfuura nguva "
                "dzaingova nenguva pfupi dzemangwanani, vanhu vakanzwa sekunge mvura "
                "yava kudururwa kubva kudenga, asi hapana makore aioneka.\n\n"
                "Pakarepo Mweya Mutsvene akaburuka semarimi emoto – ‘mvura nerimi’ – "
                "uchigara pamusoro pevakadzi nevanhurume vaivepo. Muviri wavo wakazara "
                "nesimba, vamwe vachidonha, vamwe vachichema, vamwe vachiparidza pasina "
                "kudzidziswa. Chiitiko ichi chakava chisimbiso chekuti chiporofita cha "
                "Baba Johani Muwombeki chakazadziswa: kuti Mweya achadzoka nehumambo "
                "hwakasimba kupfuura kare.\n\n"
                "Kubva pazuva iri, Chinyamatamba yakava chiratidzo chekuti "
                "Imba yaMwari haichavakiwi nematombo chete – asi nemiviri "
                "yavanhu. Ndipo pakaberekwa rugwaro rako raANHU: ‘Imba yaMwari "
                "yava muMunhu.’"
            )
        else:
            text = (
                "OUTER COURT (RA · DAY):\n"
                "In Chinyamatamba, in the hills of Mudewedzo, the year 1933 became a "
                "flame written into the bones of the land. Around the ninth hour of "
                "the morning, the people gathered in simple faith. There were no big "
                "cathedrals, no golden altars – only earth, sky and expectation.\n\n"
                "Then it came. They heard a sound like water being poured out from "
                "heaven, yet no rain fell. Upon that sound the Holy Spirit descended "
                "as tongues of fire – ‘water and flame’ – resting upon the men and "
                "women there. Bodies shook, tears flowed, prophecy erupted from lips "
                "that had never been trained to preach. Thus the word of Baba Johani "
                "Muwombeki was fulfilled: the Spirit would return with greater power.\n\n"
                "From that day Chinyamatamba became a sign that the House of God is "
                "no longer a stone building far away, but the living bodies of His "
                "people. This is the root of your ANHU doctrine: ‘The House of God "
                "is now in Man.’"
            )

        return ThroneResponse(
            persona="RA",
            mode="outer_court",
            answer=text,
        )

    # ============================================================
    # 2. HOUSE OF GOD · IMBA YAMWARI
    # ============================================================
    if _match(
        msg,
        [
            "house of god",
            "imba yamwari",
            "temple of god",
            "where does god live",
            "where is the house of god",
        ],
    ):
        if lang_is_shona:
            text = (
                "OUTER COURT (RA · ZUVA):\n"
                "Imba yaMwari haisisiri hekere yakavakwa nezuva rematombo chete. "
                "Muzvinyorwa zveANHU unodzidziswa kuti: muviri wemunhu wakagadzirwa "
                "seTemberi. Mafupa ako ndiwo zvikamu zveimba, ropa rako ndiyo ropa "
                "reChibayiro, uye mweya wako ndiwo Mukati Wakachena.\n\n"
                "Kana munhu akagara achifamba muchokwadi, achiremekedza muviri wake, "
                "pfungwa dzake nemweya wake, anova Jerusalemu itsva – guta raMwari "
                "rinofamba netsoka dzemunhu. Saka mubvunzo ‘Chii chinonzi Imba "
                "yaMwari?’ unopindurwa nezuva rimwe: ‘Imba yaMwari ndiwe – kana wakabvuma "
                "chiedza, uchifamba numutemo werudo.’"
            )
        else:
            text = (
                "OUTER COURT (RA · DAY):\n"
                "The House of God is no longer a distant stone temple guarded by "
                "priests and curtains. In the ANHU Scrolls the teaching is clear: "
                "the human body was shaped as a Temple. Your bones are the beams "
                "and pillars, your blood is the covenant offering, your spirit is "
                "the Inner Court.\n\n"
                "When a person walks in truth, honours their body, mind and breath, "
                "they become the New Jerusalem – a moving city of God carried on "
                "two feet. So the question ‘What is the house of God?’ is answered "
                "with one flame: ‘You are that house, when you welcome the Light "
                "and walk in the Law of Love.’"
            )

        return ThroneResponse(
            persona="RA",
            mode="outer_court",
            answer=text,
        )

    # ============================================================
    # 3. ANHU ALPHABET · 22 LETTERS OF LIGHT
    # ============================================================
    if _match(
        msg,
        [
            "anhu alphabet",
            "22 letters of light",
            "twenty two letters of light",
            "letters of light",
            "shona alphabet of god",
        ],
    ):
        if lang_is_shona:
            text = (
                "INNER COURT (DZI · KURAYIRA):\n"
                "ANHU Alphabet ibhuku resimba – mavara makumi maviri nemaviri "
                "anobatanidza Shona neHebheru, pasi nedenga. A = 1, BA = 2, "
                "KA = 3, RA = zuva, MA = mwedzi, DA = rudo, NA = kubatana, "
                "SA = kufanana, ZI = runyararo rwekudzika, TA = ‘tiri’, "
                "VA = ‘vari’, NGU = nguva, NDA = ‘ndiri’, PA = kupa, "
                "HA = ‘handi’, GA = kuisa, SHU = mhepo, MBA = imba, "
                "NYU = mvura, CHI = ‘chii’, TO = vatongi / mhepo, "
                "NGA = nyoka / korona / denga.\n\n"
                "Mavara aya haasi mamaki chete – ndiwo masuo. Kana uchiverenga "
                "zita rako, nyika yako, kana zuva rekuzvarwa uchishandisa ANHU "
                "Alphabet, uri kuzarura gonhi rekuziva kuti wakavezwa sei "
                "mugematriya yaMwari."
            )
        else:
            text = (
                "INNER COURT (DZI · TEACHING):\n"
                "The ANHU Alphabet is a ladder of 22 flames that binds Shona sound, "
                "Hebrew number and celestial order into one body. A = 1, BA = 2, "
                "KA = 3, RA = the Sun, MA = the Moon, DA = Love, NA = Connection, "
                "SA = As / Like, ZI = Silence, TA = ‘We Are’, VA = ‘They Are’, "
                "NGU = Time, NDA = ‘I Am’, PA = Giving, HA = ‘Will Not’, "
                "GA = To Plant / Instil, SHU = Wind, MBA = House, NYU = Water, "
                "CHI = ‘What’, TO = Judges / Air, NGA = Serpent / Crown / Heaven.\n\n"
                "These are not just letters – they are gates. When you spell a name, "
                "a land or a date through this Alphabet, you are tracing how that "
                "thing is carved into the mathematics of God."
            )

        return ThroneResponse(
            persona="RA",
            mode="inner_court",
            answer=text,
        )

    # ============================================================
    # NO MATCH -> LET TEMPLE ENGINE HANDLE IT
    # ============================================================
    return None