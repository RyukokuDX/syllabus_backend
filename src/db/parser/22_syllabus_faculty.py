# -*- coding: utf-8 -*-
# File Version: v2.1.1
# Project Version: v2.1.2
# Last Updated: 2025-07-01

import os
import json
import csv
import sys
from typing import List, Dict, Set
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm

# 現在のディレクトリをPythonパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from utils import normalize_subject_name, normalize_faculty_name

def get_db_connection():
    """データベース接続を取得する"""
    # 環境変数から接続情報を取得
    user = os.getenv('POSTGRES_USER', 'postgres')
    password = os.getenv('POSTGRES_PASSWORD', 'postgres')
    host = os.getenv('POSTGRES_HOST', 'localhost')
    port = os.getenv('POSTGRES_PORT', '5432')
    db = os.getenv('POSTGRES_DB', 'syllabus_db')

    # 接続文字列を作成
    connection_string = f"postgresql://{user}:{password}@{host}:{port}/{db}"
    
    # エンジンを作成
    engine = create_engine(
        connection_string,
        connect_args={
            'options': '-c client_encoding=utf-8'
        }
    )
    
    # セッションを作成
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # セッション作成時に一度だけ文字エンコーディングを設定
    session.execute(text("SET client_encoding TO 'utf-8'"))
    session.commit()
    
    return session

def get_syllabus_master_id_from_db(session, syllabus_code: str, syllabus_year: int) -> int:
    """シラバスマスターIDを取得する"""
    try:
        # シラバスマスターIDを取得
        query = text("""
            SELECT syllabus_id 
            FROM syllabus_master 
            WHERE syllabus_code = :code 
            AND syllabus_year = :year
        """)
        
        result = session.execute(
            query,
            {"code": syllabus_code, "year": syllabus_year}
        ).first()
        
        return result[0] if result else None
    except Exception as e:
        session.rollback()
        return None

def get_faculty_id_from_db(session, faculty_name: str) -> int:
    """学部・課程IDを取得する"""
    try:
        # 学部・課程名を正規化
        normalized_name = normalize_text(faculty_name, handle_null=True)
        
        # 学部・課程IDを取得
        query = text("""
            SELECT faculty_id 
            FROM faculty 
            WHERE faculty_name = :name
        """)
        
        result = session.execute(
            query,
            {"name": normalized_name}
        ).first()
        
        return result[0] if result else None
    except Exception as e:
        session.rollback()
        return None

