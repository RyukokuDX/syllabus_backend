# File Version: v2.3.0
# Project Version: v2.3.0
# Last Updated: 2025-07-02

import os
import json
import glob
from typing import List, Set
from datetime import datetime
from tqdm import tqdm
from .utils import normalize_faculty_name

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
    """JSONファイルから学部名を抽出する"""
    faculty_names = set()
    # スクリプトのディレクトリを基準にパスを生成
    script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    json_pattern = os.path.join(script_dir, "syllabus", str(year), "json", "*.json")
    
    print(f"JSONファイルパターン: {json_pattern}")
    
    json_files = glob.glob(json_pattern)
    if not json_files:
        raise FileNotFoundError(f"JSONファイルが見つかりません: {json_pattern}")
    
    total_files = len(json_files)
    print(f"処理対象ファイル数: {total_files}件")
    
    for json_file in tqdm(json_files, desc="JSONファイル処理", unit="file"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # 基本情報.対象学部.内容から学部名を取得
                if '基本情報' in data and '対象学部' in data['基本情報'] and '内容' in data['基本情報']['対象学部']:
                    departments = data['基本情報']['対象学部']['内容']
                    if departments:
                        # カンマで区切られた学部名を分割して追加
                        for dept in departments.split(','):
                            dept = dept.strip()
                            if dept:  # 空文字でない場合のみ追加
                                # 学部課程名を正規化（utils.pyのnormalize_faculty_nameを使用）
                                normalized_dept = normalize_faculty_name(dept)
                                if normalized_dept != 'NULL':  # NULLでない場合のみ追加
                                    faculty_names.add(normalized_dept)
        
        except json.JSONDecodeError as e:
            print(f"\nJSONファイルの解析エラー ({json_file}): {str(e)}")
            continue
        except Exception as e:
            print(f"\nファイル処理エラー ({json_file}): {str(e)}")
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