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

def get_syllabus_masters(year: int) -> List[Dict]:
    """SQLiteデータベースからシラバスマスター情報を取得する"""
    db_path = os.path.join("src", "syllabus", str(year), "data", f"syllabus_{year}.db")
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # syllabus_basicテーブルからシラバスコードを取得
        cursor.execute("""
            SELECT DISTINCT syllabus_id
            FROM syllabus_basic
            WHERE syllabus_id IS NOT NULL
        """)
        
        syllabus_masters = []
        for row in cursor.fetchall():
            syllabus_code = row[0]
            if syllabus_code:
                syllabus_masters.append({
                    'syllabus_code': syllabus_code,
                    'syllabus_year': year  # ユーザー入力の年度を使用
                })
        
        return syllabus_masters
        
    except sqlite3.Error as e:
        print(f"データベースエラー: {str(e)}")
        return []
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        return []
    finally:
        if conn:
            conn.close()

def create_syllabus_master_json(syllabus_masters: List[Dict]) -> str:
    """シラバスマスター情報のJSONファイルを作成する"""
    output_dir = os.path.join("updates", "syllabus_master", "add")
    os.makedirs(output_dir, exist_ok=True)
    
    # 現在の日時を取得してファイル名を生成
    current_time = datetime.now()
    filename = f"syllabus_master_{current_time.strftime('%Y%m%d_%H%M')}.json"
    output_file = os.path.join(output_dir, filename)
    
    data = {
        "syllabus_masters": [{
            "syllabus_code": syllabus["syllabus_code"],
            "syllabus_year": syllabus["syllabus_year"],
            "created_at": current_time.isoformat()
        } for syllabus in sorted(syllabus_masters, key=lambda x: (x["syllabus_year"], x["syllabus_code"]))]
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
        
        # データベースからシラバスマスター情報を取得
        syllabus_masters = get_syllabus_masters(year)
        print(f"抽出されたシラバスマスター情報: {len(syllabus_masters)}件")
        
        # JSONファイルの作成
        output_file = create_syllabus_master_json(syllabus_masters)
        print(f"JSONファイルを作成しました: {output_file}")
        
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        raise

if __name__ == "__main__":
    main() 