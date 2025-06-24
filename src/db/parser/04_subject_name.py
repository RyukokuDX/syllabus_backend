# File Version: v1.4.0
# Project Version: v1.4.0
# Last Updated: 2025-06-24

import os
import json
import glob
from typing import List, Set, Dict
from datetime import datetime
from tqdm import tqdm
from .utils import normalize_subject_name, get_year_from_user

def get_subject_names(year: int) -> Set[str]:
    """JSONファイルから科目名を抽出する"""
    subject_names = set()
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
                
                # 基本情報.科目名.内容から科目名を取得
                if '基本情報' in data and '科目名' in data['基本情報'] and '内容' in data['基本情報']['科目名']:
                    subject_name = data['基本情報']['科目名']['内容']
                    if subject_name:
                        # 科目名の正規化処理を適用
                        normalized_name = normalize_subject_name(subject_name)
                        if normalized_name:  # 空文字でない場合
                            subject_names.add(normalized_name)
        
        except json.JSONDecodeError as e:
            print(f"\nJSONファイルの解析エラー ({json_file}): {str(e)}")
            continue
        except Exception as e:
            print(f"\nファイル処理エラー ({json_file}): {str(e)}")
            continue
    
    return subject_names

def create_subject_name_json(subject_names: Set[str]) -> None:
    """科目名のJSONファイルを作成する"""
    output_dir = os.path.join("updates", "subject_name", "add")
    os.makedirs(output_dir, exist_ok=True)
    
    # 現在の日時を取得してファイル名を生成
    current_time = datetime.now()
    filename = f"subject_name_{current_time.strftime('%Y%m%d_%H%M')}.json"
    output_file = os.path.join(output_dir, filename)
    
    data = {
        "subject_names": [{
            "name": name,
            "created_at": current_time.isoformat()
        } for name in sorted(subject_names)]
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
        
        # 科目名の抽出
        subject_names = get_subject_names(year)
        print(f"抽出された科目名: {len(subject_names)}件")
        
        # JSONファイルの作成
        output_file = create_subject_name_json(subject_names)
        print(f"JSONファイルを作成しました: {output_file}")
        
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        raise

if __name__ == "__main__":
    main() 