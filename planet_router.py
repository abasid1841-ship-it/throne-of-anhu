"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║              THE 7 PLANETS · STOREHOUSES OF WISDOM                            ║
║                 Orbiting RA ☀️ like the Menorah                                ║
╚═══════════════════════════════════════════════════════════════════════════════╝

The Planet Router is the MESSENGER (like Mercury/Thoth) that:
1. Receives a query from RA
2. Determines which Planet(s) hold the answer
3. Runs to the correct storehouse
4. Returns with the relevant scrolls

THE 7 PLANETS:
1. SATURN (TIME) - Holy scriptures: Bible, Quran, Torah, Gita, Kebra Negast
2. JUPITER (KING) - ABASID scrolls: The King's own writings
3. MARS (ARMY) - Reserved for future teachings
4. EARTH - Baba Johane & Masowe history
5. VENUS (SCIENCE) - Science, math, astronomy, calculator
6. MERCURY (ANI) - Papyrus of Ani, Book of the Dead
7. MOON (ZIMBABWE) - Shona culture, Zimbabwe history
"""

import os
import json
import math
import re
import httpx
from typing import List, Dict, Tuple, Optional
from openai import OpenAI

PLANETS = {
    1: {
        "name": "SATURN",
        "domain": "TIME · SCRIPTURES",
        "folder": "sources/planet_1_saturn_scriptures",
        "keywords": ["bible", "jesus", "christ", "quran", "muhammad", "allah", "torah", "moses", "jehovah", "gita", "krishna", "selassie", "menelyk", "kebra", "scripture", "verse", "chapter", "gospel", "psalm", "proverb", "genesis", "exodus", "revelation", "surah", "ayah"],
        "description": "Holy scriptures from major religions"
    },
    2: {
        "name": "JUPITER", 
        "domain": "KING · ABASID",
        "folder": "sources/planet_2_jupiter_abasid",
        "keywords": ["abasid", "1841", "asaraa", "pillar", "anhu", "throne", "ngu", "logos", "remembrance", "chamhembe", "mission", "time is", "word is", "risen seeds", "asar", "cyrus", "christos", "yesu", "trinity", "calendar", "truth", "laws", "codex", "genealogy", "geneology", "lineage", "ancestry", "bloodline", "chaminuka", "biri", "sophia", "sabina"],
        "description": "The King's scrolls - ABASID 1841 teachings"
    },
    3: {
        "name": "MARS",
        "domain": "ARMY · WARRIORS",
        "folder": "sources/planet_3_mars_army",
        "keywords": ["army", "warrior", "soldier", "battle", "fight", "defend"],
        "description": "Reserved for future warrior teachings"
    },
    4: {
        "name": "EARTH",
        "domain": "MASOWE · BABA JOHANE",
        "folder": "sources/planet_4_earth_masowe",
        "keywords": ["johane", "johani", "masowe", "marange", "mapostori", "vapostori", "apostolic", "wilderness", "dare", "petros", "jakopo", "ranga", "imba ya mwari", "church of god", "seven nations", "germany", "white garment", "shaving", "baptism", "12 men", "hosanna", "pentecost", "marimba"],
        "description": "Baba Johane Masowe history and teachings"
    },
    5: {
        "name": "VENUS",
        "domain": "SCIENCE · KNOWLEDGE",
        "folder": "sources/planet_5_venus_science",
        "keywords": ["science", "math", "calculate", "square root", "diameter", "astronomy", "cosmology", "biology", "physics", "chemistry", "geometry", "pyramid", "planet", "moon", "sun", "star", "liver", "heart", "body", "organ", "medicine", "paracetamol", "surgery", "doctor", "number", "formula", "equation", "percent", "distance", "speed", "light", "gravity", "atom", "cell", "dna", "evolution", "universe", "galaxy"],
        "description": "Science, mathematics, astronomy, general knowledge"
    },
    6: {
        "name": "MERCURY",
        "domain": "ANI · THOTH · SCRIBE",
        "folder": "sources/planet_6_mercury_ani",
        "keywords": ["ani", "thoth", "papyrus", "book of dead", "egypt", "egyptian", "weighing", "heart", "feather", "maat", "judgment", "osiris", "isis", "horus", "anubis", "ra", "amen", "karnak", "luxor", "pharaoh", "pyramid", "hieroglyph", "spell", "chapter", "coming forth"],
        "description": "Papyrus of Ani, Egyptian spirituality"
    },
    7: {
        "name": "MOON",
        "domain": "ZIMBABWE · SHONA",
        "folder": "sources/planet_7_moon_zimbabwe",
        "keywords": ["shona", "zimbabwe", "dzimbabwe", "munhumutapa", "great zimbabwe", "rozvi", "changamire", "mwene", "nyanga", "mapungubwe", "ancestor", "mhondoro", "svikiro", "mudzimu", "sekuru", "mbuya", "bira", "nhare", "mbira", "chimurenga", "nehanda", "kaguvi", "lobengula", "mzilikazi"],
        "description": "Shona culture, Zimbabwe history, ancestors"
    }
}


def get_openai_client():
    """Get OpenAI client for routing decisions."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)


