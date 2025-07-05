# -*- coding: utf-8 -*-
# File Version: v2.6.0
# Project Version: v2.6.0
# Last Updated: 2025-07-05

import os
import json
import csv
import re
from typing import List, Dict, Set
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm
from dotenv import load_dotenv
from .utils import normalize_subject_name, get_year_from_user

def get_current_year() -> int:
    """現在の年度を取得する"""
    return datetime.now().year

def clean_subject_name(name: str) -> str:
    """科目名をクリーニングする（[隔年開講]などを削除）"""
    if not name:
        return name
    
    # [隔年開講]を削除
    name = re.sub(r'\[隔年開講\]', '', name)
    
    # 前後の空白を削除
    name = name.strip()
    
    return name

def get_csv_files(year: int) -> List[str]:
    """指定された年度のCSVファイルのパスを取得する（csvサブディレクトリも含む）"""
    base_dir = os.path.join("src", "course_guide", str(year), "csv")
    if not os.path.exists(base_dir):
        raise FileNotFoundError(f"ディレクトリが見つかりません: {base_dir}")
    
    # csvサブディレクトリの問い合わせ
    subdirs = []
    for item in os.listdir(base_dir):
        item_path = os.path.join(base_dir, item)
        if os.path.isdir(item_path):
            subdirs.append(item)
    
    csv_files = []
    
    if subdirs:
        print(f"見つかったcsvサブディレクトリ: {', '.join(subdirs)}")
        while True:
            subdir_input = input("処理するcsvサブディレクトリを指定してください（空の場合は全て処理）: ").strip()
            if not subdir_input:
                # 全てのサブディレクトリとメインディレクトリを処理
                # メインディレクトリ（csv）のCSVファイルを取得
                for file in os.listdir(base_dir):
                    if file.endswith('.csv'):
                        csv_files.append(os.path.join(base_dir, file))
                
                # 全てのサブディレクトリのCSVファイルを取得
                for subdir in subdirs:
                    subdir_path = os.path.join(base_dir, subdir)
                    if os.path.isdir(subdir_path):
                        for file in os.listdir(subdir_path):
                            if file.endswith('.csv'):
                                csv_files.append(os.path.join(subdir_path, file))
                break
            elif subdir_input in subdirs:
                # 指定されたサブディレクトリのみ処理
                subdir_path = os.path.join(base_dir, subdir_input)
                if os.path.isdir(subdir_path):
                    for file in os.listdir(subdir_path):
                        if file.endswith('.csv'):
                            csv_files.append(os.path.join(subdir_path, file))
                break
            else:
                print(f"無効なサブディレクトリです。有効な選択肢: {', '.join(subdirs)}")
    else:
        # サブディレクトリがない場合はメインディレクトリのみ処理
        for file in os.listdir(base_dir):
            if file.endswith('.csv'):
                csv_files.append(os.path.join(base_dir, file))
    
    if not csv_files:
        raise FileNotFoundError(f"CSVファイルが見つかりません: {base_dir}")
    
    return csv_files

def get_db_connection(db_config: Dict[str, str]):
    """データベース接続を取得する"""
    # 接続文字列を作成
    connection_string = f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['db']}"
    
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

def get_subject_name_id_from_db(session, subject_name: str) -> int:
    """科目名IDを取得する"""
    try:
        # 科目名を正規化
        normalized_name = normalize_subject_name(subject_name)
        
        query = text("""
            SELECT subject_name_id 
            FROM subject_name 
            WHERE name = :name
            ORDER BY subject_name_id
            LIMIT 1
        """)
        
        result = session.execute(
            query,
            {"name": normalized_name}
        ).first()
        
        if result:
            return result[0]
        return None
            
    except Exception as e:
        tqdm.write(f"エラー: 科目名IDの取得中にエラーが発生しました: {str(e)}")
        session.rollback()
        return None

def get_faculty_id_from_db(session, faculty_name: str) -> int:
    """学部IDを取得する"""
    try:
        query = text("""
            SELECT faculty_id 
            FROM faculty 
            WHERE faculty_name = :name
            ORDER BY faculty_id
            LIMIT 1
        """)
        
        result = session.execute(
            query,
            {"name": faculty_name}
        ).first()
        
        if result:
            return result[0]
        return None
            
    except Exception as e:
        tqdm.write(f"エラー: 学部IDの取得中にエラーが発生しました: {str(e)}")
        session.rollback()
        return None

