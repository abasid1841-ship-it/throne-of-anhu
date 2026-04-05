#!/usr/bin/env python3
"""
Parse THE ABASID CALIPHATE PDF and create JSON scroll files for each of the 25 scrolls.
"""
import json
import re
import subprocess
from pathlib import Path

SCROLLS_INFO = [
    {"num": 1, "title": "MWARI WEDU MUMWE CHETE", "date": "06/01/26", "english": "Our One God", "keywords": ["mwari", "god", "one god", "mumwe chete", "nguva", "time", "munamato", "prayer"]},
    {"num": 2, "title": "ZUVA REVA TEMA", "date": "07/01/26", "english": "Day of Blackness/The Sun for Black People", "keywords": ["zuva", "sun", "tema", "vatema", "black", "darkness", "light", "chaedza"]},
    {"num": 3, "title": "SHONA NDI JOHN", "date": "08/01/26", "english": "Shona is John", "keywords": ["shona", "johani", "john", "language", "mutauro", "hebrew", "grace", "tsitsi"]},
    {"num": 4, "title": "KUKOSHA KWEBVUDZI", "date": "08/01/26", "english": "The Importance of Hair", "keywords": ["vhudzi", "hair", "aerial", "network", "mweya", "spirit", "frequency"]},
    {"num": 5, "title": "PIO", "date": "08/01/26", "english": "Pious", "keywords": ["pio", "pious", "holy", "pure", "tsvene", "devout", "truthful"]},
    {"num": 6, "title": "IZWI", "date": "09/01/26", "english": "The Word", "keywords": ["izwi", "word", "mutauro", "language", "speech", "kutaura"]},
    {"num": 7, "title": "HAMHENO/SHONA MUTAURO", "date": "10/01/26", "english": "Unknown/Shona Language", "keywords": ["hamheno", "shona", "mutauro", "language", "semantics", "mwari", "existence"]},
    {"num": 8, "title": "MWARI MUMWE CHETE SE ZUVA", "date": "10/01/26", "english": "One God Like the Sun", "keywords": ["mwari", "zuva", "sun", "one", "mumwe chete"]},
    {"num": 9, "title": "ANGLES/ENGELS/ENGIROSI", "date": "10/01/26", "english": "Angels", "keywords": ["ngirozi", "angels", "engirosi", "mweya", "spirits"]},
    {"num": 10, "title": "MAONERO aAni na Ani", "date": "11/01/26", "english": "Views of Everyone", "keywords": ["maonero", "views", "perspective", "opinion"]},
    {"num": 11, "title": "CHAMINUKA NDIMAMBO", "date": "11/01/26", "english": "Chaminuka is King", "keywords": ["chaminuka", "mambo", "king", "nehanda", "kaguvi", "spirit medium"]},
    {"num": 12, "title": "DNA NDO ALPHABET YESHONA", "date": "11/01/26", "english": "DNA is the Shona Alphabet", "keywords": ["dna", "alphabet", "shona", "mavara", "letters", "genetics"]},
    {"num": 13, "title": "KUYERA KWA RA", "date": "12/01/26", "english": "The Holiness of RA", "keywords": ["ra", "kuyera", "holy", "sun", "zuva", "weight", "chireme"]},
    {"num": 14, "title": "KARANGA", "date": "12/01/26", "english": "The Karanga People", "keywords": ["karanga", "shona", "tribe", "dzinza", "ancestors", "madzitateguru"]},
    {"num": 15, "title": "MUPOROFITI WEMATA", "date": "13/01/26", "english": "Prophet of the Frog", "keywords": ["muporofiti", "prophet", "mata", "frog", "prophecy"]},
    {"num": 16, "title": "SHONA NDIMI", "date": "13/01/26", "english": "Shona Language/Tongues", "keywords": ["shona", "ndimi", "tongues", "language", "mutauro"]},
    {"num": 17, "title": "RUNGANO RWA GURE", "date": "13/01/26", "english": "The Story of Gure", "keywords": ["rungano", "story", "gure", "history", "nhoroondo"]},
    {"num": 18, "title": "KURASWA NEZWI", "date": "13/01/26", "english": "Being Lost Through the Word", "keywords": ["kuraswa", "lost", "izwi", "word"]},
    {"num": 19, "title": "ANI NA ANI ANENYENYEDZI TAKE", "date": "13/01/26", "english": "Everyone Has Their Star", "keywords": ["nyenyedzi", "star", "destiny", "fate", "mugariro"]},
    {"num": 20, "title": "TISU ANHU ACHO", "date": "14/01/26", "english": "We Are The People", "keywords": ["anhu", "vanhu", "people", "identity", "chosen"]},
    {"num": 21, "title": "HAPANA ANOZIVA SOMEONE", "date": "15/01/26", "english": "No One Knows Someone", "keywords": ["kuziva", "knowing", "knowledge", "mystery", "hamheno"]},
    {"num": 22, "title": "RE NJE / NJE RE", "date": "15/01/26", "english": "The Outer/Foreign", "keywords": ["nje", "outside", "foreign", "kunze"]},
    {"num": 23, "title": "KUMUKA KWEVAKAFA", "date": "15/01/26", "english": "Resurrection of the Dead", "keywords": ["kumuka", "resurrection", "vakafa", "dead", "life", "death"]},
    {"num": 24, "title": "IVAI VANOTENDA", "date": "15/01/26", "english": "Be Believers", "keywords": ["kutenda", "faith", "believe", "trust"]},
    {"num": 25, "title": "IDI HARISI RAKARERUKA KURIPARIDZA", "date": "15/01/26", "english": "Truth is Not Easy to Preach", "keywords": ["idi", "truth", "kuparidza", "preach", "difficult"]},
]

