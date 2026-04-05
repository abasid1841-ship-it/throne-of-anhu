#!/usr/bin/env python3
"""
Parse the Nhoroondo dzaBaba Johanne chronicle into a structured JSON scroll.
This sacred text documents the life, teachings, miracles, and prophecies of Baba Johanne.
"""

import re
import json
from typing import Dict, List, Optional, Tuple

def extract_dates(text: str) -> List[str]:
    """Extract dates from text."""
    dates = []
    patterns = [
        r'\d{2}-\d{2}-\d{4}',
        r'\d{1,2}-\d{2}-\d{4}',
        r'MUSI WA \d{1,2}-\d{2}-\d{4}',
        r'\d{1,2}/\d{2}/\d{4}',
        r'19[0-9]{2}',
        r'1914',
        r'1932',
        r'1933',
        r'1973',
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        dates.extend(matches)
    return list(set(dates))

def extract_locations(text: str) -> List[str]:
    """Extract location names from text."""
    locations = [
        'GANDANZARA', 'GANDAANZARA', 'NORTON', 'MARIMBA', 'GOMO REMARIMBA',
        'CHIPUKUTU', 'HUNYANI', 'RUSAPE', 'MUTARE', 'HARARE', 'SALISBURY',
        'MARONDERA', 'BUHERA', 'ZAKA', 'MASVINGO', 'BULAWAYO', 'GWERU',
        'PORT ELIZABETH', 'P.E.', 'JOHANNESBURG', 'JOBURG', 'SOUTH AFRICA',
        'BOTSWANA', 'MOROKA', 'LUSAKA', 'NDOLA', 'ZAMBIA', 'NAIROBI', 'KENYA',
        'ARUSHA', 'DAR ES SALAAM', 'DALASALAM', 'TANZANIA', 'MOZAMBIQUE',
        'MOZAMBIKWI', 'NYAMWEDA', 'CHIVERO', 'WEDZA', 'MATSINE', 'DEWEDZO',
        'CHINYAMATAMBA', 'KUTAMA', 'SAWE', 'MATABELELAND', 'MASHONALAD',
        'MUGWAMBI', 'SHENA', 'CHIRUMANZU', 'KWEKWE', 'KADOMA', 'CHEGUTU',
        'HARTLEY', 'EGYPT', 'EGPTY', 'ISRAEL', 'AFRICA', 'AFRIKA', 'HAM',
        'ARABIA', 'LEIGHWOODS', 'MALANDELAS', 'MASVOSVA', 'NYAHAWA', 'NYAHUBVU'
    ]
    found = []
    text_upper = text.upper()
    for loc in locations:
        if loc in text_upper:
            found.append(loc.title())
    return list(set(found))

def categorize_content(text: str) -> List[str]:
    """Categorize verse content by type."""
    categories = []
    text_upper = text.upper()
    
    if any(w in text_upper for w in ['KUPOROFITA', 'PROPHECY', 'CHIPOROFITA', 'ZVICHAITIKA', 'WANOZO', 'KUCHA', 'WANOCHA', 'WAKA POROFITA']):
        categories.append('prophecy')
    if any(w in text_upper for w in ['MUTEMO', 'MIRAO', 'MIRAYIRO', 'LAW', 'COMMANDMENT', 'MITEMO']):
        categories.append('law')
    if any(w in text_upper for w in ['KUDZIDZISA', 'TEACHING', 'DZIDZISA', 'WAKA TAWURA', 'WAKA TI', 'AKATI']):
        categories.append('teaching')
    if any(w in text_upper for w in ['CHISHAMISO', 'MIRACLE', 'MASHURA', 'ZVISHAMISO']):
        categories.append('miracle')
    if any(w in text_upper for w in ['KURAPA', 'HEAL', 'PORISA', 'CHIRWERE', 'KURWARA']):
        categories.append('healing')
    if any(w in text_upper for w in ['KUPIKA', 'JERI', 'PRISON', 'ARREST', 'POLICE', 'MAPURISA', 'KUTAMBUDZWA', 'PERSECUTION']):
        categories.append('persecution')
    if any(w in text_upper for w in ['HOPE', 'DREAM', 'VISION', 'ROTA', 'ZARURA']):
        categories.append('vision')
    if any(w in text_upper for w in ['RWUBHABHATIDZO', 'RUBHABHATIDZO', 'BAPTISM', 'JORODANI', 'JORDAN']):
        categories.append('baptism')
    if any(w in text_upper for w in ['KUFA', 'DEATH', 'CHITUNHA', 'KUBEREKWA', 'BIRTH', 'SUNUNGUKA']):
        categories.append('life_event')
    if any(w in text_upper for w in ['MWEYA', 'SPIRIT', 'DENGA', 'HEAVEN', 'NGIROZI', 'ANGEL']):
        categories.append('spiritual')
    if any(w in text_upper for w in ['RWENDO', 'JOURNEY', 'KUYENDA', 'KUSVIKA', 'TRAVEL']):
        categories.append('journey')
    if any(w in text_upper for w in ['CHIRANGANO', 'CHURCH', 'KEREKE', 'WANHU', 'FOLLOWERS']):
        categories.append('church')
    if any(w in text_upper for w in ['MASHOKO', 'WORDS', 'TAWURA', 'SPEAK', 'SAY']):
        categories.append('speech')
    if any(w in text_upper for w in ['HUMBOWO', 'WITNESS', 'TESTIMONY']):
        categories.append('testimony')
    
    return categories if categories else ['narrative']

def parse_chapters(text: str) -> List[Dict]:
    """Parse the chronicle into chapters and verses."""
    chapters = []
    
    chapter_pattern = r'CHITSAWUKO\s+(\d+)[.,:]?\s*([^\n\[\]]*?)(?=\n|\[|$)'
    chapter_matches = list(re.finditer(chapter_pattern, text, re.IGNORECASE))
    
    for i, match in enumerate(chapter_matches):
        chapter_num = match.group(1)
        chapter_title = match.group(2).strip() if match.group(2) else ""
        
        start_pos = match.end()
        end_pos = chapter_matches[i + 1].start() if i + 1 < len(chapter_matches) else len(text)
        
        chapter_text = text[start_pos:end_pos]
        
        verse_pattern = r'\[(\d+)\]\s*([^\[\]]+?)(?=\[\d+\]|\Z)'
        verse_matches = re.findall(verse_pattern, chapter_text, re.DOTALL)
        
        verses = []
        for verse_num, verse_text in verse_matches:
            clean_text = ' '.join(verse_text.strip().split())
            if clean_text and len(clean_text) > 10:
                verses.append({
                    "verse_num": int(verse_num),
                    "text": clean_text,
                    "dates": extract_dates(clean_text),
                    "locations": extract_locations(clean_text),
                    "categories": categorize_content(clean_text)
                })
        
        if verses:
            chapters.append({
                "chapter_num": int(chapter_num),
                "title": chapter_title,
                "title_shona": chapter_title,
                "verses": verses,
                "date_references": list(set([d for v in verses for d in v.get('dates', [])])),
                "location_references": list(set([l for v in verses for l in v.get('locations', [])])),
                "categories": list(set([c for v in verses for c in v.get('categories', [])]))
            })
    
    return chapters

def create_scroll_json(chapters: List[Dict]) -> Dict:
    """Create the final scroll JSON structure."""
    
    all_verses = []
    verse_index = 0
    
    for chapter in chapters:
        chapter_num = chapter['chapter_num']
        chapter_title = chapter.get('title', '')
        
        if chapter_title:
            all_verses.append({
                "verse_id": verse_index,
                "chapter": chapter_num,
                "text": f"CHITSAWUKO {chapter_num}: {chapter_title}",
                "type": "chapter_header",
                "language": "shona",
                "dates": chapter.get('date_references', []),
                "locations": chapter.get('location_references', []),
                "categories": chapter.get('categories', [])
            })
            verse_index += 1
        
        for verse in chapter.get('verses', []):
            all_verses.append({
                "verse_id": verse_index,
                "chapter": chapter_num,
                "verse_num": verse['verse_num'],
                "text": verse['text'],
                "type": "verse",
                "language": "shona",
                "dates": verse.get('dates', []),
                "locations": verse.get('locations', []),
                "categories": verse.get('categories', [])
            })
            verse_index += 1
    
    scroll = {
        "scrolls": [{
            "scroll_id": "nhoroondo_dzababa_johanne",
            "series": "Sacred Chronicles",
            "book_title": "Nhoroondo dzaBaba Johanne - The Chronicles of Father John Masowe",
            "book_title_shona": "Nhoroondo dzaBaba Johanne",
            "language": "SHONA",
            "priority": "PRIMARY",
            "description": "A comprehensive sacred chronicle documenting the life, teachings, miracles, prophecies, laws, and testimonies of Baba Johanne Masowe, the African Messiah. Written by George Ben Medekiah.",
            "key_dates": {
                "birth": "01-10-1914",
                "holy_spirit_descent": "01-10-1932",
                "death": "13-09-1973",
                "ministry_start": "1932",
                "port_elizabeth_arrival": "06-08-1951"
            },
            "key_locations": [
                "Gandanzara (birthplace)",
                "Norton/Marimba (holy spirit descent)",
                "Port Elizabeth (major ministry)",
                "Ndola/Zambia (death)",
                "Kenya, Tanzania, Botswana (ministry travels)"
            ],
            "tags": [
                "baba johanne", "baba johani", "johane masowe", "masowe",
                "african messiah", "messiah", "1914", "1932", "1973",
                "gandanzara", "norton", "marimba", "port elizabeth",
                "prophecy", "miracles", "teachings", "laws", "mitemo",
                "shona", "zimbabwe", "sacred history", "chronicle"
            ],
            "total_chapters": len(chapters),
            "total_verses": len(all_verses),
            "verses": all_verses
        }]
    }
    
    return scroll

def main():
    with open('/tmp/nhoroondo_full.txt', 'r', encoding='utf-8') as f:
        text = f.read()
    
    print("Parsing chapters...")
    chapters = parse_chapters(text)
    print(f"Found {len(chapters)} chapters")
    
    total_verses = sum(len(ch.get('verses', [])) for ch in chapters)
    print(f"Found {total_verses} verses")
    
    print("Creating scroll JSON...")
    scroll = create_scroll_json(chapters)
    
    output_path = 'static/allscrolls.json/nhoroondo_dzababa_johanne.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(scroll, f, ensure_ascii=False, indent=2)
    
    print(f"Saved to {output_path}")
    
    for i, chapter in enumerate(chapters[:5]):
        print(f"\nChapter {chapter['chapter_num']}: {chapter.get('title', 'No title')[:50]}")
        print(f"  Verses: {len(chapter.get('verses', []))}")
        print(f"  Dates: {chapter.get('date_references', [])[:3]}")
        print(f"  Locations: {chapter.get('location_references', [])[:3]}")
        print(f"  Categories: {chapter.get('categories', [])[:3]}")

if __name__ == '__main__':
    main()