def get_subject_id_from_db(session, subject_name_id: int, faculty_id: int, curriculum_year: int) -> int:
    """科目IDを取得する"""
    try:
        query = text("""
            SELECT subject_id 
            FROM subject 
            WHERE subject_name_id = :subject_name_id
            AND faculty_id = :faculty_id
            AND curriculum_year = :curriculum_year
            ORDER BY subject_id
            LIMIT 1
        """)
        
        result = session.execute(
            query,
            {
                "subject_name_id": subject_name_id,
                "faculty_id": faculty_id,
                "curriculum_year": curriculum_year
            }
        ).first()
        
        if result:
            return result[0]
        return None
            
    except Exception as e:
        tqdm.write(f"エラー: 科目IDの取得中にエラーが発生しました: {str(e)}")
        session.rollback()
        return None

def get_attribute_id_from_db(session, attribute_name: str) -> int:
    """属性IDを取得する"""
    try:
        query = text("""
            SELECT attribute_id 
            FROM subject_attribute 
            WHERE attribute_name = :name
            ORDER BY attribute_id
            LIMIT 1
        """)
        
        result = session.execute(
            query,
            {"name": attribute_name}
        ).first()
        
        if result:
            return result[0]
        else:
            tqdm.write(f"エラー: 属性が見つかりません: {attribute_name}")
            return None
            
    except Exception as e:
        tqdm.write(f"エラー: 属性IDの取得中にエラーが発生しました: {str(e)}")
        session.rollback()
        return None

def create_warning_csv(year: int, errors: List[Dict]) -> str:
    """エラー内容を詳細にCSVファイルに記載する"""
    # 警告ディレクトリを作成
    warning_dir = os.path.join("warning", str(year))
    os.makedirs(warning_dir, exist_ok=True)
    
    # 現在の日時を取得してファイル名を生成
    current_time = datetime.now()
    filename = f"subject_attribute_value_{current_time.strftime('%Y%m%d_%H%M')}.csv"
    output_file = os.path.join(warning_dir, filename)
    
    # CSVファイルにエラー情報を書き込み
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        
        # ヘッダー行
        writer.writerow([
            'ファイル名',
            '行番号',
            '科目名',
            '学部課程',
            '年度',
            '属性名',
            '属性値',
            'エラータイプ',
            'エラー詳細',
            '正規化後科目名',
            '処理日時'
        ])
        
        # エラーデータ
        for error in errors:
            writer.writerow([
                error.get('file_name', ''),
                error.get('row_number', ''),
                error.get('subject_name', ''),
                error.get('faculty_name', ''),
                error.get('year', ''),
                error.get('attribute_name', ''),
                error.get('attribute_value', ''),
                error.get('error_type', ''),
                error.get('error_detail', ''),
                error.get('normalized_subject_name', ''),
                error.get('processed_at', '')
            ])
    
    return output_file

