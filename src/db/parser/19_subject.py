# -*- coding: utf-8 -*-
# File Version: v2.5.1
# Project Version: v2.5.1
# Last Updated: 2025-07-04

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

def clean_subject_name(name: str) -> str:
    """科目名をクリーニングする（[隔年開講]などを削除）"""
    if not name:
        return name
    
    # [隔年開講]を削除
    name = re.sub(r'\[隔年開講\]', '', name)
    
    # 前後の空白を削除
    name = name.strip()
    
    return name

def get_subject_name_id_from_db(session, name: str) -> int:
    """科目名IDを取得する"""
    try:
        # 科目名をクリーニング（[隔年開講]などを削除）
        cleaned_name = clean_subject_name(name)
        
        # 科目名を正規化
        normalized_name = normalize_subject_name(cleaned_name)
        
        # まず完全一致で検索
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
            
        # 完全一致で見つからない場合、部分一致で検索
        query = text("""
            SELECT subject_name_id 
            FROM subject_name 
            WHERE name LIKE :name
            ORDER BY subject_name_id
            LIMIT 1
        """)
        
        result = session.execute(
            query,
            {"name": f"%{normalized_name}%"}
        ).first()
        
        if result:
            tqdm.write(f"警告: 科目名の部分一致が見つかりました: {name} -> {normalized_name}")
            return result[0]
        
        # ローマ数字を除去して再検索
        name_without_roman = re.sub(r'[Ⅰ-Ⅹ]', '', normalized_name)
        if name_without_roman != normalized_name:
            query = text("""
                SELECT subject_name_id 
                FROM subject_name 
                WHERE name LIKE :name
                ORDER BY subject_name_id
                LIMIT 1
            """)
            
            result = session.execute(
                query,
                {"name": f"%{name_without_roman}%"}
            ).first()
            
            if result:
                tqdm.write(f"警告: ローマ数字を除去した科目名の部分一致が見つかりました: {name} -> {name_without_roman}")
                return result[0]
        
        tqdm.write(f"エラー: 科目名が見つかりません: {name} (正規化後: {normalized_name})")
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
        else:
            tqdm.write(f"エラー: 学部が見つかりません: {faculty_name}")
            return None
            
    except Exception as e:
        tqdm.write(f"エラー: 学部IDの取得中にエラーが発生しました: {str(e)}")
        session.rollback()
        return None

def get_class_id_from_db(session, class_name: str) -> int:
    """科目区分IDを取得する"""
    try:
        query = text("""
            SELECT class_id 
            FROM class 
            WHERE class_name = :name
            ORDER BY class_id
            LIMIT 1
        """)
        
        result = session.execute(
            query,
            {"name": class_name}
        ).first()
        
        if result:
            return result[0]
        else:
            tqdm.write(f"エラー: 科目区分が見つかりません: {class_name}")
            return None
            
    except Exception as e:
        tqdm.write(f"エラー: 科目区分IDの取得中にエラーが発生しました: {str(e)}")
        session.rollback()
        return None

def get_subclass_id_from_db(session, subclass_name: str) -> int:
    """科目小区分IDを取得する"""
    try:
        if not subclass_name:
            return None
            
        query = text("""
            SELECT subclass_id 
            FROM subclass 
            WHERE subclass_name = :name
            ORDER BY subclass_id
            LIMIT 1
        """)
        
        result = session.execute(
            query,
            {"name": subclass_name}
        ).first()
        
        if result:
            return result[0]
        else:
            tqdm.write(f"エラー: 科目小区分が見つかりません: {subclass_name}")
            return None
            
    except Exception as e:
        tqdm.write(f"エラー: 科目小区分IDの取得中にエラーが発生しました: {str(e)}")
        session.rollback()
        return None

def create_warning_csv(year: int, errors: List[Dict]) -> str:
    """エラー内容を詳細にCSVファイルに記載する"""
    # 警告ディレクトリを作成
    warning_dir = os.path.join("warning", str(year))
    os.makedirs(warning_dir, exist_ok=True)
    
    # 現在の日時を取得してファイル名を生成
    current_time = datetime.now()
    filename = f"subject_{current_time.strftime('%Y%m%d_%H%M')}.csv"
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
            '科目区分',
            '科目小区分',
            '必須度',
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
                error.get('class_name', ''),
                error.get('subclass_name', ''),
                error.get('requirement_type', ''),
                error.get('error_type', ''),
                error.get('error_detail', ''),
                error.get('normalized_subject_name', ''),
                error.get('processed_at', '')
            ])
    
    return output_file

