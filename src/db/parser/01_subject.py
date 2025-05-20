from bs4 import BeautifulSoup
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import os
import json
import argparse
from glob import glob
from pathlib import Path
import sys

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from src.db.models import Subject
from src.db.database import Database

@dataclass
class Subject:
    syllabus_code: str
    subject_name: str
    subject_name_en: str
    subject_type: str
    subject_type_en: str
    credits: int
    grade: str
    grade_en: str
    semester: str
    semester_en: str
    department: str
    department_en: str
    created_at: datetime
    updated_at: datetime

class SubjectParser:
    @staticmethod
    def parse(raw_data: Dict[str, Any]) -> Optional[Subject]:
        try:
            return Subject(
                syllabus_code=raw_data.get('syllabus_code', ''),
                subject_name=raw_data.get('subject_name', ''),
                subject_name_en=raw_data.get('subject_name_en', ''),
                subject_type=raw_data.get('subject_type', ''),
                subject_type_en=raw_data.get('subject_type_en', ''),
                credits=raw_data.get('credits', 0),
                grade=raw_data.get('grade', ''),
                grade_en=raw_data.get('grade_en', ''),
                semester=raw_data.get('semester', ''),
                semester_en=raw_data.get('semester_en', ''),
                department=raw_data.get('department', ''),
                department_en=raw_data.get('department_en', ''),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        except Exception as e:
            print(f"Error parsing subject data: {e}")
            return None

def parse_subject_table(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    # 明示的にテーブルを検索する（複数候補の中から属性と科目名を含むものを特定）
    tables = soup.find_all('table', class_='dataT')
    table = None
    for t in tables:
        headers = t.find_all('th')
        if any('属性' in th.get_text(strip=True) for th in headers) and any('科目名' in th.get_text(strip=True) for th in headers):
            table = t
            break

    if not table:
        print("  No matching table found.")
        return []

    data = []
    rows = table.find_all('tr')[1:]  # Skip header row
    for i, row in enumerate(rows):
        cols = row.find_all('td')
        if len(cols) < 4:
            print(f"    Row {i} skipped (not enough columns).")
            continue

        # 属性の処理
        attr_text = cols[2].get_text(strip=True)
        note = ''
        class_name = attr_text
        subclass_name = ''

        if '：' in attr_text:
            note, rest = attr_text.split('：', 1)
            class_name = rest

        if '・' in class_name:
            class_name, subclass_name = class_name.split('・', 1)

        # 科目名の処理
        name_part = cols[3].get_text(strip=True).split('\n')[0].strip()
        name_part = name_part.split('@')[0].strip()
        links = cols[3].find_all('a', href=True)
        syllabus_code = ''
        for link in links:
            href = link['href']
            if 'do?i=' in href:
                syllabus_code = href.split('do?i=')[1].split('&')[0]
                break

        if syllabus_code:
            current_time = datetime.now().isoformat()
            entry = {
                "syllabus_code": syllabus_code,
                "name": name_part,
                "class_name": class_name,
                "subclass_name": subclass_name,
                "class_note": note,
                "created_at": current_time,
                "updated_at": None
            }
            data.append(entry)

    return data

def save_json(entry: Dict[str, Any], year: str) -> None:
    syllabus_code = entry["syllabus_code"]
    out_dir = f"updates/subject/add"
    os.makedirs(out_dir, exist_ok=True)
    filepath = os.path.join(out_dir, f"{syllabus_code}.json")
    
    json_data = {
        "content": entry
    }
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    print(f"  Saved: {filepath}")

def parse_html_file(filepath: str) -> List[Dict[str, Any]]:
    with open(filepath, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    # 整形されたHTMLを初回のみ保存（多重保存を防ぐ）
    pretty_path = filepath.replace('.pretty.html', '') + '.pretty.html'
    if not os.path.exists(pretty_path):
        with open(pretty_path, 'w', encoding='utf-8') as f:
            f.write(soup.prettify())

    return parse_subject_table(soup)

def process_subject_data(year: str) -> None:
    """
    指定された年のシラバスデータを処理する
    
    Args:
        year (str): 処理対象の年
    """
    html_files = glob(f"src/syllabus/{year}/search_page/*.html")
    total_files = len(html_files)
    print(f"Found {total_files} HTML files.")

    processed_count = 0
    for file in html_files:
        processed_count += 1
        try:
            entries = parse_html_file(file)
            for entry in entries:
                save_json(entry, year)
        except Exception as e:
            print(f"Error processing {file}: {str(e)}")
            continue

    print(f"\nCompleted processing {processed_count} files.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse syllabus HTML and output JSON files.')
    parser.add_argument('-y', '--year', required=True, help='Target year')
    args = parser.parse_args()
    
    process_subject_data(args.year) 