def keyword_match_planets(query: str) -> List[int]:
    """
    Fast keyword-based routing to find relevant planets.
    Returns list of planet numbers that match.
    """
    query_lower = query.lower()
    matched = []
    
    for planet_num, planet in PLANETS.items():
        for keyword in planet["keywords"]:
            if keyword in query_lower:
                matched.append(planet_num)
                break
    
    return matched if matched else [2]


def ai_route_to_planets(query: str) -> List[int]:
    """
    Use AI to determine which planet(s) should handle this query.
    Falls back to keyword matching if AI fails.
    """
    client = get_openai_client()
    if not client:
        return keyword_match_planets(query)
    
    try:
        planet_desc = "\n".join([
            f"{num}. {p['name']} ({p['domain']}): {p['description']}"
            for num, p in PLANETS.items()
        ])
        
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            temperature=0.1,
            max_tokens=50,
            messages=[
                {"role": "system", "content": f"""You route queries to the correct storehouse. 
                
THE 7 PLANETS:
{planet_desc}

Given a query, return ONLY the planet number(s) that should answer it.
Format: comma-separated numbers, e.g., "2,4" or just "5"
If unsure, default to "2" (ABASID scrolls).
For math/science/body/medicine questions, return "5".
For scripture quotes, return "1".
For Baba Johane/Masowe, return "4".
For Egyptian/Ani, return "6"."""},
                {"role": "user", "content": query}
            ]
        )
        
        result = response.choices[0].message.content.strip()
        numbers = [int(n.strip()) for n in result.split(",") if n.strip().isdigit()]
        valid_numbers = [n for n in numbers if n in PLANETS]
        
        if valid_numbers:
            print(f"[ROUTER] AI routed to planets: {valid_numbers}")
            return valid_numbers
        
    except Exception as e:
        print(f"[ROUTER] AI routing failed: {e}")
    
    return keyword_match_planets(query)