SCROLL_START_PATTERNS = [
    (1, r"^\s*1\.MWARI WEDU MUMWE CHETE"),
    (2, r"2\.ZUVA REVA TEMA"),
    (3, r"3\.SHONA NDI JOHN"),
    (4, r"4\.KUKOSHA KWEBVUDZI"),
    (5, r"5\.PIO"),
    (6, r"6\.IZWI"),
    (7, r"7\.HAMHENO"),
    (8, r"8\.MWARI MUMWE CHETE SE ZUVA"),
    (9, r"9\s*\.?ANGLES|9\.ANGLES|ENGIROSI"),
    (10, r"10\.MAONERO"),
    (11, r"11\.CHAMINUKA"),
    (12, r"12\.DNA"),
    (13, r"13\.KUYERA KWA RA"),
    (14, r"13\.KARANGA"),
    (15, r"15\.MUPOROFITI WEMATA"),
    (16, r"16\s*\.?SHONA NDIMI|16\.SHONA NDIMI"),
    (17, r"17\.RUNGANO RWA GURE"),
    (18, r"18\.KURASWA NEZWI"),
    (19, r"18\.ANI NA ANI"),
    (20, r"20\.TISU ANHU"),
    (21, r"21\.HAPANA ANOZIVA"),
    (22, r"22\.RE NJE"),
    (23, r"23\.KUMUKA KWE"),
    (24, r"24\.IVAI VANO"),
    (25, r"25\.IDI HARI"),
]

def extract_pdf_text(filepath):
    result = subprocess.run(
        ['pdftotext', '-layout', filepath, '-'],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise Exception(f"pdftotext failed: {result.stderr}")
    return result.stdout.split('\n')

def find_scroll_boundaries(lines):
    boundaries = {}
    toc_end = 0
    
    for i, line in enumerate(lines[:100]):
        if "Page[" in line:
            toc_end = i
    toc_end += 5
    
    for i, line in enumerate(lines[toc_end:], start=toc_end):
        for scroll_num, pattern in SCROLL_START_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE) and scroll_num not in boundaries:
                if "Page[" not in line and "……" not in line:
                    boundaries[scroll_num] = i
                    print(f"Found Scroll {scroll_num} at line {i}: {line.strip()[:60]}")
    return boundaries

