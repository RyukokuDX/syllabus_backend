# File Version: v1.3.3
# Project Version: v1.3.3
# Last Updated: 2025-06-15

import os
import json
import glob
from typing import List, Dict, Set
from datetime import datetime
from tqdm import tqdm
from .utils import normalize_subject_name, get_year_from_user

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
    """JSONファイルから教員情報を取得する"""
    instructors = set()
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
                
                # 基本情報から教員情報を取得
                if '基本情報' in data:
                    basic_info = data['基本情報']
                    kanji_info = basic_info.get('漢字氏名', {}).get('内容', {})
                    kana_info = basic_info.get('カナ氏名', {}).get('内容', {})
                    
                    # 担当者一覧から教員情報を取得
                    kanji_instructors = kanji_info.get('担当者一覧', [])
                    kana_instructors = kana_info.get('担当者一覧', [])
                    
                    # 担当者数が一致することを確認
                    if len(kanji_instructors) != len(kana_instructors):
                        print(f"\n警告: 漢字氏名とカナ氏名の担当者数が一致しません: {json_file}")
                        print(f"漢字氏名の担当者数: {len(kanji_instructors)}")
                        print(f"カナ氏名の担当者数: {len(kana_instructors)}")
                        continue
                    
                    # 各担当者の情報を処理
                    for kanji_instructor, kana_instructor in zip(kanji_instructors, kana_instructors):
                        kanji_name = kanji_instructor.get('氏名', '')
                        kana_name = kana_instructor.get('カナ氏名', '')
                        
                        if kanji_name:  # 漢字名が存在する場合のみ追加
                            # 名前の正規化処理を適用
                            normalized_name = normalize_subject_name(kanji_name)
                            normalized_kana = normalize_subject_name(kana_name) if kana_name else None
                            
                            if normalized_name:  # 空文字でない場合
                                instructor_info = {
                                    'name': normalized_name,
                                    'name_kana': normalized_kana
                                }
                                # タプルに変換してセットに追加（重複を防ぐため）
                                instructor_tuple = tuple(sorted(instructor_info.items()))
                                instructors.add(instructor_tuple)
        
        except json.JSONDecodeError as e:
            print(f"\nJSONファイルの解析エラー ({json_file}): {str(e)}")
            continue
        except Exception as e:
            print(f"\nファイル処理エラー ({json_file}): {str(e)}")
            continue
    
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