def extract_subject_info(csv_file: str, db_config: Dict[str, str], stats: Dict, errors: List[Dict]) -> List[Dict]:
    """CSVから科目基本情報を抽出する"""
    subjects = []
    session = get_db_connection(db_config)
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            rows = list(reader)
            stats['total_items'] += len(rows)
            
            for row_idx, row in enumerate(rows, start=2):  # ヘッダー行を除いて2から開始
                try:
                    # 科目名をクリーニングして正規化
                    subject_name = clean_subject_name(row['科目名'])
                    normalized_subject_name = normalize_subject_name(subject_name)
                    
                    # 各IDを取得
                    subject_name_id = get_subject_name_id_from_db(session, subject_name)
                    faculty_id = get_faculty_id_from_db(session, row['学部課程'])
                    class_id = get_class_id_from_db(session, row['科目区分'])
                    subclass_id = get_subclass_id_from_db(session, row['科目小区分']) if row['科目小区分'] else None
                    
                    # エラーチェックとエラー情報の収集
                    error_info = {
                        'file_name': os.path.basename(csv_file),
                        'row_number': row_idx,
                        'subject_name': row['科目名'],
                        'faculty_name': row['学部課程'],
                        'year': row['年度'],
                        'class_name': row['科目区分'],
                        'subclass_name': row['科目小区分'],
                        'requirement_type': row['必須度'],
                        'normalized_subject_name': normalized_subject_name,
                        'processed_at': datetime.now().isoformat()
                    }
                    
                    if subject_name_id is None:
                        error_info['error_type'] = '科目名ID未取得'
                        error_info['error_detail'] = f'科目名が見つかりません: {subject_name} (正規化後: {normalized_subject_name})'
                        errors.append(error_info)
                        stats['error_items'] += 1
                        error_type = '科目名ID未取得'
                        if error_type not in stats['specific_errors']:
                            stats['specific_errors'][error_type] = 0
                        stats['specific_errors'][error_type] += 1
                        continue
                        
                    if faculty_id is None:
                        error_info['error_type'] = '学部ID未取得'
                        error_info['error_detail'] = f'学部が見つかりません: {row["学部課程"]}'
                        errors.append(error_info)
                        stats['error_items'] += 1
                        error_type = '学部ID未取得'
                        if error_type not in stats['specific_errors']:
                            stats['specific_errors'][error_type] = 0
                        stats['specific_errors'][error_type] += 1
                        continue
                        
                    if class_id is None:
                        error_info['error_type'] = '科目区分ID未取得'
                        error_info['error_detail'] = f'科目区分が見つかりません: {row["科目区分"]}'
                        errors.append(error_info)
                        stats['error_items'] += 1
                        error_type = '科目区分ID未取得'
                        if error_type not in stats['specific_errors']:
                            stats['specific_errors'][error_type] = 0
                        stats['specific_errors'][error_type] += 1
                        continue
                        
                    subject_info = {
                        'subject_name_id': subject_name_id,
                        'faculty_id': faculty_id,
                        'curriculum_year': int(row['年度']),
                        'class_id': class_id,
                        'subclass_id': subclass_id,
                        'requirement_type': row['必須度'] if row['必須度'] else None,
                        'created_at': datetime.now().isoformat()
                    }
                    subjects.append(subject_info)
                    stats['valid_items'] += 1
                    
                except Exception as e:
                    error_info = {
                        'file_name': os.path.basename(csv_file),
                        'row_number': row_idx,
                        'subject_name': row.get('科目名', ''),
                        'faculty_name': row.get('学部課程', ''),
                        'year': row.get('年度', ''),
                        'class_name': row.get('科目区分', ''),
                        'subclass_name': row.get('科目小区分', ''),
                        'requirement_type': row.get('必須度', ''),
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
    
    return subjects

def create_subject_json(subjects: List[Dict]) -> str:
    """科目基本情報のJSONファイルを作成する"""
    output_dir = os.path.join("updates", "subject", "add")
    os.makedirs(output_dir, exist_ok=True)
    
    # 現在の日時を取得してファイル名を生成
    current_time = datetime.now()
    filename = f"subject_{current_time.strftime('%Y%m%d_%H%M')}.json"
    output_file = os.path.join(output_dir, filename)
    
    data = {
        "subjects": [{
            "subject_name_id": subject["subject_name_id"],
            "faculty_id": subject["faculty_id"],
            "curriculum_year": subject["curriculum_year"],
            "class_id": subject["class_id"],
            "subclass_id": subject["subclass_id"],
            "requirement_type": subject["requirement_type"],
            "created_at": subject["created_at"]
        } for subject in sorted(subjects, key=lambda x: (
            x["subject_name_id"],
            x["faculty_id"],
            x["curriculum_year"],
            x["class_id"],
            x["subclass_id"] if x["subclass_id"] is not None else 0
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
        tqdm.write(f"科目パーサー - 対象年度: {year}")
        tqdm.write(f"{'='*60}")
        
        # CSVファイルの取得
        csv_files = get_csv_files(year)
        stats['total_files'] = len(csv_files)
        tqdm.write(f"処理対象ファイル数: {len(csv_files)}")
        
        # 科目基本情報の抽出
        all_subjects = []
        for csv_file in tqdm(csv_files, desc="CSVファイル処理中", unit="file"):
            try:
                subjects = extract_subject_info(csv_file, db_config, stats, errors)
                all_subjects.extend(subjects)
                stats['processed_files'] += 1
                tqdm.write(f"ファイル {os.path.basename(csv_file)}: {len(subjects)}件の科目を抽出")
            except Exception as e:
                tqdm.write(f"ファイル {os.path.basename(csv_file)} の処理でエラー: {str(e)}")
                continue
        
        # 重複を除去（subject_name_id, faculty_id, curriculum_year, class_id, subclass_idの組み合わせで一意）
        unique_subjects = []
        seen_combinations = set()
        for subject in all_subjects:
            combination = (
                subject['subject_name_id'],
                subject['faculty_id'],
                subject['curriculum_year'],
                subject['class_id'],
                subject['subclass_id']
            )
            if combination not in seen_combinations:
                seen_combinations.add(combination)
                unique_subjects.append(subject)
        
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
        tqdm.write(f"✅ 正常データ: {len(unique_subjects)}件")
        tqdm.write(f"⚠️  エラーデータ: {stats['error_items']}件")
        tqdm.write(f"📈 合計: {stats['total_items']}件")
        
        # JSONファイルの作成
        output_file = create_subject_json(unique_subjects)
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