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
    CSVファイルから科目名情報を抽出する
    
    Args:
        filepath (str): 解析対象のCSVファイルパス
        
    Returns:
        List[Dict[str, Any]]: 抽出された科目名情報のリスト
    """
    print(f"Processing CSV file: {filepath}")
    entries = []
    seen_names = set()  # 重複チェック用のセット
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    # 科目名の取得
                    name = row.get('科目名', '')
                    
                    # 重複チェック
                    if name and name not in seen_names:
                        seen_names.add(name)
                        entry = {
                            'name': name
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
    科目名情報をJSONファイルとして保存する
    
    Args:
        entries (List[Dict[str, Any]]): 保存する科目名情報のリスト
        year (str): 年度
    """
    if not entries:
        print("  No entries to save")
        return
        
    filepath = f"updates/subject_name/add/subject_name_{year}.json"
    
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        json_data = {
            "subject_names": [{
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

def process_subject_name_data(year: str) -> None:
    """
    指定された年の科目名データを処理する
    
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
    parser = argparse.ArgumentParser(description="Process subject name data for a specific year")
    parser.add_argument("-y", "--year", help="Year to process")
    args = parser.parse_args()
    
    year = args.year
    if not year:
        year = input("年度を入力してください（空の場合は今年）: ").strip()
        if not year:
            year = datetime.now().year
    
    process_subject_name_data(str(year)) 