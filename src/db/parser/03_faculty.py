import os
import json
import sqlite3
from typing import List, Set
from datetime import datetime

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

def get_faculty_names(year: int) -> Set[str]:
    """SQLiteデータベースから学部名を抽出する"""
    faculty_names = set()
    db_path = os.path.join("src", "syllabus", str(year), "data", f"syllabus_{year}.db")
    
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"データベースファイルが見つかりません: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # departmentsカラムから学部名を取得
        cursor.execute("SELECT DISTINCT departments FROM syllabus_basic WHERE departments IS NOT NULL")
        rows = cursor.fetchall()
        
        for row in rows:
            if row[0]:  # NULLでない場合
                # カンマで区切られた学部名を分割して追加
                departments = row[0].split(',')
                for dept in departments:
                    dept = dept.strip()
                    if dept:  # 空文字でない場合のみ追加
                        faculty_names.add(dept)
        
    except sqlite3.Error as e:
        print(f"データベースエラー: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()
    
    return faculty_names

def create_faculty_json(faculty_names: Set[str]) -> None:
    """学部情報のJSONファイルを作成する"""
    output_dir = os.path.join("updates", "faculty", "add")
    os.makedirs(output_dir, exist_ok=True)
    
    # 現在の日時を取得してファイル名を生成
    current_time = datetime.now()
    filename = f"faculty_{current_time.strftime('%Y%m%d_%H%M')}.json"
    output_file = os.path.join(output_dir, filename)
    
    data = {
        "faculties": [{
            "faculty_name": name,
            "created_at": current_time.isoformat()
        } for name in sorted(faculty_names)]
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
        
        # 学部名の抽出
        faculty_names = get_faculty_names(year)
        print(f"抽出された学部名: {len(faculty_names)}件")
        
        # JSONファイルの作成
        output_file = create_faculty_json(faculty_names)
        print(f"JSONファイルを作成しました: {output_file}")
        
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        raise

if __name__ == "__main__":
    main() 