def extract_subject_attribute_values(csv_file: str, db_config: Dict[str, str], stats: Dict, errors: List[Dict]) -> List[Dict]:
    """CSVから科目属性値情報を抽出する"""
    attribute_values = []
    session = get_db_connection(db_config)
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            rows = list(reader)
            stats['total_items'] += len(rows)
            
            for row_idx, row in enumerate(rows, start=2):  # ヘッダー行を除いて2から開始
                try:
                    # 17_subject.pyで処理したフィールドを除外
                    processed_fields = {'科目名', '学部課程', '年度', '科目区分', '科目小区分', '必須度'}
                    attribute_fields = set(row.keys()) - processed_fields
                    
                    # 科目名を正規化
                    subject_name = row['科目名']
                    cleaned_subject_name = clean_subject_name(subject_name)
                    normalized_subject_name = normalize_subject_name(cleaned_subject_name)
                    
                    # 科目名IDを取得
                    subject_name_id = get_subject_name_id_from_db(session, cleaned_subject_name)
                    if subject_name_id is None:
                        error_info = {
                            'file_name': os.path.basename(csv_file),
                            'row_number': row_idx,
                            'subject_name': subject_name,
                            'faculty_name': row['学部課程'],
                            'year': row['年度'],
                            'attribute_name': '',
                            'attribute_value': '',
                            'normalized_subject_name': normalized_subject_name,
                            'error_type': '科目名ID未取得',
                            'error_detail': f'科目名が見つかりません: {cleaned_subject_name} (正規化後: {normalized_subject_name})',
                            'processed_at': datetime.now().isoformat()
                        }
                        errors.append(error_info)
                        stats['error_items'] += 1
                        error_type = '科目名ID未取得'
                        if error_type not in stats['specific_errors']:
                            stats['specific_errors'][error_type] = 0
                        stats['specific_errors'][error_type] += 1
                        continue
                    
                    # 学部IDを取得
                    faculty_id = get_faculty_id_from_db(session, row['学部課程'])
                    if faculty_id is None:
                        error_info = {
                            'file_name': os.path.basename(csv_file),
                            'row_number': row_idx,
                            'subject_name': subject_name,
                            'faculty_name': row['学部課程'],
                            'year': row['年度'],
                            'attribute_name': '',
                            'attribute_value': '',
                            'normalized_subject_name': normalized_subject_name,
                            'error_type': '学部ID未取得',
                            'error_detail': f'学部が見つかりません: {row["学部課程"]}',
                            'processed_at': datetime.now().isoformat()
                        }
                        errors.append(error_info)
                        stats['error_items'] += 1
                        error_type = '学部ID未取得'
                        if error_type not in stats['specific_errors']:
                            stats['specific_errors'][error_type] = 0
                        stats['specific_errors'][error_type] += 1
                        continue
                    
                    # 科目IDを取得
                    subject_id = get_subject_id_from_db(session, subject_name_id, faculty_id, int(row['年度']))
                    if subject_id is None:
                        error_info = {
                            'file_name': os.path.basename(csv_file),
                            'row_number': row_idx,
                            'subject_name': subject_name,
                            'faculty_name': row['学部課程'],
                            'year': row['年度'],
                            'attribute_name': '',
                            'attribute_value': '',
                            'normalized_subject_name': normalized_subject_name,
                            'error_type': '科目ID未取得',
                            'error_detail': f'科目が見つかりません: {subject_name} (学部: {row["学部課程"]}, 年度: {row["年度"]})',
                            'processed_at': datetime.now().isoformat()
                        }
                        errors.append(error_info)
                        stats['error_items'] += 1
                        error_type = '科目ID未取得'
                        if error_type not in stats['specific_errors']:
                            stats['specific_errors'][error_type] = 0
                        stats['specific_errors'][error_type] += 1
                        continue
                    
                    # 各属性フィールドを処理
                    for field_name in attribute_fields:
                        value = row[field_name]
                        # NULL値、null値、空文字、空白文字のみの場合はスキップ
                        if value == "NULL" or value == "null" or not value or value.strip() == "":
                            continue
                        
                        # 可変長配列形式の値を分割
                        values_to_process = []
                        if value.startswith('[') and value.endswith(']'):
                            # [A,B,C]形式の場合、カンマで分割
                            array_content = value[1:-1]  # [と]を除去
                            if array_content.strip():  # 空の配列でない場合
                                values_to_process = [item.strip() for item in array_content.split(',') if item.strip()]
                            else:
                                continue  # 空の配列はスキップ
                        else:
                            # 通常の値の場合
                            values_to_process = [value]
                        
                        # 分割された各値を処理
                        for single_value in values_to_process:
                            # 空の値はスキップ
                            if not single_value or single_value.strip() == "":
                                continue
                                
                            attribute_id = get_attribute_id_from_db(session, field_name)
                            if attribute_id is None:
                                error_info = {
                                    'file_name': os.path.basename(csv_file),
                                    'row_number': row_idx,
                                    'subject_name': subject_name,
                                    'faculty_name': row['学部課程'],
                                    'year': row['年度'],
                                    'attribute_name': field_name,
                                    'attribute_value': single_value,
                                    'normalized_subject_name': normalized_subject_name,
                                    'error_type': '属性ID未取得',
                                    'error_detail': f'属性が見つかりません: {field_name}',
                                    'processed_at': datetime.now().isoformat()
                                }
                                errors.append(error_info)
                                stats['error_items'] += 1
                                error_type = '属性ID未取得'
                                if error_type not in stats['specific_errors']:
                                    stats['specific_errors'][error_type] = 0
                                stats['specific_errors'][error_type] += 1
                                continue
                            
                            attribute_value_info = {
                                'subject_id': subject_id,
                                'attribute_id': attribute_id,
                                'value': single_value,
                                'created_at': datetime.now().isoformat()
                            }
                            attribute_values.append(attribute_value_info)
                            stats['valid_items'] += 1
                        
                except Exception as e:
                    error_info = {
                        'file_name': os.path.basename(csv_file),
                        'row_number': row_idx,
                        'subject_name': row.get('科目名', ''),
                        'faculty_name': row.get('学部課程', ''),
                        'year': row.get('年度', ''),
                        'attribute_name': '',
                        'attribute_value': '',
                        'normalized_subject_name': '',
                        'error_type': 'データ処理エラー',
                        'error_detail': str(e),
                        'processed_at': datetime.now().isoformat()
                    }
                    errors.append(error_info)
                    stats['error_items'] += 1
                    error_type = 'データ処理エラー'
                    if error_type not in stats['specific_errors']:
                        stats['specific_errors'][error_type] = 0
                    stats['specific_errors'][error_type] += 1
                    tqdm.write(f"エラー: 行の処理でエラーが発生しました: {str(e)}")
                    continue
    finally:
        session.close()
    
    return attribute_values

