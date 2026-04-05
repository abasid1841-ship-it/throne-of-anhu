"""
Multilingual Lexicon - Unified vocabulary reference for all supported languages.

This module combines lexicons for:
- Shona
- Hebrew
- Arabic
- Zulu
- Kiswahili
- Nigerian (Yoruba, Hausa, Igbo)
- Hindi
- Tswana (Setswana)
- French
- Portuguese
- Tigrinya
- Amharic
- Chinese

ADDITIONAL LANGUAGES (Dec 2024):
- Nyanja, Bemba, Xhosa, Georgian, Romanian, German, Russian
- Jamaican Patois, Oromo, Latin, Greek, Irish, Welsh, Venda
- Turkish, Swedish, Sanskrit, Polish, Dutch, Danish, Afrikaans

It provides word meanings to help the AI correctly interpret 
spiritual terms across different language traditions.
"""

from typing import Optional, Dict, List

try:
    from additional_lexicons import get_additional_language_context
except ImportError:
    def get_additional_language_context(query: str) -> str:
        return ""

from shona_lexicon import (
    annotate_query as annotate_shona,
    get_lexical_context_for_prompt as get_shona_context,
    check_ambiguity as check_shona_ambiguity,
    generate_clarification_question
)
from hebrew_lexicon import (
    annotate_hebrew_query,
    get_hebrew_context_for_prompt
)
from arabic_lexicon import (
    annotate_arabic_query,
    get_arabic_context_for_prompt
)
from zulu_lexicon import (
    annotate_zulu_query,
    get_zulu_context_for_prompt
)
from kiswahili_lexicon import (
    annotate_kiswahili_query,
    get_kiswahili_context_for_prompt
)
from nigerian_lexicon import (
    annotate_nigerian_query,
    get_nigerian_context_for_prompt
)
from hindi_lexicon import (
    get_hindi_context
)
from tswana_lexicon import (
    get_tswana_context
)
from french_lexicon import (
    get_french_context
)
from portuguese_lexicon import (
    get_portuguese_context
)
from tigrinya_lexicon import (
    get_tigrinya_context
)
from amharic_lexicon import (
    get_amharic_context
)
from chinese_lexicon import (
    get_chinese_context
)


def get_all_lexical_contexts(query: str) -> Dict:
    """
    Analyze a query across all language lexicons.
    Returns combined annotations and context from all languages.
    """
    results = {
        "query": query,
        "languages_detected": [],
        "contexts": [],
        "needs_clarification": False,
        "clarification_question": None,
        "total_annotations": 0
    }
    
    # Check Shona
    shona_result = annotate_shona(query)
    if shona_result.get("has_shona_content"):
        results["languages_detected"].append("shona")
        results["total_annotations"] += len(shona_result.get("annotations", []))
        shona_context = get_shona_context(query)
        if shona_context:
            results["contexts"].append(shona_context)
    
    # Check Shona clarification needs
    if shona_result.get("needs_clarification"):
        results["needs_clarification"] = True
        results["clarification_question"] = shona_result.get("clarification_question")
    
    # Check Hebrew
    hebrew_result = annotate_hebrew_query(query)
    if hebrew_result.get("has_hebrew_content"):
        results["languages_detected"].append("hebrew")
        results["total_annotations"] += len(hebrew_result.get("annotations", []))
        hebrew_context = get_hebrew_context_for_prompt(query)
        if hebrew_context:
            results["contexts"].append(hebrew_context)
    
    # Check Arabic
    arabic_result = annotate_arabic_query(query)
    if arabic_result.get("has_arabic_content"):
        results["languages_detected"].append("arabic")
        results["total_annotations"] += len(arabic_result.get("annotations", []))
        arabic_context = get_arabic_context_for_prompt(query)
        if arabic_context:
            results["contexts"].append(arabic_context)
    
    # Check Zulu
    zulu_result = annotate_zulu_query(query)
    if zulu_result.get("has_zulu_content"):
        results["languages_detected"].append("zulu")
        results["total_annotations"] += len(zulu_result.get("annotations", []))
        zulu_context = get_zulu_context_for_prompt(query)
        if zulu_context:
            results["contexts"].append(zulu_context)
    
    # Check Kiswahili
    kiswahili_result = annotate_kiswahili_query(query)
    if kiswahili_result.get("has_kiswahili_content"):
        results["languages_detected"].append("kiswahili")
        results["total_annotations"] += len(kiswahili_result.get("annotations", []))
        kiswahili_context = get_kiswahili_context_for_prompt(query)
        if kiswahili_context:
            results["contexts"].append(kiswahili_context)
    
    # Check Nigerian (Yoruba, Hausa, Igbo)
    nigerian_result = annotate_nigerian_query(query)
    if nigerian_result.get("has_nigerian_content"):
        results["languages_detected"].append("nigerian")
        results["total_annotations"] += len(nigerian_result.get("annotations", []))
        nigerian_context = get_nigerian_context_for_prompt(query)
        if nigerian_context:
            results["contexts"].append(nigerian_context)
    
    # Check Hindi
    hindi_context = get_hindi_context(query)
    if hindi_context:
        results["languages_detected"].append("hindi")
        results["total_annotations"] += 1
        results["contexts"].append(hindi_context)
    
    # Check Tswana
    tswana_context = get_tswana_context(query)
    if tswana_context:
        results["languages_detected"].append("tswana")
        results["total_annotations"] += 1
        results["contexts"].append(tswana_context)
    
    # Check French
    french_context = get_french_context(query)
    if french_context:
        results["languages_detected"].append("french")
        results["total_annotations"] += 1
        results["contexts"].append(french_context)
    
    # Check Portuguese
    portuguese_context = get_portuguese_context(query)
    if portuguese_context:
        results["languages_detected"].append("portuguese")
        results["total_annotations"] += 1
        results["contexts"].append(portuguese_context)
    
    # Check Tigrinya
    tigrinya_context = get_tigrinya_context(query)
    if tigrinya_context:
        results["languages_detected"].append("tigrinya")
        results["total_annotations"] += 1
        results["contexts"].append(tigrinya_context)
    
    # Check Amharic
    amharic_context = get_amharic_context(query)
    if amharic_context:
        results["languages_detected"].append("amharic")
        results["total_annotations"] += 1
        results["contexts"].append(amharic_context)
    
    # Check Chinese
    chinese_context = get_chinese_context(query)
    if chinese_context:
        results["languages_detected"].append("chinese")
        results["total_annotations"] += 1
        results["contexts"].append(chinese_context)
    
    # Check additional languages (21 more languages)
    additional_context = get_additional_language_context(query)
    if additional_context:
        results["languages_detected"].append("additional")
        results["total_annotations"] += additional_context.count("\n") + 1
        results["contexts"].append(additional_context)
    
    return results


