"""
Fuzzy matching utilities for handling typos and spelling variations in lexicons.

Supports:
- Levenshtein distance for close matches
- Common vowel/consonant substitutions
- Missing/extra character tolerance
"""

from typing import Optional, List, Tuple, Dict


def levenshtein_distance(s1: str, s2: str) -> int:
    """Calculate the Levenshtein distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]


def similarity_ratio(s1: str, s2: str) -> float:
    """
    Calculate similarity ratio between two strings (0.0 to 1.0).
    Higher is more similar.
    """
    if not s1 or not s2:
        return 0.0
    
    distance = levenshtein_distance(s1.lower(), s2.lower())
    max_len = max(len(s1), len(s2))
    return 1.0 - (distance / max_len)


def normalize_for_fuzzy(text: str) -> str:
    """Normalize text for fuzzy matching."""
    return ' '.join(text.lower().strip().split())


def find_closest_match(
    query: str, 
    candidates: List[str], 
    threshold: float = 0.75,
    max_results: int = 1
) -> List[Tuple[str, float]]:
    """
    Find the closest matching strings from a list of candidates.
    
    Args:
        query: The input string to match
        candidates: List of possible matches
        threshold: Minimum similarity ratio (0.0 to 1.0)
        max_results: Maximum number of results to return
    
    Returns:
        List of (match, similarity_ratio) tuples, sorted by similarity
    """
    normalized_query = normalize_for_fuzzy(query)
    matches = []
    
    for candidate in candidates:
        normalized_candidate = normalize_for_fuzzy(candidate)
        
        # Try exact match first
        if normalized_query == normalized_candidate:
            matches.append((candidate, 1.0))
            continue
        
        # Try without spaces (compound words)
        query_no_spaces = normalized_query.replace(' ', '')
        candidate_no_spaces = normalized_candidate.replace(' ', '')
        
        if query_no_spaces == candidate_no_spaces:
            matches.append((candidate, 0.99))
            continue
        
        # Calculate similarity
        ratio = similarity_ratio(normalized_query, normalized_candidate)
        
        # Also try without spaces for compound words
        ratio_no_spaces = similarity_ratio(query_no_spaces, candidate_no_spaces)
        best_ratio = max(ratio, ratio_no_spaces)
        
        if best_ratio >= threshold:
            matches.append((candidate, best_ratio))
    
    # Sort by similarity (highest first)
    matches.sort(key=lambda x: x[1], reverse=True)
    
    return matches[:max_results]


def fuzzy_lookup(
    query: str,
    lexicon: Dict,
    threshold: float = 0.75
) -> Optional[Tuple[str, any, float]]:
    """
    Look up a query in a lexicon with fuzzy matching.
    
    Args:
        query: The input string to look up
        lexicon: Dictionary to search in
        threshold: Minimum similarity for a match
    
    Returns:
        Tuple of (matched_key, value, similarity) or None
    """
    normalized_query = normalize_for_fuzzy(query)
    
    # Try exact match first
    if normalized_query in lexicon:
        return (normalized_query, lexicon[normalized_query], 1.0)
    
    # Try without spaces
    query_no_spaces = normalized_query.replace(' ', '')
    if query_no_spaces in lexicon:
        return (query_no_spaces, lexicon[query_no_spaces], 0.99)
    
    # Fuzzy search
    matches = find_closest_match(query, list(lexicon.keys()), threshold)
    
    if matches:
        best_match, similarity = matches[0]
        return (best_match, lexicon[normalize_for_fuzzy(best_match)], similarity)
    
    return None


def suggest_correction(query: str, candidates: List[str], threshold: float = 0.6) -> Optional[str]:
    """
    Suggest a spelling correction for a query.
    
    Returns a suggestion message if a close match is found but not exact.
    """
    normalized_query = normalize_for_fuzzy(query)
    
    # Check if exact match exists
    for candidate in candidates:
        if normalize_for_fuzzy(candidate) == normalized_query:
            return None  # Exact match, no correction needed
    
    # Find close matches
    matches = find_closest_match(query, candidates, threshold, max_results=3)
    
    if not matches:
        return None
    
    best_match, similarity = matches[0]
    
    # Only suggest if it's close but not exact
    if 0.6 <= similarity < 0.99:
        if len(matches) == 1:
            return f"Did you mean '{best_match}'?"
        else:
            suggestions = [m[0] for m in matches[:3]]
            return f"Did you mean: {', '.join(suggestions)}?"
    
    return None


# Common substitution patterns for African languages
VOWEL_SUBSTITUTIONS = {
    'a': ['e', 'o'],
    'e': ['a', 'i'],
    'i': ['e', 'y'],
    'o': ['a', 'u'],
    'u': ['o', 'w'],
}

CONSONANT_SUBSTITUTIONS = {
    'b': ['v', 'p'],
    'd': ['t'],
    'g': ['k'],
    'n': ['m', 'ng'],
    's': ['z', 'sh'],
    'z': ['s'],
    'w': ['v', 'u'],
}


def generate_variations(word: str, max_variations: int = 10) -> List[str]:
    """
    Generate common spelling variations of a word.
    Useful for pre-populating fuzzy match candidates.
    """
    variations = [word]
    word_lower = word.lower()
    
    # Vowel at end variations (e.g., johane -> johani)
    if word_lower and word_lower[-1] in VOWEL_SUBSTITUTIONS:
        for sub in VOWEL_SUBSTITUTIONS[word_lower[-1]]:
            variations.append(word_lower[:-1] + sub)
    
    # Missing first vowel (e.g., gurumwandira -> grumwandira)
    for i, char in enumerate(word_lower):
        if char in 'aeiou' and i > 0:
            variation = word_lower[:i] + word_lower[i+1:]
            if variation not in variations:
                variations.append(variation)
            break
    
    # Double letter reduction
    prev = ''
    reduced = ''
    for char in word_lower:
        if char != prev:
            reduced += char
        prev = char
    if reduced != word_lower and reduced not in variations:
        variations.append(reduced)
    
    return variations[:max_variations]
