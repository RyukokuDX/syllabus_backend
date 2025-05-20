from bs4 import BeautifulSoup
from typing import Dict, Any, List
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

def parse_subject_table(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """
    検索結果ページのテーブルから科目情報を抽出する
    
    Args:
        soup (BeautifulSoup): 解析対象のHTML
        
    Returns:
        List[Dict[str, Any]]: 抽出された科目情報のリスト
    """
    # 検索結果テーブルを探す
    table = soup.find("table", class_="dataT")
    if not table:
        print("  Error: table.dataT not found.")
        return []

    # データ行を取得（ヘッダー行をスキップ）
    rows = table.find_all("tr")[1:]
    print(f"  Found {len(rows)} rows in dataT table")

    # シラバス管理番号リストを取得
    syllabus_codes = []
    input_tag = soup.find("input", {"name": "param_syllabusKanriNo"})
    if input_tag and input_tag.get("value"):
        syllabus_codes = input_tag["value"].split(",")
    else:
        print("  Error: param_syllabusKanriNo not found")
        return []

    data = []
    for i, row in enumerate(rows):
        try:
            cols = row.find_all("td")
            if len(cols) < 7 or i >= len(syllabus_codes):
                print(f"    Row {i+1} skipped: insufficient columns or no syllabus code")
                continue

            syllabus_code = syllabus_codes[i].strip()
            year = cols[1].get_text(strip=True)
            attribute = cols[2].get_text(strip=True)
            subject_name = cols[3].get_text(strip=True)
            timeslot = cols[4].get_text(strip=True)
            assigned_year = cols[5].get_text(strip=True)
            instructor = cols[6].get_text(strip=True)

            current_time = datetime.now().isoformat()
            entry = {
                "syllabus_code": syllabus_code,
                "name": subject_name,
                "class_name": attribute,
                "subclass_name": "",
                "class_note": "",
                "year": year,
                "timeslot": timeslot,
                "assigned_year": assigned_year,
                "instructor": instructor,
                "created_at": current_time,
                "updated_at": None
            }
            data.append(entry)
            print(f"    Row {i+1}: {subject_name} ({syllabus_code})")

        except Exception as e:
            print(f"    Error processing row {i+1}: {str(e)}")
            continue

    return data

def save_json(entry: Dict[str, Any], year: str) -> None:
    """
    科目情報をJSONファイルとして保存する
    
    Args:
        entry (Dict[str, Any]): 保存する科目情報
        year (str): 対象年度
    """
    syllabus_code = entry["syllabus_code"]
    out_dir = f"updates/subject/add"
    os.makedirs(out_dir, exist_ok=True)
    filepath = os.path.join(out_dir, f"{syllabus_code}.json")
    
    json_data = {
        "content": entry
    }
    
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        print(f"  Saved: {filepath}")
    except Exception as e:
        print(f"  Error saving {filepath}: {str(e)}")

def parse_html_file(filepath: str) -> List[Dict[str, Any]]:
    """
    HTMLファイルを解析して科目情報を抽出する
    
    Args:
        filepath (str): 解析対象のHTMLファイルパス
        
    Returns:
        List[Dict[str, Any]]: 抽出された科目情報のリスト
    """
    print(f"Processing file: {filepath}")
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")

        # 整形されたHTMLを初回のみ保存
        pretty_path = filepath.replace(".pretty.html", "") + ".pretty.html"
        if not os.path.exists(pretty_path):
            with open(pretty_path, "w", encoding="utf-8") as f:
                f.write(soup.prettify())

        entries = parse_subject_table(soup)
        print(f"  Found {len(entries)} entries in {filepath}")
        return entries
        
    except Exception as e:
        print(f"  Error processing {filepath}: {str(e)}")
        return []

def process_subject_data(year: str) -> None:
    """
    指定された年のシラバスデータを処理する
    
    Args:
        year (str): 処理対象の年
    """
    html_files = glob(f"src/syllabus/{year}/raw_page/*.html")
    total_files = len(html_files)
    print(f"Found {total_files} HTML files.")

    processed_count = 0
    total_entries = 0
    error_count = 0

    for file in html_files:
        processed_count += 1
        try:
            entries = parse_html_file(file)
            if entries:
                total_entries += len(entries)
                for entry in entries:
                    save_json(entry, year)
            else:
                error_count += 1
        except Exception as e:
            print(f"Error processing {file}: {str(e)}")
            error_count += 1
            continue

    print(f"\nProcessing Summary:")
    print(f"Total files processed: {processed_count}")
    print(f"Total entries found: {total_entries}")
    print(f"Files with errors: {error_count}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse syllabus HTML and output JSON files.")
    parser.add_argument("-y", "--year", default="2025", help="Target year (default: 2025)")
    args = parser.parse_args()
    
    process_subject_data(args.year) 