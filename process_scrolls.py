#!/usr/bin/env python3
"""
Process ABASID scrolls from PDF files into structured JSON format.
Uses pypdf for proper PDF text extraction.
"""
import re
import json
import os
from pypdf import PdfReader

SCROLL_CONFIGS = [
    {
        "input_file": "attached_assets/☀️THE_GOSPEL_OF_CYRUS_1841_1766789707349.pdf",
        "output_file": "sources/gospel_of_cyrus.json",
        "id": "gospel_of_cyrus",
        "title": "The Gospel of Cyrus (RA - The Sun Anointed)",
        "author": "ABASID 1841",
        "tradition": "Abasid",
        "language": "English"
    },
    {
        "input_file": "attached_assets/3x☀️2_GOD_IS_TIME_1766789707368.pdf",
        "output_file": "sources/god_is_time.json",
        "id": "god_is_time",
        "title": "God Is Time (NGU)",
        "author": "ABASID 1841",
        "tradition": "Abasid",
        "language": "English/Shona"
    },
    {
        "input_file": "attached_assets/☀️_The_Gospel_of_CHRISTOS_1480_(THE_ANOINTED_TOWER)_1766789707385.pdf",
        "output_file": "sources/gospel_of_christos.json",
        "id": "gospel_of_christos",
        "title": "The Gospel of Christos 1480 (The Anointed Tower)",
        "author": "ABASID 1841",
        "tradition": "Abasid",
        "language": "English"
    },
    {
        "input_file": "attached_assets/☀️#14_THE_BOOK_OF_THE_NEW_CALENDAR__1766789707401.pdf",
        "output_file": "sources/book_of_new_calendar.json",
        "id": "book_of_new_calendar",
        "title": "The Book of the New Calendar",
        "author": "ABASID 1841",
        "tradition": "Abasid",
        "language": "English"
    },
    {
        "input_file": "attached_assets/☀️_BOOK_OF_ASAR_1841_1766789707415.pdf",
        "output_file": "sources/book_of_asar.json",
        "id": "book_of_asar",
        "title": "The Book of ASAR 1841",
        "author": "ABASID 1841",
        "tradition": "Abasid",
        "language": "English"
    },
    {
        "input_file": "attached_assets/☀️THE_GOSPEL_OF_YESU_1841_1766789707429.pdf",
        "output_file": "sources/gospel_of_yesu.json",
        "id": "gospel_of_yesu",
        "title": "The Gospel of Yesu (The Lamb and The Lion)",
        "author": "ABASID 1841",
        "tradition": "Abasid",
        "language": "English"
    },
    {
        "input_file": "attached_assets/THE_TRUE_EXODUS_1841_1766789707441.pdf",
        "output_file": "sources/true_exodus.json",
        "id": "true_exodus",
        "title": "The True Exodus 1841",
        "author": "ABASID 1841",
        "tradition": "Abasid",
        "language": "English/Hebrew"
    },
    {
        "input_file": "attached_assets/☀️2_GOD_IS_NUMBER_1766789707454.pdf",
        "output_file": "sources/god_is_number.json",
        "id": "god_is_number",
        "title": "God Is Number",
        "author": "ABASID 1841",
        "tradition": "Abasid",
        "language": "English/Shona"
    },
    {
        "input_file": "attached_assets/☀️#40_THE_BOOK_OF_THE_RISEN_SEEDS_1766789707467.pdf",
        "output_file": "sources/book_of_risen_seeds.json",
        "id": "book_of_risen_seeds",
        "title": "The Book of the Risen Seeds",
        "author": "ABASID 1841",
        "tradition": "Abasid",
        "language": "English"
    },
    {
        "input_file": "attached_assets/6x☀️copy_POWER_OF_THE_TRINITY_1766789707480.pdf",
        "output_file": "sources/power_of_trinity.json",
        "id": "power_of_trinity",
        "title": "The Power of the Trinity (Two Crowns)",
        "author": "ABASID 1841",
        "tradition": "Abasid",
        "language": "English"
    }
]


def extract_text_from_pdf(pdf_path):
    """Extract all text from a PDF file."""
    try:
        reader = PdfReader(pdf_path)
        text_parts = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)
        return '\n'.join(text_parts)
    except Exception as e:
        print(f"  Error extracting PDF: {e}")
        return ""


def is_page_number(line):
    """Check if a line is just a page number."""
    stripped = line.strip()
    return bool(re.match(r'^\d{1,3}$', stripped))


def is_skip_line(line):
    """Check if line should be skipped."""
    stripped = line.strip()
    skip_patterns = [
        r'^Qq$',
        r'^Yes RA$',
        r'^Shall I now pour',
        r'^Let me know if',
        r'^POUR RA$',
        r'^Then let (the|me)',
        r'^\(\+\d+ lines\)$',
        r'^☀️❤️',
    ]
    for pattern in skip_patterns:
        if re.match(pattern, stripped, re.IGNORECASE):
            return True
    return False


