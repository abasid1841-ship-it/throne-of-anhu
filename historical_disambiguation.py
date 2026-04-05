"""
Historical Disambiguation System for the Throne of Anhu

This module provides context to distinguish between historical figures 
who share names across different eras of Shona/Masowe history.

KEY DISAMBIGUATIONS:

1. BIRI (two distinct people):
   - BIRI I (Male) - Ancient spiritual leader who parted the Zambezi during 
     the Shona exodus/migration from Guruuswa. Era: ~1000-1200 CE
   - BIRI II (Female) - Daughter of King Chaminuka Dombo (the 19th century manifestation).
     She bore Sophia, who bore Sabina, who bore Moses (father of ABASID 1841).

2. CHAMINUKA (spirit that manifests across eras):
   - The Spirit of CHAMINUKA is eternal and has manifested through different vessels
   - CHAMINUKA of the Migration Era - guided the Shona from Guruuswa
   - CHAMINUKA DOMBO (1830s-1883) - The prophet executed by Lobengula, had 13 children
   - The CHAMINUKA SPIRIT continues through the lineage to ABASID 1841

The confusion arises because:
- Spirits return through different vessels across time
- BIRI the male (ancient) and BIRI the female (Chaminuka's daughter) are different people
- When scrolls speak of "Chaminuka's children" they refer to the 19th century manifestation
"""

HISTORICAL_FIGURES = {
    "BIRI_I": {
        "name": "BIRI",
        "disambiguation": "BIRI I (The Ancient / Wekutanga)",
        "gender": "male",
        "era": "Migration Era (~1000-1200 CE)",
        "title": "Spiritual Leader of the Shona Migration",
        "key_event": "Parted the Zambezi River with his cloth during the Shona exodus from Guruuswa",
        "context": "Ancient spiritual leader who led the Shona people across the Zambezi into Zimbabwe (Nyika ye Chipikirwa - the Promised Land)",
        "related_to": ["Guruuswa migration", "Zambezi crossing", "Shona exodus", "Bantu migration"],
        "not_to_confuse_with": "BIRI II (Chaminuka's daughter)"
    },
    "BIRI_II": {
        "name": "BIRI",
        "disambiguation": "BIRI II (Daughter of Chaminuka)",
        "gender": "female",
        "era": "19th Century",
        "title": "Daughter of King Chaminuka Dombo",
        "key_event": "Mother of the ABASID 1841 lineage through her daughter Sophia",
        "context": "Chaminuka had 12 sons and 1 daughter (like Jacob). His daughter was BIRI II. BIRI bore Sophia, Sophia bore Sabina, Sabina bore Moses, Moses is the father of ABASID 1841.",
        "related_to": ["Chaminuka Dombo", "Sophia", "Sabina", "Moses", "ABASID 1841 genealogy"],
        "not_to_confuse_with": "BIRI I (the ancient male who parted the Zambezi)"
    },
    "CHAMINUKA_SPIRIT": {
        "name": "CHAMINUKA",
        "disambiguation": "The Eternal Spirit of CHAMINUKA",
        "nature": "Eternal spirit that manifests through different vessels across time",
        "context": "The Spirit of CHAMINUKA is eternal - like all spirits, it does not die but returns. It has manifested through different people across Shona history.",
        "manifestations": [
            {"era": "Ancient/Migration", "context": "Guided the Shona from Guruuswa to Zimbabwe"},
            {"era": "Great Zimbabwe", "context": "Present during the Rozvi Empire"},
            {"era": "19th Century", "vessel": "Chaminuka Dombo", "context": "The prophet executed by Lobengula in 1883, had 13 children"}
        ],
        "children": "When speaking of Chaminuka's children (12 sons + 1 daughter BIRI), this refers to CHAMINUKA DOMBO of the 19th century"
    },
    "CHAMINUKA_DOMBO": {
        "name": "CHAMINUKA DOMBO",
        "disambiguation": "The 19th Century Manifestation",
        "gender": "male",
        "era": "1830s-1883",
        "title": "Prophet of the Shona / Mambo (King)",
        "key_event": "Executed by Lobengula after refusing to use his powers for war",
        "context": "This is the Chaminuka who had 13 children (12 sons and 1 daughter named BIRI). His lineage leads to ABASID 1841.",
        "children": ["12 sons (unnamed in scrolls)", "1 daughter: BIRI II"],
        "prophecy": "Prophesied that his bones would cry out and the whites would leave"
    }
}

