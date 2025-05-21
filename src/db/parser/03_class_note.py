from typing import Dict, Any, List
import os
import json
import argparse
from pathlib import Path
import sys
import csv
from datetime import datetime

def parse_csv_file(filepath: str) -> List[Dict[str, Any]]:
    """
    CSVファイルから科目区分の備考情報を抽出する
    
    Args:
        filepath (str): 解析対象のCSVファイルパス
        
    Returns:
        List[Dict[str, Any]]: 抽出された科目区分の備考情報のリスト
    """
    print(f"Processing CSV file: {filepath}")
    entries = []
    seen_notes = set()  # 重複チェック用のセット
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    # 属性の変換
                    attribute = row.get('属性', '')
                    class_note = None
                    
                    # 「：」があれば、左側をclass_noteに
                    if '：' in attribute:
                        parts = attribute.split('：')
                        class_note = parts[0].strip()
                    
                    # 重複チェック
                    if class_note and class_note not in seen_notes:
                        seen_notes.add(class_note)
                        entry = {
                            'class_note': class_note
                        }
                        entries.append(entry)
                except Exception as e:
                    print(f"  Error parsing CSV row: {str(e)}")
                    continue
                    
        print(f"  Found {len(entries)} unique entries in {filepath}")
        return entries
        
    except Exception as e:
        print(f"  Error processing {filepath}: {str(e)}")
        return []

def save_json(entries: List[Dict[str, Any]], year: str) -> None:
    """
    科目区分の備考情報をJSONファイルとして保存する
    
    Args:
        entries (List[Dict[str, Any]]): 保存する科目区分の備考情報のリスト
        year (str): 年度
    """
    if not entries:
        print("  No entries to save")
        return
        
    filepath = f"update/class_note/add/class_note_{year}.json"
    
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        json_data = {
            "class_notes": [{
                **entry,
                "created_at": datetime.now().isoformat(),
                "updated_at": None
            } for entry in entries]
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        print(f"  Saved {len(entries)} entries to {filepath}")
    except Exception as e:
        print(f"  Error saving {filepath}: {str(e)}")

def process_class_note_data(year: str) -> None:
    """
    指定された年の科目区分の備考データを処理する
    
    Args:
        year (str): 処理対象の年
    """
    # CSVファイルの処理
    csv_file = f"src/syllabus/{year}/search_page/syllabus_list.csv"
    if not os.path.exists(csv_file):
        print(f"CSV file not found: {csv_file}")
        return

    try:
        entries = parse_csv_file(csv_file)
        if entries:
            save_json(entries, year)
            print(f"\nProcessing Summary:")
            print(f"Total entries processed: {len(entries)}")
        else:
            print("No entries found in CSV file")
    except Exception as e:
        print(f"Error processing CSV file: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process class note data for a specific year")
    parser.add_argument("-y", "--year", help="Year to process")
    args = parser.parse_args()
    
    year = args.year
    if not year:
        year = input("年度を入力してください（空の場合は今年）: ").strip()
        if not year:
            year = datetime.now().year
    
    process_class_note_data(str(year)) 