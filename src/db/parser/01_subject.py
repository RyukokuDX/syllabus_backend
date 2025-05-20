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
    CSVファイルから科目情報を抽出する
    
    Args:
        filepath (str): 解析対象のCSVファイルパス
        
    Returns:
        List[Dict[str, Any]]: 抽出された科目情報のリスト
    """
    print(f"Processing CSV file: {filepath}")
    entries = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    # 属性の変換
                    attribute = row.get('属性', '')
                    class_name = attribute
                    subclass_name = None
                    class_note = None
                    
                    # 属性に括弧が含まれる場合、括弧内をclass_noteとして抽出
                    if '(' in attribute and ')' in attribute:
                        class_name = attribute.split('(')[0].strip()
                        class_note = attribute[attribute.find('(')+1:attribute.find(')')].strip()
                    
                    entry = {
                        'syllabus_code': row.get('シラバス管理番号', ''),
                        'name': row.get('科目名', ''),
                        'class_name': class_name,
                        'subclass_name': subclass_name,
                        'class_note': class_note
                    }
                    entries.append(entry)
                except Exception as e:
                    print(f"  Error parsing CSV row: {str(e)}")
                    continue
                    
        print(f"  Found {len(entries)} entries in {filepath}")
        return entries
        
    except Exception as e:
        print(f"  Error processing {filepath}: {str(e)}")
        return []

def save_json(entry: Dict[str, Any], year: str) -> None:
    """
    科目情報をJSONファイルとして保存する
    
    Args:
        entry (Dict[str, Any]): 保存する科目情報
        year (str): 年度
    """
    syllabus_code = entry['syllabus_code']
    if not syllabus_code:
        print(f"  Skipping entry with empty syllabus_code")
        return
        
    filepath = f"updates/subject/add/{syllabus_code}.json"
    
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        # サンプルファイルと同じ形式に整形
        json_data = {
            "subjects": [{
                **entry,
                "created_at": datetime.now().isoformat(),
                "updated_at": None
            }]
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"  Error saving {filepath}: {str(e)}")

def process_subject_data(year: str) -> None:
    """
    指定された年のシラバスデータを処理する
    
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
            for entry in entries:
                save_json(entry, year)
            print(f"\nProcessing Summary:")
            print(f"Total entries processed: {len(entries)}")
        else:
            print("No entries found in CSV file")
    except Exception as e:
        print(f"Error processing CSV file: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process syllabus data for a specific year")
    parser.add_argument("year", nargs="?", default="2025", help="Year to process (default: 2025)")
    args = parser.parse_args()
    
    process_subject_data(args.year) 