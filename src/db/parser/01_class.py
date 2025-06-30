# File Version: v2.0.0
# Project Version: v2.0.0
# Last Updated: 2025-06-30
import os
import json
import csv
import sqlite3
from typing import List, Set, Dict
from datetime import datetime
import chardet
from .utils import get_year_from_user

def get_csv_files(year: int) -> List[str]:
    """指定された年度のCSVファイルのパスを取得する"""
    base_dir = os.path.join("src", "course_guide", str(year), "csv")
    if not os.path.exists(base_dir):
        raise FileNotFoundError(f"ディレクトリが見つかりません: {base_dir}")
    
    csv_files = [f for f in os.listdir(base_dir) if f.endswith('.csv')]
    if not csv_files:
        raise FileNotFoundError(f"CSVファイルが見つかりません: {base_dir}")
    
    return [os.path.join(base_dir, f) for f in csv_files]

def detect_encoding(file_path: str) -> str:
    """ファイルのエンコーディングを検出する"""
    with open(file_path, 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        return result['encoding']

def extract_class_names(csv_files: List[str]) -> Set[str]:
    """CSVファイルから科目区分を抽出する"""
    class_names = set()
    
    for csv_file in csv_files:
        try:
            # エンコーディングを自動検出
            encoding = detect_encoding(csv_file)
            if not encoding:
                encoding = 'utf-8'  # デフォルトはUTF-8
            
            with open(csv_file, 'r', encoding=encoding, errors='replace') as f:
                reader = csv.DictReader(f, delimiter='\t')
                for row in reader:
                    if '科目区分' in row and row['科目区分']:
                        class_names.add(row['科目区分'].strip())
        except Exception as e:
            print(f"警告: {csv_file}の処理中にエラーが発生しました: {str(e)}")
            continue
    
    return class_names

def create_class_json(class_names: Set[str]) -> None:
    """科目区分のJSONファイルを作成する"""
    output_dir = os.path.join("updates", "class", "add")
    os.makedirs(output_dir, exist_ok=True)
    
    # 現在の日時を取得してファイル名を生成
    current_time = datetime.now()
    filename = f"class_{current_time.strftime('%Y%m%d_%H%M')}.json"
    output_file = os.path.join(output_dir, filename)
    
    data = {
        "classes": [{
            "class_name": name,
            "created_at": current_time.isoformat()
        } for name in sorted(class_names)]
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return output_file

def main():
    """メイン処理"""
    try:
        # 年度の取得
        year = get_year_from_user()
        print(f"処理対象年度: {year}")
        
        # CSVファイルの取得
        csv_files = get_csv_files(year)
        print(f"処理対象ファイル: {len(csv_files)}件")
        
        # 科目区分の抽出
        class_names = extract_class_names(csv_files)
        print(f"抽出された科目区分: {len(class_names)}件")
        
        # JSONファイルの作成
        output_file = create_class_json(class_names)
        print(f"JSONファイルを作成しました: {output_file}")
        
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        raise

if __name__ == "__main__":
    main() 