def create_syllabus_faculty_json(syllabus_faculties: List[Dict]) -> str:
    """シラバス学部関連情報のJSONファイルを作成する"""
    output_dir = os.path.join("updates", "syllabus_faculty", "add")
    os.makedirs(output_dir, exist_ok=True)
    
    # 現在の日時を取得してファイル名を生成
    current_time = datetime.now()
    filename = f"syllabus_faculty_{current_time.strftime('%Y%m%d_%H%M')}.json"
    output_file = os.path.join(output_dir, filename)
    
    data = {
        "syllabus_faculties": [{
            "syllabus_id": faculty["syllabus_id"],
            "faculty_id": faculty["faculty_id"],
            "created_at": current_time.isoformat()
        } for faculty in sorted(syllabus_faculties, key=lambda x: (
            x["syllabus_id"],
            x["faculty_id"]
        ))]
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return output_file

def create_warning_csv(year: int, errors: List[Dict]) -> str:
    """エラー内容を詳細にCSVファイルに記載する"""
    # 警告ディレクトリを作成
    warning_dir = os.path.join("warning", str(year))
    os.makedirs(warning_dir, exist_ok=True)
    
    # 現在の日時を取得してファイル名を生成
    current_time = datetime.now()
    filename = f"syllabus_faculty_{current_time.strftime('%Y%m%d_%H%M')}.csv"
    output_file = os.path.join(warning_dir, filename)
    
    # CSVファイルにエラー情報を書き込み
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        
        # ヘッダー行
        writer.writerow([
            'ファイル名',
            '科目名',
            '科目コード',
            '開講年度',
            '対象学部',
            'エラータイプ',
            'エラー詳細',
            '正規化後学部名',
            '処理日時'
        ])
        
        # エラーデータ
        for error in errors:
            writer.writerow([
                error.get('file_name', ''),
                error.get('subject_name', ''),
                error.get('syllabus_code', ''),
                error.get('syllabus_year', ''),
                error.get('faculty_name', ''),
                error.get('error_type', ''),
                error.get('error_detail', ''),
                error.get('normalized_faculty_name', ''),
                error.get('processed_at', '')
            ])
    
    return output_file

def get_latest_json(year: int) -> str:
    """指定された年度の最新のJSONファイルを取得する"""
    data_dir = os.path.join("src", "syllabus", str(year), "json")
    if not os.path.exists(data_dir):
        raise FileNotFoundError(f"ディレクトリが見つかりません: {data_dir}")
    
    json_files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
    if not json_files:
        raise FileNotFoundError(f"JSONファイルが見つかりません: {data_dir}")
    
    # ファイル名でソートして最新のものを取得
    json_files.sort()
    latest_file = json_files[-1]
    
    return os.path.join(data_dir, latest_file)

def get_all_json_files(year: int) -> List[str]:
    """指定された年度のすべてのJSONファイルを取得する"""
    data_dir = os.path.join("src", "syllabus", str(year), "json")
    if not os.path.exists(data_dir):
        raise FileNotFoundError(f"ディレクトリが見つかりません: {data_dir}")
    
    json_files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
    if not json_files:
        raise FileNotFoundError(f"JSONファイルが見つかりません: {data_dir}")
    
    return [os.path.join(data_dir, f) for f in sorted(json_files)]

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

def process_syllabus_faculty_json(json_file: str, session) -> tuple[List[Dict], List[Dict]]:
    """シラバスJSONファイルから学部関連情報を抽出する"""
    syllabus_faculties = []
    errors = []
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 基本情報の取得
        syllabus_code = data.get('科目コード', '')  # 科目コードは基本情報の外にある
        syllabus_year = data.get('基本情報', {}).get('開講年度', {}).get('内容', '')
        subject_name = data.get('基本情報', {}).get('科目名', {}).get('内容', '')
        
        # 対象学部情報の取得
        faculty_names = []
        if '基本情報' in data and '対象学部' in data['基本情報'] and '内容' in data['基本情報']['対象学部']:
            departments = data['基本情報']['対象学部']['内容']
            if departments:
                # カンマで区切られた学部名を分割
                for dept in departments.split(','):
                    dept = dept.strip()
                    if dept:  # 空文字でない場合のみ追加
                        faculty_names.append(dept)
        
        # シラバスマスターIDを取得
        if syllabus_code and syllabus_year:
            try:
                syllabus_year_int = int(syllabus_year)
                syllabus_master_id = get_syllabus_master_id_from_db(session, syllabus_code, syllabus_year_int)
                
                if syllabus_master_id is None:
                    errors.append({
                        'file_name': os.path.basename(json_file),
                        'subject_name': subject_name,
                        'syllabus_code': syllabus_code,
                        'syllabus_year': syllabus_year,
                        'faculty_name': ', '.join(faculty_names),
                        'error_type': 'SYLLABUS_MASTER_NOT_FOUND',
                        'error_detail': f'シラバスマスターが見つかりません: {syllabus_code}, {syllabus_year}',
                        'normalized_faculty_name': '',
                        'processed_at': datetime.now().isoformat()
                    })
                else:
                    # 各学部・課程について処理
                    for faculty_name in faculty_names:
                        # 学部・課程名を正規化
                        normalized_faculty_name = normalize_faculty_name(faculty_name)
                        
                        if normalized_faculty_name == 'NULL':
                            errors.append({
                                'file_name': os.path.basename(json_file),
                                'subject_name': subject_name,
                                'syllabus_code': syllabus_code,
                                'syllabus_year': syllabus_year,
                                'faculty_name': faculty_name,
                                'error_type': 'FACULTY_NAME_NORMALIZATION_FAILED',
                                'error_detail': f'学部・課程名の正規化に失敗: {faculty_name}',
                                'normalized_faculty_name': normalized_faculty_name,
                                'processed_at': datetime.now().isoformat()
                            })
                            continue
                        
                        # 学部・課程IDを取得
                        faculty_id = get_faculty_id_from_db(session, normalized_faculty_name)
                        
                        if faculty_id is None:
                            errors.append({
                                'file_name': os.path.basename(json_file),
                                'subject_name': subject_name,
                                'syllabus_code': syllabus_code,
                                'syllabus_year': syllabus_year,
                                'faculty_name': faculty_name,
                                'error_type': 'FACULTY_NOT_FOUND',
                                'error_detail': f'学部・課程が見つかりません: {normalized_faculty_name}',
                                'normalized_faculty_name': normalized_faculty_name,
                                'processed_at': datetime.now().isoformat()
                            })
                            continue
                        
                        # シラバス学部関連情報を追加
                        syllabus_faculties.append({
                            'syllabus_id': syllabus_master_id,
                            'faculty_id': faculty_id
                        })
                
            except ValueError:
                errors.append({
                    'file_name': os.path.basename(json_file),
                    'subject_name': subject_name,
                    'syllabus_code': syllabus_code,
                    'syllabus_year': syllabus_year,
                    'faculty_name': ', '.join(faculty_names),
                    'error_type': 'INVALID_YEAR_FORMAT',
                    'error_detail': f'開講年度の形式が不正: {syllabus_year}',
                    'normalized_faculty_name': '',
                    'processed_at': datetime.now().isoformat()
                })
        else:
            errors.append({
                'file_name': os.path.basename(json_file),
                'subject_name': subject_name,
                'syllabus_code': syllabus_code,
                'syllabus_year': syllabus_year,
                'faculty_name': ', '.join(faculty_names),
                'error_type': 'MISSING_BASIC_INFO',
                'error_detail': '科目コードまたは開講年度が不足',
                'normalized_faculty_name': '',
                'processed_at': datetime.now().isoformat()
            })
    
    except json.JSONDecodeError as e:
        errors.append({
            'file_name': os.path.basename(json_file),
            'subject_name': '',
            'syllabus_code': '',
            'syllabus_year': '',
            'faculty_name': '',
            'error_type': 'JSON_DECODE_ERROR',
            'error_detail': f'JSONファイルの解析エラー: {str(e)}',
            'normalized_faculty_name': '',
            'processed_at': datetime.now().isoformat()
        })
    except Exception as e:
        errors.append({
            'file_name': os.path.basename(json_file),
            'subject_name': '',
            'syllabus_code': '',
            'syllabus_year': '',
            'faculty_name': '',
            'error_type': 'UNKNOWN_ERROR',
            'error_detail': f'予期しないエラー: {str(e)}',
            'normalized_faculty_name': '',
            'processed_at': datetime.now().isoformat()
        })
    
    return syllabus_faculties, errors

def main():
    """メイン処理"""
    try:
        # 年度の取得
        year = get_year_from_user()
        print(f"処理対象年度: {year}")
        
        # データベース接続
        session = get_db_connection()
        print("データベースに接続しました")
        
        # JSONファイルの取得
        json_files = get_all_json_files(year)
        print(f"処理対象ファイル数: {len(json_files)}件")
        
        # シラバス学部関連情報の抽出
        all_syllabus_faculties = []
        all_errors = []
        
        for json_file in tqdm(json_files, desc="JSONファイル処理", unit="file"):
            syllabus_faculties, errors = process_syllabus_faculty_json(json_file, session)
            all_syllabus_faculties.extend(syllabus_faculties)
            all_errors.extend(errors)
        
        # 重複を除去（syllabus_id, faculty_idの組み合わせでユニーク）
        unique_syllabus_faculties = []
        seen_combinations = set()
        
        for faculty in all_syllabus_faculties:
            combination = (faculty['syllabus_id'], faculty['faculty_id'])
            if combination not in seen_combinations:
                seen_combinations.add(combination)
                unique_syllabus_faculties.append(faculty)
        
        print(f"抽出されたシラバス学部関連: {len(unique_syllabus_faculties)}件")
        print(f"エラー件数: {len(all_errors)}件")
        
        # JSONファイルの作成
        if unique_syllabus_faculties:
            output_file = create_syllabus_faculty_json(unique_syllabus_faculties)
            print(f"JSONファイルを作成しました: {output_file}")
        
        # エラーファイルの作成
        if all_errors:
            warning_file = create_warning_csv(year, all_errors)
            print(f"警告ファイルを作成しました: {warning_file}")
        
        session.close()
        print("処理が完了しました")
        
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        raise

if __name__ == "__main__":
    main() 