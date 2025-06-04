import os
import json
import csv
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

def get_csv_files(year: int) -> List[str]:
    """指定された年度のCSVファイルのパスを取得する"""
    base_dir = os.path.join("src", "course_guide", str(year), "csv")
    if not os.path.exists(base_dir):
        raise FileNotFoundError(f"ディレクトリが見つかりません: {base_dir}")
    
    csv_files = [f for f in os.listdir(base_dir) if f.endswith('.csv')]
    if not csv_files:
        raise FileNotFoundError(f"CSVファイルが見つかりません: {base_dir}")
    
    return [os.path.join(base_dir, f) for f in csv_files]

def extract_syllabus_info(csv_file: str) -> List[Dict]:
    """CSVからシラバス情報を抽出する"""
    syllabi = []
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            syllabus_info = {
                'subject_name_id': int(row['科目名']),
                'faculty_id': int(row['学部課程']),
                'curriculum_year': int(row['年度']),
                'class_id': int(row['科目区分']),
                'subclass_id': int(row['科目小区分']) if row['科目小区分'] else None,
                'requirement_type': row['必須度'],
                'created_at': datetime.now().isoformat()
            }
            syllabi.append(syllabus_info)
    
    return syllabi

def create_syllabus_json(syllabi: Set[Dict]) -> str:
    """シラバス情報のJSONファイルを作成する"""
    output_dir = os.path.join("updates", "syllabus", "add")
    os.makedirs(output_dir, exist_ok=True)
    
    # 現在の日時を取得してファイル名を生成
    current_time = datetime.now()
    filename = f"syllabus_{current_time.strftime('%Y%m%d_%H%M')}.json"
    output_file = os.path.join(output_dir, filename)
    
    data = {
        "syllabi": [{
            "subject_name_id": syllabus["subject_name_id"],
            "faculty_id": syllabus["faculty_id"],
            "curriculum_year": syllabus["curriculum_year"],
            "class_id": syllabus["class_id"],
            "subclass_id": syllabus["subclass_id"],
            "requirement_type": syllabus["requirement_type"],
            "created_at": syllabus["created_at"]
        } for syllabus in sorted(syllabi, key=lambda x: (
            x["subject_name_id"],
            x["faculty_id"],
            x["curriculum_year"],
            x["class_id"],
            x["subclass_id"] if x["subclass_id"] is not None else 0
        ))]
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return output_file

def process_csv_file(csv_file: str) -> List[Dict]:
    """CSVファイルを処理してシラバス情報を抽出する"""
    return extract_syllabus_info(csv_file)

def main():
    """メイン処理"""
    try:
        # 年度の取得
        year = get_year_from_user()
        print(f"処理対象年度: {year}")
        
        # CSVファイルの取得
        csv_files = get_csv_files(year)
        print(f"処理対象ファイル数: {len(csv_files)}")
        
        # シラバス情報の抽出
        all_syllabi = set()
        for csv_file in tqdm(csv_files, desc="CSVファイル処理中"):
            syllabi = process_csv_file(csv_file)
            
            # 各シラバスの情報をタプルに変換してセットに追加（重複を防ぐため）
            for syllabus in syllabi:
                syllabus_tuple = tuple(sorted(syllabus.items()))
                all_syllabi.add(syllabus_tuple)
        
        # タプルを辞書に戻す
        syllabus_dicts = [dict(t) for t in all_syllabi]
        print(f"抽出されたシラバス情報: {len(syllabus_dicts)}件")
        
        # JSONファイルの作成
        output_file = create_syllabus_json(syllabus_dicts)
        print(f"JSONファイルを作成しました: {output_file}")
        
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        raise

if __name__ == "__main__":
    main() 