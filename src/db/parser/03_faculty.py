import os
import json
import csv
from typing import List, Set
from datetime import datetime
import chardet

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
    base_dir = os.path.join("src", "syllabus", str(year), "search_page")
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

def extract_faculty_names(csv_files: List[str]) -> Set[str]:
    """CSVファイルから学部名を抽出する"""
    faculty_names = set()
    
    for csv_file in csv_files:
        try:
            # エンコーディングを自動検出
            encoding = detect_encoding(csv_file)
            if not encoding:
                encoding = 'utf-8'  # デフォルトはUTF-8
            
            with open(csv_file, 'r', encoding=encoding, errors='replace') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if '学部' in row and row['学部']:
                        faculty_names.add(row['学部'].strip())
        except Exception as e:
            print(f"警告: {csv_file}の処理中にエラーが発生しました: {str(e)}")
            continue
    
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
        
        # CSVファイルの取得
        csv_files = get_csv_files(year)
        print(f"処理対象ファイル: {len(csv_files)}件")
        
        # 学部名の抽出
        faculty_names = extract_faculty_names(csv_files)
        print(f"抽出された学部名: {len(faculty_names)}件")
        
        # JSONファイルの作成
        output_file = create_faculty_json(faculty_names)
        print(f"JSONファイルを作成しました: {output_file}")
        
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        raise

if __name__ == "__main__":
    main() 