def get_chapter_name(line):
    """Extract chapter name if this is a chapter heading."""
    stripped = line.strip()
    chapter_patterns = [
        r'^(CHAPTER\s+[\dIVXLC]+)',
        r'^(PROLOGUE)',
        r'^(INTRODUCTION)',
        r'^(OUTRO)',
        r'^(APPENDIX)',
        r'^(Section\s+[\dIVXLC]+)',
    ]
    for pattern in chapter_patterns:
        match = re.match(pattern, stripped, re.IGNORECASE)
        if match:
            return stripped
    return None


def parse_scroll(raw_text, scroll_id):
    """Parse raw text into structured verses."""
    lines = raw_text.split('\n')
    verses = []
    current_chapter = "Main"
    current_verse_num = None
    current_verse_lines = []
    
    for line in lines:
        stripped = line.strip()
        
        if not stripped:
            continue
        if is_page_number(stripped):
            continue
        if is_skip_line(stripped):
            continue
        
        chapter = get_chapter_name(stripped)
        if chapter:
            if current_verse_num is not None and current_verse_lines:
                text = ' '.join(current_verse_lines)
                text = re.sub(r'\s+', ' ', text).strip()
                if text and len(text) > 5:
                    verses.append({
                        "verse": current_verse_num,
                        "chapter": current_chapter,
                        "text": text
                    })
                current_verse_num = None
                current_verse_lines = []
            current_chapter = chapter
            continue
        
        verse_match = re.match(r'^(\d+)\.\s*(.*)$', stripped)
        if verse_match:
            if current_verse_num is not None and current_verse_lines:
                text = ' '.join(current_verse_lines)
                text = re.sub(r'\s+', ' ', text).strip()
                if text and len(text) > 5:
                    verses.append({
                        "verse": current_verse_num,
                        "chapter": current_chapter,
                        "text": text
                    })
            
            current_verse_num = int(verse_match.group(1))
            first_text = verse_match.group(2).strip()
            current_verse_lines = [first_text] if first_text else []
        else:
            if current_verse_num is not None:
                current_verse_lines.append(stripped)
    
    if current_verse_num is not None and current_verse_lines:
        text = ' '.join(current_verse_lines)
        text = re.sub(r'\s+', ' ', text).strip()
        if text and len(text) > 5:
            verses.append({
                "verse": current_verse_num,
                "chapter": current_chapter,
                "text": text
            })
    
    unique_verses = []
    seen = set()
    for v in verses:
        key = (v["verse"], v["chapter"][:30], v["text"][:50])
        if key not in seen:
            seen.add(key)
            unique_verses.append(v)
    
    return unique_verses


def process_scroll(config):
    """Process a single scroll file into JSON format."""
    input_path = config["input_file"]
    output_path = config["output_file"]
    
    print(f"Processing: {config['title']}")
    
    raw_text = extract_text_from_pdf(input_path)
    if not raw_text:
        print(f"  No text extracted from {input_path}")
        return None
    
    verses = parse_scroll(raw_text, config["id"])
    
    scroll_data = {
        "id": config["id"],
        "title": config["title"],
        "author": config["author"],
        "tradition": config["tradition"],
        "language": config["language"],
        "verse_count": len(verses),
        "verses": verses
    }
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(scroll_data, f, indent=2, ensure_ascii=False)
    
    print(f"  Created: {output_path} with {len(verses)} verses")
    return scroll_data


def main():
    """Process all scrolls."""
    print("=" * 60)
    print("ABASID SCROLL PROCESSOR - PDF Edition")
    print("=" * 60)
    
    results = []
    total_verses = 0
    
    for config in SCROLL_CONFIGS:
        result = process_scroll(config)
        if result:
            results.append({
                "id": result["id"],
                "title": result["title"],
                "file": config["output_file"],
                "verse_count": result["verse_count"]
            })
            total_verses += result["verse_count"]
    
    print("\n" + "=" * 60)
    print(f"SUMMARY: Processed {len(results)} scrolls with {total_verses} total verses")
    print("=" * 60)
    
    manifest = {
        "name": "ABASID 1841 Scroll Collection",
        "version": "1.0",
        "scroll_count": len(results),
        "total_verses": total_verses,
        "scrolls": results
    }
    
    with open("sources/abasid_scrolls_manifest.json", 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    print(f"\nManifest saved to: sources/abasid_scrolls_manifest.json")
    
    for r in results:
        print(f"  - {r['title']}: {r['verse_count']} verses")
    
    return results


if __name__ == "__main__":
    main()
