import os
import json
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

def get_latest_json(year: int) -> str:
    """指定された年度の最新のJSONファイルを取得する"""
    data_dir = os.path.join("src", "syllabus", str(year), "data")
    if not os.path.exists(data_dir):
        raise FileNotFoundError(f"ディレクトリが見つかりません: {data_dir}")
    
    json_files = [f for f in os.listdir(data_dir) if f.startswith('syllabus_') and f.endswith('.json')]
    if not json_files:
        raise FileNotFoundError(f"JSONファイルが見つかりません: {data_dir}")
    
    # ファイル名のタイムスタンプでソートして最新のものを取得
    latest_json = sorted(json_files)[-1]
    return os.path.join(data_dir, latest_json)

def extract_instructor_info(json_data: Dict) -> List[Dict]:
    """JSONデータから教員情報を抽出する"""
    instructors = []
    
    for syllabus in json_data.get("content", []):
        for instructor in syllabus.get("instructors", []):
            instructor_info = {
                'last_name': instructor.get('last_name_kanji', ''),
                'first_name': instructor.get('first_name_kanji', ''),
                'last_name_kana': instructor.get('last_name_kana', ''),
                'first_name_kana': instructor.get('first_name_kana', '')
            }
            # 空の値を持つ教員情報は除外
            if all(instructor_info.values()):
                instructors.append(instructor_info)
    
    return instructors

def create_instructor_json(instructors: Set[Dict]) -> str:
    """教員情報のJSONファイルを作成する"""
    output_dir = os.path.join("updates", "instructor", "add")
    os.makedirs(output_dir, exist_ok=True)
    
    # 現在の日時を取得してファイル名を生成
    current_time = datetime.now()
    filename = f"instructor_{current_time.strftime('%Y%m%d_%H%M')}.json"
    output_file = os.path.join(output_dir, filename)
    
    data = {
        "instructors": [{
            "last_name": instructor["last_name"],
            "first_name": instructor["first_name"],
            "last_name_kana": instructor["last_name_kana"],
            "first_name_kana": instructor["first_name_kana"],
            "created_at": current_time.isoformat()
        } for instructor in sorted(instructors, key=lambda x: (x["last_name_kana"], x["first_name_kana"]))]
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
        
        # 最新のJSONファイルを取得
        json_file = get_latest_json(year)
        print(f"処理対象ファイル: {json_file}")
        
        # JSONファイルを読み込む
        with open(json_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        # 教員情報の抽出
        all_instructors = set()
        instructors = extract_instructor_info(json_data)
        
        # 各教員の情報をタプルに変換してセットに追加（重複を防ぐため）
        for instructor in instructors:
            instructor_tuple = tuple(sorted(instructor.items()))
            all_instructors.add(instructor_tuple)
        
        # タプルを辞書に戻す
        instructor_dicts = [dict(t) for t in all_instructors]
        print(f"抽出された教員情報: {len(instructor_dicts)}件")
        
        # JSONファイルの作成
        output_file = create_instructor_json(instructor_dicts)
        print(f"JSONファイルを作成しました: {output_file}")
        
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        raise

if __name__ == "__main__":
    main() 