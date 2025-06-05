import os
import json
import csv
import sqlite3
from typing import List, Set, Dict
from datetime import datetime
import chardet
from .utils import normalize_subject_name, get_year_from_user

def get_subject_names(year: int) -> Set[str]:
    """SQLiteデータベースから科目名を抽出する"""
    subject_names = set()
    db_path = os.path.join("src", "syllabus", str(year), "data", f"syllabus_{year}.db")
    
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"データベースファイルが見つかりません: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # course_titleカラムから科目名を取得
        cursor.execute("SELECT DISTINCT course_title FROM syllabus_basic WHERE course_title IS NOT NULL")
        rows = cursor.fetchall()
        
        for row in rows:
            if row[0]:  # NULLでない場合
                normalized_name = normalize_subject_name(row[0])
                if normalized_name:  # 空文字でない場合
                    subject_names.add(normalized_name)
        
    except sqlite3.Error as e:
        print(f"データベースエラー: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()
    
    return subject_names

def create_subject_name_json(subject_names: Set[str]) -> None:
    """科目名のJSONファイルを作成する"""
    output_dir = os.path.join("updates", "subject_name", "add")
    os.makedirs(output_dir, exist_ok=True)
    
    # 現在の日時を取得してファイル名を生成
    current_time = datetime.now()
    filename = f"subject_name_{current_time.strftime('%Y%m%d_%H%M')}.json"
    output_file = os.path.join(output_dir, filename)
    
    data = {
        "subject_names": [{
            "name": name,
            "created_at": current_time.isoformat()
        } for name in sorted(subject_names)]
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
        
        # 科目名の抽出
        subject_names = get_subject_names(year)
        print(f"抽出された科目名: {len(subject_names)}件")
        
        # JSONファイルの作成
        output_file = create_subject_name_json(subject_names)
        print(f"JSONファイルを作成しました: {output_file}")
        
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        raise

if __name__ == "__main__":
    main() 