def create_subject_attribute_value_json(attribute_values: List[Dict]) -> str:
    """科目属性値情報のJSONファイルを作成する"""
    output_dir = os.path.join("updates", "subject_attribute_value", "add")
    os.makedirs(output_dir, exist_ok=True)
    
    # 現在の日時を取得してファイル名を生成
    current_time = datetime.now()
    filename = f"subject_attribute_value_{current_time.strftime('%Y%m%d_%H%M')}.json"
    output_file = os.path.join(output_dir, filename)
    
    data = {
        "subject_attribute_values": [{
            "subject_id": value["subject_id"],
            "attribute_id": value["attribute_id"],
            "value": value["value"],
            "created_at": value["created_at"]
        } for value in sorted(attribute_values, key=lambda x: (
            x["subject_id"],
            x["attribute_id"]
        ))]
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return output_file

def main(db_config: Dict[str, str]):
    """メイン処理"""
    try:
        # 年度の取得
        year = get_year_from_user()
        
        # 統計情報の初期化
        stats = {
            'total_files': 0,
            'processed_files': 0,
            'total_items': 0,
            'valid_items': 0,
            'error_items': 0,
            'specific_errors': {}
        }
        
        # エラー情報の収集用リスト
        errors = []
        
        # 処理開始時のメッセージ
        tqdm.write(f"\n{'='*60}")
        tqdm.write(f"科目属性値パーサー - 対象年度: {year}")
        tqdm.write(f"{'='*60}")
        
        # CSVファイルの取得
        csv_files = get_csv_files(year)
        stats['total_files'] = len(csv_files)
        tqdm.write(f"処理対象ファイル数: {len(csv_files)}")
        
        # 科目属性値情報の抽出
        all_attribute_values = []
        for csv_file in tqdm(csv_files, desc="CSVファイル処理中", unit="file"):
            try:
                attribute_values = extract_subject_attribute_values(csv_file, db_config, stats, errors)
                all_attribute_values.extend(attribute_values)
                stats['processed_files'] += 1
                tqdm.write(f"ファイル {os.path.basename(csv_file)}: {len(attribute_values)}件の属性値を抽出")
            except Exception as e:
                tqdm.write(f"ファイル {os.path.basename(csv_file)} の処理でエラー: {str(e)}")
                continue
        
        # 重複を除去
        unique_attribute_values = []
        seen_values = set()
        for value in all_attribute_values:
            value_key = (value['subject_id'], value['attribute_id'], value['value'])
            if value_key not in seen_values:
                seen_values.add(value_key)
                unique_attribute_values.append(value)
        
        # エラー情報をCSVファイルに出力
        if errors:
            warning_file = create_warning_csv(year, errors)
            tqdm.write(f"⚠️  エラー詳細をCSVファイルに出力しました: {warning_file}")
        
        # 最終統計の表示
        tqdm.write("\n" + "="*60)
        tqdm.write("処理完了 - 統計情報")
        tqdm.write("="*60)
        tqdm.write(f"総ファイル数: {stats['total_files']}")
        tqdm.write(f"処理済みファイル数: {stats['processed_files']}")
        tqdm.write(f"総データ数: {stats['total_items']}")
        tqdm.write(f"正常データ数: {stats['valid_items']}")
        tqdm.write(f"エラーデータ数: {stats['error_items']}")
        
        # 特定エラーの詳細表示
        if stats['specific_errors']:
            tqdm.write("\nエラー詳細:")
            for error_type, count in stats['specific_errors'].items():
                tqdm.write(f"  {error_type}: {count}件")
        
        tqdm.write("="*60)
        
        # 結果サマリーの表示
        tqdm.write(f"\n{'='*60}")
        tqdm.write("📊 抽出結果サマリー")
        tqdm.write(f"{'='*60}")
        tqdm.write(f"✅ 正常データ: {len(unique_attribute_values)}件")
        tqdm.write(f"⚠️  エラーデータ: {stats['error_items']}件")
        tqdm.write(f"📈 合計: {stats['total_items']}件")
        
        # JSONファイルの作成
        output_file = create_subject_attribute_value_json(unique_attribute_values)
        tqdm.write(f"JSONファイルを作成しました: {output_file}")
        
    except Exception as e:
        tqdm.write(f"エラーが発生しました: {str(e)}")
        raise

if __name__ == "__main__":
    # .envファイルから設定を読み込む
    load_dotenv()
    
    # データベース設定を取得（デフォルト値を設定）
    db_config = {
        'user': os.getenv('POSTGRES_USER', 'postgres'),
        'password': os.getenv('POSTGRES_PASSWORD', 'postgres'),
        'host': os.getenv('POSTGRES_HOST', 'localhost'),
        'port': os.getenv('POSTGRES_PORT', '5432'),
        'db': os.getenv('POSTGRES_DB', 'syllabus_db')
    }
    
    main(db_config) 