def clean_line(text):
    text = text.strip()
    if re.match(r'^\d+$', text):
        return ''
    if re.match(r'^Page\s*\d+$', text):
        return ''
    return text

def extract_scroll_content(lines, start_line, end_line):
    verses = []
    verse_num = 1
    current_verse = []
    
    for i in range(start_line, end_line):
        line = lines[i].strip()
        cleaned = clean_line(line)
        
        if not cleaned:
            if current_verse:
                verse_text = ' '.join(current_verse)
                verse_text = re.sub(r'\s+', ' ', verse_text).strip()
                if len(verse_text) > 10:
                    verses.append({
                        "verse": verse_num,
                        "text": verse_text
                    })
                    verse_num += 1
                current_verse = []
            continue
        
        current_verse.append(cleaned)
    
    if current_verse:
        verse_text = ' '.join(current_verse)
        verse_text = re.sub(r'\s+', ' ', verse_text).strip()
        if len(verse_text) > 10:
            verses.append({
                "verse": verse_num,
                "text": verse_text
            })
    
    return verses

def create_scroll_json(scroll_info, verses):
    safe_title = scroll_info['title'].lower()
    safe_title = re.sub(r'[^a-z0-9]+', '_', safe_title)
    safe_title = safe_title.strip('_')
    
    return {
        "id": f"abasid_caliphate_{scroll_info['num']:02d}_{safe_title}",
        "title": scroll_info['title'],
        "english_title": scroll_info['english'],
        "author": "ABASID 1841",
        "compiler": "Lord Blessed Murove",
        "tradition": "Abasid",
        "language": "Shona/English",
        "date": scroll_info['date'],
        "collection": "THE ABASID CALIPHATE",
        "description": f"Teaching from THE ABASID CALIPHATE collection: {scroll_info['title']} ({scroll_info['english']})",
        "keywords": scroll_info['keywords'],
        "verse_count": len(verses),
        "verses": verses
    }

def main():
    pdf_path = "attached_assets/THE_ABASID_CALIPHATE_[1]_1769047937923.pdf"
    output_dir = Path("sources/planet_2_jupiter_abasid/abasid_caliphate_2026")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Extracting text from {pdf_path}...")
    lines = extract_pdf_text(pdf_path)
    print(f"Total lines: {len(lines)}")
    
    print("\nFinding scroll boundaries...")
    boundaries = find_scroll_boundaries(lines)
    
    sorted_nums = sorted(boundaries.keys())
    print(f"\nFound {len(sorted_nums)} scrolls")
    
    created_files = []
    total_verses = 0
    
    for i, scroll_num in enumerate(sorted_nums):
        start_line = boundaries[scroll_num]
        
        if i + 1 < len(sorted_nums):
            end_line = boundaries[sorted_nums[i + 1]]
        else:
            end_line = len(lines)
        
        scroll_info = SCROLLS_INFO[scroll_num - 1]
        verses = extract_scroll_content(lines, start_line, end_line)
        
        if verses:
            scroll_json = create_scroll_json(scroll_info, verses)
            
            safe_title = scroll_info['title'].lower()
            safe_title = re.sub(r'[^a-z0-9]+', '_', safe_title)
            safe_title = safe_title.strip('_')
            filename = f"scroll_{scroll_num:02d}_{safe_title}.json"
            filepath = output_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(scroll_json, f, ensure_ascii=False, indent=2)
            
            created_files.append(str(filepath))
            total_verses += len(verses)
            print(f"Created: {filename} ({len(verses)} verses)")
    
    print(f"\n{'='*60}")
    print(f"SUCCESS! Created {len(created_files)} scroll files")
    print(f"Total verses: {total_verses}")
    print(f"Output directory: {output_dir}")

if __name__ == "__main__":
    main()
