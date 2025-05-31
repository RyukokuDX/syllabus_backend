import os
import json
from typing import List, Dict, Set
from datetime import datetime
from tqdm import tqdm

def create_syllabus_master_json(syllabus_masters: Set[Dict]) -> str:
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

def get_year_from_user() -> int:
    """ユーザーから年度を入力してもらう"""
    while True:
        try:
            year = input("年度を入力してください（空の場合は現在の年度）: ").strip()
            if not year:
                return datetime.now().year
            year = int(year)
            if 2000 <= year <= 2100:  # 妥当な年度の範囲をチェック
                return year
            print("2000年から2100年の間で入力してください。")
        except ValueError:
            print("有効な数値を入力してください。")

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
        
        # シラバスマスター情報を処理
        all_syllabus_masters = set()
        processed_count = 0
        
        for syllabus in tqdm(json_data.get("content", []), desc="シラバスマスター情報を処理中"):
            if not syllabus.get("syllabus_code"):
                continue
            
            syllabus_master_info = {
                "syllabus_code": syllabus["syllabus_code"],
                "syllabus_year": syllabus["syllabus_year"]
            }
            syllabus_master_tuple = tuple(sorted(syllabus_master_info.items()))
            all_syllabus_masters.add(syllabus_master_tuple)
            processed_count += 1
        
        # タプルを辞書に戻す
        syllabus_master_dicts = [dict(t) for t in all_syllabus_masters]
        print(f"抽出されたシラバスマスター情報: {len(syllabus_master_dicts)}件")
        
        # JSONファイルの作成
        output_file = create_syllabus_master_json(syllabus_master_dicts)
        print(f"JSONファイルを作成しました: {output_file}")
        
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        raise

if __name__ == "__main__":
    main() 