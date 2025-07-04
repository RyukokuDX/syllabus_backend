import os
import json
import glob
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
    """JSONファイルからシラバスマスター情報を取得する"""
    json_dir = os.path.join("src", "syllabus", str(year), "json")
    
    if not os.path.exists(json_dir):
        print(f"ディレクトリが存在しません: {json_dir}")
        return []
    
    # JSONファイルのパターンを取得
    json_pattern = os.path.join(json_dir, "*.json")
    json_files = glob.glob(json_pattern)
    
    if not json_files:
        print(f"JSONファイルが見つかりません: {json_pattern}")
        return []
    
    syllabus_masters = []
    syllabus_codes = set()  # 重複チェック用
    
    for json_file in tqdm(json_files, desc="JSONファイルを処理中"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # JSONファイルからシラバスコードを抽出
            # ファイル名から抽出する場合
            filename = os.path.basename(json_file)
            if filename.endswith('.json'):
                syllabus_code = filename[:-5]  # .jsonを除去
                
                # 重複チェック
                if syllabus_code not in syllabus_codes:
                    syllabus_codes.add(syllabus_code)
                    syllabus_masters.append({
                        'syllabus_code': syllabus_code,
                        'syllabus_year': year
                    })
            
            # または、JSONデータ内から抽出する場合（データ構造に応じて調整）
            # if isinstance(data, dict) and 'syllabus_code' in data:
            #     syllabus_code = data['syllabus_code']
            #     if syllabus_code not in syllabus_codes:
            #         syllabus_codes.add(syllabus_code)
            #         syllabus_masters.append({
            #             'syllabus_code': syllabus_code,
            #             'syllabus_year': year
            #         })
            
        except json.JSONDecodeError as e:
            print(f"JSONファイルの解析エラー {json_file}: {str(e)}")
            continue
        except Exception as e:
            print(f"ファイル処理エラー {json_file}: {str(e)}")
            continue
    
    return syllabus_masters

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
        
        # JSONファイルからシラバスマスター情報を取得
        syllabus_masters = get_syllabus_masters(year)
        print(f"抽出されたシラバスマスター情報: {len(syllabus_masters)}件")
        
        if not syllabus_masters:
            print("シラバスマスター情報が見つかりませんでした。")
            return
        
        # JSONファイルの作成
        output_file = create_syllabus_master_json(syllabus_masters)
        print(f"JSONファイルを作成しました: {output_file}")
        
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        raise

if __name__ == "__main__":
    main() 