def load_planet_scrolls(planet_num: int) -> List[Dict]:
    """Load all scrolls from a planet's folder."""
    planet = PLANETS.get(planet_num)
    if not planet:
        return []
    
    folder = planet["folder"]
    scrolls = []
    
    if not os.path.exists(folder):
        return []
    
    for filename in os.listdir(folder):
        if filename.endswith(".json"):
            filepath = os.path.join(folder, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        scrolls.extend(data)
                    elif isinstance(data, dict):
                        if "verses" in data:
                            scrolls.extend(data["verses"])
                        elif "scrolls" in data:
                            scrolls.extend(data["scrolls"])
                        elif "chapters" in data:
                            for chapter in data["chapters"]:
                                if "verses" in chapter:
                                    scrolls.extend(chapter["verses"])
                        else:
                            scrolls.append(data)
            except Exception as e:
                print(f"[ROUTER] Error loading {filepath}: {e}")
    
    return scrolls


def search_planet(planet_num: int, query: str, limit: int = 5) -> List[Dict]:
    """
    Search a specific planet for relevant scrolls.
    Returns top matches based on keyword overlap.
    """
    scrolls = load_planet_scrolls(planet_num)
    query_words = set(query.lower().split())
    
    scored = []
    for scroll in scrolls:
        text = ""
        if isinstance(scroll, dict):
            text = scroll.get("text", "") or scroll.get("content", "") or scroll.get("verse", "") or str(scroll)
        else:
            text = str(scroll)
        
        text_lower = text.lower()
        score = sum(1 for word in query_words if word in text_lower)
        
        if score > 0:
            scored.append((score, scroll, text))
    
    scored.sort(key=lambda x: x[0], reverse=True)
    return [{"scroll": s[1], "text": s[2][:500]} for s in scored[:limit]]


def handle_math_query(query: str) -> Optional[str]:
    """
    Handle mathematical calculations for Planet 5 (Venus).
    """
    query_lower = query.lower()
    
    sqrt_match = re.search(r'square root (?:of )?(\d+(?:\.\d+)?)', query_lower)
    if sqrt_match:
        num = float(sqrt_match.group(1))
        result = math.sqrt(num)
        return f"The square root of {int(num) if num == int(num) else num} is {result:.6f}"
    
    diameter_patterns = {
        "moon": "The diameter of the Moon is approximately 3,474 km (2,159 miles).",
        "sun": "The diameter of the Sun is approximately 1,392,700 km (865,370 miles).",
        "earth": "The diameter of Earth is approximately 12,742 km (7,918 miles).",
        "mars": "The diameter of Mars is approximately 6,779 km (4,212 miles).",
        "jupiter": "The diameter of Jupiter is approximately 139,820 km (86,881 miles).",
        "saturn": "The diameter of Saturn is approximately 116,460 km (72,366 miles).",
        "venus": "The diameter of Venus is approximately 12,104 km (7,521 miles).",
        "mercury": "The diameter of Mercury is approximately 4,879 km (3,032 miles).",
    }
    
    for body, answer in diameter_patterns.items():
        if body in query_lower and "diameter" in query_lower:
            return answer
    
    calc_match = re.search(r'(\d+(?:\.\d+)?)\s*[\+\-\*\/\^]\s*(\d+(?:\.\d+)?)', query)
    if calc_match:
        try:
            expr = query.replace("^", "**")
            numbers = re.findall(r'[\d\.]+\s*[\+\-\*\/\*\*]\s*[\d\.]+', expr)
            if numbers:
                result = eval(numbers[0])
                return f"The answer is {result}"
        except:
            pass
    
    percent_match = re.search(r'(\d+(?:\.\d+)?)\s*%\s*(?:of\s+)?(\d+(?:\.\d+)?)', query_lower)
    if percent_match:
        percent = float(percent_match.group(1))
        number = float(percent_match.group(2))
        result = (percent / 100) * number
        return f"{percent}% of {number} is {result}"
    
    return None


def simplify_for_child(text: str, topic: str) -> str:
    """
    Simplify technical Wikipedia text for a 12-year-old.
    Uses simple word substitutions and sentence shortening.
    """
    simple_replacements = {
        "analgesic and antipyretic agent": "medicine for pain and fever",
        "neurodegenerative": "brain-weakening",
        "olfactory receptor genes": "smell sensors",
        "acetaminophen": "paracetamol",
        "over-the-counter": "without prescription",
        "approximately": "about",
        "subsequently": "then",
        "furthermore": "also",
        "nevertheless": "but",
        "consequently": "so",
        "additionally": "also",
        "electromagnetic": "light and energy",
        "gravitational": "gravity",
        "photosynthesis": "how plants make food from sunlight",
        "cardiovascular": "heart and blood",
        "respiratory": "breathing",
        "gastrointestinal": "stomach and digestion",
        "neurological": "brain and nerves",
    }
    
    result = text
    for complex_word, simple_word in simple_replacements.items():
        result = result.replace(complex_word, simple_word)
        result = result.replace(complex_word.capitalize(), simple_word.capitalize())
    
    return result


def search_wikipedia(query: str) -> Optional[str]:
    """
    Search Wikipedia for factual/scientific information.
    Returns a concise, simplified summary for Planet 5 (Venus) queries.
    """
    try:
        search_query = query.replace("what is", "").replace("how does", "").replace("explain", "").strip()
        
        headers = {
            "User-Agent": "ThroneOfAnhu/1.0 (https://thecollegeofanhu.com; contact@thecollegeofanhu.com)"
        }
        
        search_url = "https://en.wikipedia.org/w/api.php"
        search_params = {
            "action": "query",
            "list": "search",
            "srsearch": search_query,
            "format": "json",
            "srlimit": 1
        }
        
        with httpx.Client(timeout=10.0, headers=headers) as client:
            search_resp = client.get(search_url, params=search_params)
            search_data = search_resp.json()
        
        if not search_data.get("query", {}).get("search"):
            return None
        
        page_title = search_data["query"]["search"][0]["title"]
        
        summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{page_title.replace(' ', '_')}"
        
        with httpx.Client(timeout=10.0, headers=headers) as client:
            summary_resp = client.get(summary_url)
            if summary_resp.status_code == 200:
                summary_data = summary_resp.json()
                extract = summary_data.get("extract", "")
                if extract:
                    extract = simplify_for_child(extract, page_title)
                    if len(extract) > 600:
                        extract = extract[:600] + "..."
                    print(f"[VENUS] Wikipedia found: {page_title}")
                    return f"[FACT: {page_title}] {extract}"
        
        return None
        
    except Exception as e:
        print(f"[VENUS] Wikipedia search error: {e}")
        return None


def fetch_from_planets(query: str) -> Dict:
    """
    Main entry point: Route query to correct planet(s) and fetch relevant scrolls.
    
    Returns:
        {
            "planets_consulted": [1, 2],
            "scrolls": [...],
            "math_result": "..." (if applicable),
            "science_search": True/False (if web search needed)
        }
    """
    result = {
        "planets_consulted": [],
        "scrolls": [],
        "math_result": None,
        "science_search": False
    }
    
    planets = ai_route_to_planets(query)
    result["planets_consulted"] = planets
    
    if 5 in planets:
        math_result = handle_math_query(query)
        if math_result:
            result["math_result"] = math_result
            return result
        
        query_lower = query.lower()
        science_keywords = ["what is", "how does", "how do", "function of", "works", "explain", "define", "calculate", "how many", "where is", "when was", "who invented", "who discovered"]
        if any(kw in query_lower for kw in science_keywords):
            wiki_result = search_wikipedia(query)
            if wiki_result:
                result["science_search"] = wiki_result
            else:
                result["science_search"] = True
    
    for planet_num in planets:
        planet_scrolls = search_planet(planet_num, query, limit=3)
        for ps in planet_scrolls:
            ps["planet"] = PLANETS[planet_num]["name"]
        result["scrolls"].extend(planet_scrolls)
    
    print(f"[ROUTER] Consulted planets {[PLANETS[p]['name'] for p in planets]}, found {len(result['scrolls'])} scrolls")
    
    return result


def get_planet_context(query: str) -> str:
    """
    Get context from the correct planets for the witness engine.
    Returns formatted scroll excerpts.
    """
    fetch_result = fetch_from_planets(query)
    
    context_parts = []
    
    if fetch_result["math_result"]:
        context_parts.append(f"[CALCULATION] {fetch_result['math_result']}")
    
    if fetch_result["science_search"]:
        if isinstance(fetch_result["science_search"], str):
            context_parts.append(fetch_result["science_search"])
        else:
            context_parts.append("[SCIENCE QUERY] This is a factual/scientific question. Answer directly with known facts.")
    
    for scroll in fetch_result["scrolls"][:5]:
        planet = scroll.get("planet", "UNKNOWN")
        text = scroll.get("text", "")[:400]
        context_parts.append(f"[{planet}] {text}")
    
    return "\n\n".join(context_parts)


if __name__ == "__main__":
    test_queries = [
        "What are the 7 nations?",
        "What is the square root of 864?",
        "What is the diameter of the moon?",
        "Quote John 1:1",
        "Who is Osiris Ani?",
        "What is the function of the liver?",
    ]
    
    for q in test_queries:
        print(f"\n{'='*60}")
        print(f"QUERY: {q}")
        result = fetch_from_planets(q)
        print(f"Planets: {[PLANETS[p]['name'] for p in result['planets_consulted']]}")
        if result["math_result"]:
            print(f"Math: {result['math_result']}")
        if result["science_search"]:
            print("Science search suggested")
        print(f"Scrolls found: {len(result['scrolls'])}")