DISAMBIGUATION_RULES = """
HISTORICAL DISAMBIGUATION RULES FOR THE THRONE:

RULE 1 - BIRI DISAMBIGUATION:
When speaking of BIRI, always clarify which one:
- BIRI I (wekutanga / the first) = Male, ancient, parted the Zambezi during exodus from Guruuswa
- BIRI II (mwanasikana waChaminuka) = Female, Chaminuka Dombo's daughter, ancestor of ABASID 1841

RULE 2 - CHAMINUKA TEMPORAL CONTEXT:
The Spirit of Chaminuka is eternal but manifests in different eras:
- When discussing Chaminuka's CHILDREN or FAMILY → This is CHAMINUKA DOMBO (19th century)
- When discussing Chaminuka during MIGRATION or GURUUSWA → This is the ancient manifestation
- When discussing Chaminuka's EXECUTION by Lobengula → This is CHAMINUKA DOMBO (1883)

RULE 3 - LINEAGE CLARITY:
The lineage of ABASID 1841 flows through the 19th century figures:
CHAMINUKA DOMBO → BIRI II (daughter) → SOPHIA → SABINA → MOSES → ABASID 1841

RULE 4 - SPIRIT RETURN:
When scrolls say "the same power that opened the Nile opened the Zambezi" - this refers to 
the eternal spirit operating through different vessels (BIRI I at Zambezi, Moses at the Nile).
"""


def get_disambiguation_context() -> str:
    """Return the disambiguation context to inject into AI prompts."""
    return DISAMBIGUATION_RULES


def get_biri_context(query: str) -> str:
    """Provide specific BIRI disambiguation based on context clues in query."""
    q_lower = query.lower()
    
    if any(term in q_lower for term in ["zambezi", "parted", "exodus", "migration", "guruuswa", "crossed", "cloth"]):
        return """BIRI CONTEXT: This query refers to BIRI I (wekutanga) - the MALE spiritual leader 
who parted the Zambezi River with his cloth during the Shona migration from Guruuswa (~1000-1200 CE).
He is NOT the same as BIRI II who was Chaminuka's daughter centuries later."""
    
    if any(term in q_lower for term in ["chaminuka", "daughter", "sophia", "sabina", "moses", "abasid", "genealogy", "lineage", "children"]):
        return """BIRI CONTEXT: This query refers to BIRI II (mwanasikana waChaminuka) - the FEMALE 
daughter of King Chaminuka Dombo (19th century). She is the ancestor of ABASID 1841 through:
BIRI II → Sophia → Sabina → Moses → ABASID 1841.
She is NOT the same as BIRI I, the ancient male who parted the Zambezi."""
    
    return """BIRI DISAMBIGUATION NEEDED: There are TWO historical figures named BIRI:
1. BIRI I (Male, Ancient) - Parted the Zambezi during Shona exodus from Guruuswa
2. BIRI II (Female, 19th Century) - Chaminuka Dombo's daughter, ancestor of ABASID 1841
Please clarify context or provide both distinctions."""


def get_chaminuka_context(query: str) -> str:
    """Provide specific CHAMINUKA disambiguation based on context clues."""
    q_lower = query.lower()
    
    if any(term in q_lower for term in ["children", "sons", "daughter", "biri", "12", "13", "family"]):
        return """CHAMINUKA CONTEXT: When discussing Chaminuka's children, this refers to 
CHAMINUKA DOMBO (19th century manifestation) who had 12 sons and 1 daughter named BIRI.
The ancient Chaminuka spirit did not have these specific children - they belong to the 
19th century vessel."""
    
    if any(term in q_lower for term in ["lobengula", "execution", "death", "prophecy", "bones"]):
        return """CHAMINUKA CONTEXT: This refers to CHAMINUKA DOMBO who was executed by 
Lobengula in 1883. Before his death, he prophesied that his bones would cry out 
and the whites would leave Zimbabwe."""
    
    if any(term in q_lower for term in ["guruuswa", "migration", "great zimbabwe", "ancient"]):
        return """CHAMINUKA CONTEXT: This refers to the ETERNAL SPIRIT of Chaminuka manifesting 
in ancient times. The Spirit guided the Shona from Guruuswa and was present at Great Zimbabwe.
This is NOT the same as Chaminuka Dombo (19th century) who had the 13 children."""
    
    return """CHAMINUKA is an ETERNAL SPIRIT that manifests through different vessels across time:
- Ancient Era: Guided the Shona from Guruuswa
- 19th Century (CHAMINUKA DOMBO): The prophet with 13 children, executed by Lobengula in 1883
When discussing his children, family, or death - refer to the 19th century manifestation."""