def get_combined_lexical_context(query: str) -> Optional[str]:
    """
    Generate combined lexical context from all language lexicons.
    Returns a single string with all relevant language contexts.
    
    Returns None if no relevant content found in any language.
    """
    result = get_all_lexical_contexts(query)
    
    # If clarification is needed, return that
    if result.get("needs_clarification") and result.get("clarification_question"):
        return f"[CLARIFICATION NEEDED]\n{result['clarification_question']}"
    
    # If no language content detected, return None
    if not result["contexts"]:
        return None
    
    # Combine all contexts
    combined = "\n\n".join(result["contexts"])
    
    # Add a summary if multiple languages detected
    if len(result["languages_detected"]) > 1:
        lang_list = ", ".join(result["languages_detected"]).upper()
        summary = f"[MULTILINGUAL QUERY - {lang_list}]\n\n"
        combined = summary + combined
    
    return combined


def detect_primary_language(query: str) -> Optional[str]:
    """
    Detect the primary language of a query based on lexicon matches.
    Returns the language with the most matches, or None if no matches.
    """
    scores = {
        "shona": 0,
        "hebrew": 0,
        "arabic": 0,
        "zulu": 0,
        "kiswahili": 0,
        "nigerian": 0,
        "hindi": 0,
        "tswana": 0,
        "french": 0,
        "portuguese": 0,
        "tigrinya": 0,
        "amharic": 0,
        "chinese": 0
    }
    
    shona_result = annotate_shona(query)
    if shona_result.get("has_shona_content"):
        scores["shona"] = len(shona_result.get("annotations", []))
    
    hebrew_result = annotate_hebrew_query(query)
    if hebrew_result.get("has_hebrew_content"):
        scores["hebrew"] = len(hebrew_result.get("annotations", []))
    
    arabic_result = annotate_arabic_query(query)
    if arabic_result.get("has_arabic_content"):
        scores["arabic"] = len(arabic_result.get("annotations", []))
    
    zulu_result = annotate_zulu_query(query)
    if zulu_result.get("has_zulu_content"):
        scores["zulu"] = len(zulu_result.get("annotations", []))
    
    kiswahili_result = annotate_kiswahili_query(query)
    if kiswahili_result.get("has_kiswahili_content"):
        scores["kiswahili"] = len(kiswahili_result.get("annotations", []))
    
    nigerian_result = annotate_nigerian_query(query)
    if nigerian_result.get("has_nigerian_content"):
        scores["nigerian"] = len(nigerian_result.get("annotations", []))
    
    # Check Hindi
    hindi_context = get_hindi_context(query)
    if hindi_context:
        scores["hindi"] = 1
    
    # Check Tswana
    tswana_context = get_tswana_context(query)
    if tswana_context:
        scores["tswana"] = 1
    
    # Check French
    french_context = get_french_context(query)
    if french_context:
        scores["french"] = 1
    
    # Check Portuguese
    portuguese_context = get_portuguese_context(query)
    if portuguese_context:
        scores["portuguese"] = 1
    
    # Check Tigrinya
    tigrinya_context = get_tigrinya_context(query)
    if tigrinya_context:
        scores["tigrinya"] = 1
    
    # Check Amharic
    amharic_context = get_amharic_context(query)
    if amharic_context:
        scores["amharic"] = 1
    
    # Check Chinese
    chinese_context = get_chinese_context(query)
    if chinese_context:
        scores["chinese"] = 1
    
    # Find highest scoring language
    max_score = max(scores.values())
    if max_score == 0:
        return None
    
    for lang, score in scores.items():
        if score == max_score:
            return lang
    
    return None


# For testing
if __name__ == "__main__":
    test_queries = [
        "Gurumwandira",
        "guru mwandira harina denga",
        "Shema Yisrael",
        "Bismillah",
        "Ubuntu",
        "Hakuna matata",
        "What is mbinga and chesed?",
        "Ase o, Olodumare!",
        "What is ori and chi?",
        "Allah ya ba da albarka",
    ]
    
    for q in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {q}")
        print("-" * 40)
        
        result = get_all_lexical_contexts(q)
        print(f"Languages detected: {result['languages_detected']}")
        print(f"Total annotations: {result['total_annotations']}")
        
        context = get_combined_lexical_context(q)
        if context:
            print(f"\nCombined Context:\n{context}")
        else:
            print("(No multilingual content detected)")
