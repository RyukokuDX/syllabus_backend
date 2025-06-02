import os
import json
import sqlite3
from typing import List, Dict, Set
from datetime import datetime
from tqdm import tqdm

def get_current_year() -> int:
    """現在の年度を取得する"""
    return datetime.now().year

def get_year_from_user() -> int:
    """ユーザーから年度を入力してもらう"""
    while True:
        try:
            year = input("年度を入力してください（空の場合は現在の年度）: ").strip()
            if not year:
                return get_current_year()
            year = int(year)
            if 2000 <= year <= 2100:  # 妥当な年度の範囲をチェック
                return year
            print("2000年から2100年の間で入力してください。")
        except ValueError:
            print("有効な数値を入力してください。")

def get_instructor_names(year: int) -> Set[dict]:
    """SQLiteデータベースから教員情報を取得する"""
    db_path = os.path.join("src", "syllabus", str(year), "data", f"syllabus_{year}.db")
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"データベースファイルが見つかりません: {db_path}")

    instructors = set()
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            # instructorsテーブルから教員情報を取得
            cursor.execute("""
                SELECT DISTINCT kanji_name, kana_name
                FROM instructors
                WHERE kanji_name IS NOT NULL
            """)
            
            for row in cursor.fetchall():
                kanji_name, kana_name = row
                if kanji_name:  # 漢字名が存在する場合のみ追加
                    instructor_info = {
                        'name': kanji_name,
                        'name_kana': kana_name
                    }
                    # タプルに変換してセットに追加（重複を防ぐため）
                    instructor_tuple = tuple(sorted(instructor_info.items()))
                    instructors.add(instructor_tuple)
    
    except sqlite3.Error as e:
        raise Exception(f"データベースエラー: {str(e)}")

    return instructors

def create_instructor_json(instructors: Set[tuple]) -> str:
    """教員情報のJSONファイルを作成する"""
    output_dir = os.path.join("updates", "instructor", "add")
    os.makedirs(output_dir, exist_ok=True)
    
    # 現在の日時を取得してファイル名を生成
    current_time = datetime.now()
    filename = f"instructor_{current_time.strftime('%Y%m%d_%H%M')}.json"
    output_file = os.path.join(output_dir, filename)
    
    # タプルを辞書に戻す
    instructor_dicts = [dict(t) for t in instructors]
    
    data = {
        "instructors": [{
            "name": instructor["name"],
            "name_kana": instructor["name_kana"],
            "created_at": current_time.isoformat()
        } for instructor in sorted(instructor_dicts, key=lambda x: x["name_kana"] or x["name"])]
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
        
        # 教員情報の取得
        instructors = get_instructor_names(year)
        print(f"抽出された教員情報: {len(instructors)}件")
        
        # JSONファイルの作成
        output_file = create_instructor_json(instructors)
        print(f"JSONファイルを作成しました: {output_file}")
        
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        raise

if __name__ == "__main__":
    main() 