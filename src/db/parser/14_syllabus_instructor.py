# File Version: v2.7.0
# Project Version: v2.7.0
# Last Updated: 2025-07-06

import os
import json
import glob
from typing import List, Dict, Set
from datetime import datetime
from tqdm import tqdm
from .utils import get_db_connection, get_syllabus_master_id_from_db, get_year_from_user, normalize_subject_name

def get_syllabus_instructor_data(year: int) -> List[Dict]:
    """JSONファイルからシラバス教員関連情報を取得する"""
    syllabus_instructors = []
    
    # スクリプトのディレクトリを基準にパスを生成
    script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    json_pattern = os.path.join(script_dir, "syllabus", str(year), "json", "*.json")
    
    json_files = glob.glob(json_pattern)
    
    if not json_files:
        print(f"警告: {year}年度のJSONファイルが見つかりません: {json_pattern}")
        return syllabus_instructors
    
    print(f"{len(json_files)}個のJSONファイルを処理中...")
    
    # デバッグ用カウンター
    processed_files = 0
    found_instructors = 0
    
    for json_file in tqdm(json_files, desc="シラバス教員情報を抽出中"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 基本情報から科目コードと年度を取得
            syllabus_code = data.get("科目コード")
            basic_info = data.get("基本情報", {})
            syllabus_year = int(basic_info.get("開講年度", {}).get("内容", str(year)))
            
            if not syllabus_code:
                continue
            
            # 指定されたパスから教員名を取得
            # 基本情報.漢字氏名.内容.担当者一覧.氏名
            instructor_names = []
            
            try:
                # パスを段階的に取得
                kanji_name_info = basic_info.get("漢字氏名", {})
                content_info = kanji_name_info.get("内容", {})
                instructor_list = content_info.get("担当者一覧", [])
                
                # デバッグ出力（最初の数ファイルのみ）
                if processed_files < 5:
                    print(f"\nデバッグ: {os.path.basename(json_file)}")
                    print(f"  漢字氏名情報: {kanji_name_info}")
                    print(f"  内容情報: {content_info}")
                    print(f"  担当者一覧: {instructor_list}")
                
                # 担当者一覧から氏名を取得
                if isinstance(instructor_list, list):
                    for instructor in instructor_list:
                        if isinstance(instructor, dict) and "氏名" in instructor:
                            instructor_name = instructor["氏名"]
                            if instructor_name and instructor_name.strip():
                                instructor_names.append(instructor_name.strip())
                
                # 担当者一覧が取得できない場合の代替手段
                if not instructor_names:
                    # 文字列表記を取得
                    text_notation = content_info.get("文字列表記")
                    if text_notation and text_notation.strip():
                        instructor_names.append(text_notation.strip())
                    
                    # 元の内容を取得
                    original_content = kanji_name_info.get("元の内容")
                    if original_content and original_content.strip():
                        instructor_names.append(original_content.strip())
                
                # デバッグ出力（最初の数ファイルのみ）
                if processed_files < 5:
                    print(f"  取得された教員名: {instructor_names}")
                
                processed_files += 1
                
            except Exception as e:
                print(f"教員名取得エラー: {json_file} - {str(e)}")
                continue
            
            # 各教員についてシラバス教員関連情報を作成
            for instructor_name in instructor_names:
                if instructor_name and instructor_name.strip():
                    # 教員名を正規化（既存のnormalize_subject_name関数を使用）
                    normalized_name = normalize_subject_name(instructor_name.strip())
                    
                    syllabus_instructor = {
                        "syllabus_code": syllabus_code,
                        "syllabus_year": syllabus_year,
                        "instructor_name": normalized_name,
                        "original_name": instructor_name.strip(),
                        "source_file": os.path.basename(json_file)
                    }
                    syllabus_instructors.append(syllabus_instructor)
                    found_instructors += 1
                    
        except Exception as e:
            print(f"エラー: {json_file}の処理中にエラーが発生しました: {str(e)}")
            continue
    
    print(f"\nデバッグ情報:")
    print(f"  処理したファイル数: {processed_files}")
    print(f"  見つかった教員数: {found_instructors}")
    
    return syllabus_instructors

def create_syllabus_instructor_json(syllabus_instructors: List[Dict]) -> str:
    """シラバス教員関連情報のJSONファイルを作成する"""
    output_dir = os.path.join("updates", "syllabus_instructor", "add")
    os.makedirs(output_dir, exist_ok=True)
    
    # 現在の日時を取得してファイル名を生成
    current_time = datetime.now()
    filename = f"syllabus_instructor_{current_time.strftime('%Y%m%d_%H%M%S')}.json"
    output_file = os.path.join(output_dir, filename)
    
    data = {
        "syllabus_instructors": [{
            "syllabus_id": instructor["syllabus_id"],
            "instructor_id": instructor["instructor_id"],
            "created_at": current_time.isoformat()
        } for instructor in sorted(syllabus_instructors, key=lambda x: (x["syllabus_id"], x["instructor_id"]))]
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return output_file

def get_instructor_id_from_db(session, instructor_name: str) -> int:
    """教員IDを取得する（正規化された名前で検索）"""
    try:
        from sqlalchemy import text
        
        # 教員名を正規化（既存のnormalize_subject_name関数を使用）
        normalized_name = normalize_subject_name(instructor_name)
        
        # 教員IDを取得（正規化された名前で検索）
        query = text("""
            SELECT instructor_id 
            FROM instructor 
            WHERE name = :name
            ORDER BY instructor_id
            LIMIT 1
        """)
        
        result = session.execute(
            query,
            {"name": normalized_name}
        ).first()
        
        return result[0] if result else None
    except Exception as e:
        print(f"[DB接続エラー] instructor取得時にエラー: {str(e)}")
        session.rollback()
        return None

def process_syllabus_instructor_data(syllabus_instructors: List[Dict], session) -> tuple[List[Dict], List[str]]:
    """シラバス教員関連データを処理する"""
    processed_data = []
    errors = []
    
    print("データベースからIDを取得中...")
    
    for instructor_data in tqdm(syllabus_instructors, desc="シラバス教員情報を処理中"):
        try:
            # シラバスマスターIDを取得
            syllabus_id = get_syllabus_master_id_from_db(
                session, 
                instructor_data["syllabus_code"], 
                instructor_data["syllabus_year"]
            )
            
            if not syllabus_id:
                errors.append(f"シラバスマスターが見つかりません: {instructor_data['syllabus_code']} ({instructor_data['syllabus_year']})")
                continue
            
            # 教員IDを取得（正規化された名前で検索）
            instructor_id = get_instructor_id_from_db(session, instructor_data["instructor_name"])
            
            if not instructor_id:
                errors.append(f"教員が見つかりません: {instructor_data['original_name']} (正規化: {instructor_data['instructor_name']})")
                continue
            
            # 処理済みデータを作成
            processed_instructor = {
                "syllabus_id": syllabus_id,
                "instructor_id": instructor_id,
                "source_file": instructor_data["source_file"]
            }
            
            processed_data.append(processed_instructor)
            
        except Exception as e:
            errors.append(f"データ処理エラー: {instructor_data.get('syllabus_code', 'Unknown')} - {str(e)}")
            continue
    
    return processed_data, errors

def main():
    """メイン処理"""
    print("=== シラバス教員関連パーサー ===")
    
    try:
        # 年度を取得
        year = get_year_from_user()
        print(f"処理対象年度: {year}")
        
        # データベース接続
        print("データベースに接続中...")
        session = get_db_connection()
        
        # JSONファイルからデータを取得
        print("JSONファイルからシラバス教員情報を抽出中...")
        syllabus_instructors = get_syllabus_instructor_data(year)
        
        if not syllabus_instructors:
            print("抽出されたシラバス教員情報がありません。")
            return
        
        print(f"抽出されたシラバス教員情報: {len(syllabus_instructors)}件")
        
        # データを処理
        processed_data, errors = process_syllabus_instructor_data(syllabus_instructors, session)
        
        if errors:
            print(f"\n警告: {len(errors)}件のエラーが発生しました:")
            for error in errors[:10]:  # 最初の10件のみ表示
                print(f"  - {error}")
            if len(errors) > 10:
                print(f"  ... 他 {len(errors) - 10}件")
        
        if not processed_data:
            print("処理可能なシラバス教員情報がありません。")
            return
        
        print(f"処理済みシラバス教員情報: {len(processed_data)}件")
        
        # JSONファイルを作成
        output_file = create_syllabus_instructor_json(processed_data)
        print(f"JSONファイルを作成しました: {output_file}")
        
        # 重複チェック
        unique_pairs = set()
        duplicates = []
        
        for data in processed_data:
            pair = (data["syllabus_id"], data["instructor_id"])
            if pair in unique_pairs:
                duplicates.append(pair)
            else:
                unique_pairs.add(pair)
        
        if duplicates:
            print(f"警告: {len(duplicates)}件の重複データが見つかりました")
        
        print("=== 処理完了 ===")
        
    except Exception as e:
        print(f"エラー: {str(e)}")
        return
    finally:
        if 'session' in locals():
            session.close()

if __name__ == "__main__":
    main()