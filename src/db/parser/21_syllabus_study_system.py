# -*- coding: utf-8 -*-
# File Version: v2.5.0
# Project Version: v2.5.0
# Last Updated: 2025-07-03

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

from utils import normalize_subject_name

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

def get_subject_name_id_from_db(session, name: str) -> int:
    """科目名IDを取得する"""
    try:
        # 科目名を正規化
        normalized_name = normalize_subject_name(name)
        
        # 科目名IDを取得（重複を考慮）
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
        else:
            return None
    except Exception as e:
        session.rollback()
        return None

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

def get_syllabus_id_from_db(session, syllabus_master_id: int, subject_name_id: int) -> int:
    """シラバスIDを取得する"""
    try:
        # シラバスIDを取得
        query = text("""
            SELECT syllabus_id 
            FROM syllabus 
            WHERE syllabus_id = :syllabus_master_id
            AND subject_name_id = :subject_name_id
        """)
        
        result = session.execute(
            query,
            {"syllabus_master_id": syllabus_master_id, "subject_name_id": subject_name_id}
        ).first()
        
        return result[0] if result else None
    except Exception as e:
        session.rollback()
        return None

def create_syllabus_study_system_json(syllabus_study_systems: List[Dict]) -> str:
    """シラバス学習システム情報のJSONファイルを作成する"""
    output_dir = os.path.join("updates", "syllabus_study_system", "add")
    os.makedirs(output_dir, exist_ok=True)
    
    # 現在の日時を取得してファイル名を生成
    current_time = datetime.now()
    filename = f"syllabus_study_system_{current_time.strftime('%Y%m%d_%H%M')}.json"
    output_file = os.path.join(output_dir, filename)
    
    data = {
        "syllabus_study_systems": [{
            "source_syllabus_id": study_system["source_syllabus_id"],
            "target": study_system["target"],
            "created_at": current_time.isoformat()
        } for study_system in sorted(syllabus_study_systems, key=lambda x: (
            x["source_syllabus_id"],
            x["target"]
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
    filename = f"syllabus_study_system_{current_time.strftime('%Y%m%d_%H%M')}.csv"
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
            'エラータイプ',
            'エラー詳細',
            '正規化後科目名',
            '処理日時'
        ])
        
        # エラーデータ
        for error in errors:
            writer.writerow([
                error.get('file_name', ''),
                error.get('subject_name', ''),
                error.get('syllabus_code', ''),
                error.get('syllabus_year', ''),
                error.get('error_type', ''),
                error.get('error_detail', ''),
                error.get('normalized_subject_name', ''),
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
    latest_json = sorted(json_files)[-1]
    return os.path.join(data_dir, latest_json)

def get_all_json_files(year: int) -> List[str]:
    """指定された年度のすべてのJSONファイルを取得する"""
    data_dir = os.path.join("src", "syllabus", str(year), "json")
    if not os.path.exists(data_dir):
        raise FileNotFoundError(f"ディレクトリが見つかりません: {data_dir}")
    
    json_files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
    if not json_files:
        raise FileNotFoundError(f"JSONファイルが見つかりません: {data_dir}")
    
    # ファイル名でソート
    json_files.sort()
    return [os.path.join(data_dir, f) for f in json_files]

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

def process_syllabus_study_system_json(json_file: str, session) -> tuple[List[Dict], List[Dict]]:
    """個別のシラバスJSONファイルから学習システム情報を処理する"""
    errors = []
    study_systems = []
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        # 基本情報からデータを抽出
        basic_info = json_data.get("基本情報", {})
        
        # 必須情報の取得
        subject_name = basic_info.get("科目名", {}).get("内容")
        syllabus_code = json_data.get("科目コード")
        syllabus_year = int(basic_info.get("開講年度", {}).get("内容", "2025"))
        
        # エラー情報の基本データ
        error_base = {
            'file_name': os.path.basename(json_file),
            'subject_name': subject_name,
            'syllabus_code': syllabus_code,
            'syllabus_year': syllabus_year,
            'processed_at': datetime.now().isoformat()
        }
        
        if not subject_name or not syllabus_code:
            error_info = error_base.copy()
            error_info.update({
                'error_type': '必須情報不足',
                'error_detail': f'必須情報が不足 - 科目名: {subject_name}, 科目コード: {syllabus_code}',
                'normalized_subject_name': ''
            })
            errors.append(error_info)
            return [], errors
        
        # 科目名を正規化
        normalized_subject_name = normalize_subject_name(subject_name)
        error_base['normalized_subject_name'] = normalized_subject_name
        
        # データベースからIDを取得
        subject_name_id = get_subject_name_id_from_db(session, normalized_subject_name)
        if not subject_name_id:
            error_info = error_base.copy()
            error_info.update({
                'error_type': '科目名ID未取得',
                'error_detail': f'科目名が見つかりません - \'{normalized_subject_name}\' (元: \'{subject_name}\')'
            })
            errors.append(error_info)
            return [], errors
        
        syllabus_master_id = get_syllabus_master_id_from_db(session, syllabus_code, syllabus_year)
        if not syllabus_master_id:
            error_info = error_base.copy()
            error_info.update({
                'error_type': 'シラバスマスターID未取得',
                'error_detail': f'シラバスマスターが見つかりません - コード: {syllabus_code}, 年度: {syllabus_year}'
            })
            errors.append(error_info)
            return [], errors
        
        # シラバスIDを取得
        syllabus_id = get_syllabus_id_from_db(session, syllabus_master_id, subject_name_id)
        if not syllabus_id:
            error_info = error_base.copy()
            error_info.update({
                'error_type': 'シラバスID未取得',
                'error_detail': f'シラバスが見つかりません - マスターID: {syllabus_master_id}, 科目名ID: {subject_name_id}'
            })
            errors.append(error_info)
            return [], errors
        
        # 学習システム情報を取得
        # 詳細情報から系統的履修情報を抽出
        detail_info = json_data.get("詳細情報", {})
        
        # 系統的履修情報の抽出
        systematic_study_info = detail_info.get("系統的履修", {})
        if systematic_study_info and systematic_study_info.get("内容"):
            target = systematic_study_info.get("内容", "")
            if target and target.strip():
                study_system = {
                    "source_syllabus_id": syllabus_id,
                    "target": target.strip()
                }
                study_systems.append(study_system)
        
        return study_systems, errors
        
    except Exception as e:
        error_info = {
            'file_name': os.path.basename(json_file),
            'subject_name': '',
            'syllabus_code': '',
            'syllabus_year': '',
            'error_type': 'データ処理エラー',
            'error_detail': f'処理中にエラーが発生: {str(e)}',
            'normalized_subject_name': '',
            'processed_at': datetime.now().isoformat()
        }
        errors.append(error_info)
        return [], errors

def main():
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
            'specific_errors': {},
            'successful_files': 0,
            'error_files': 0,
            'total_study_systems': 0
        }
        
        # エラー情報の収集用リスト
        errors = []
        
        # すべてのJSONファイルを取得
        json_files = get_all_json_files(year)
        stats['total_files'] = len(json_files)
        
        # データベース接続
        session = get_db_connection()
        
        # シラバス学習システム情報を処理
        all_study_systems = []
        processed_count = 0
        error_count = 0
        skipped_count = 0
        
        # tqdmを使用してプログレスバーを表示
        for json_file in tqdm(json_files, desc="JSONファイルを処理中", unit="file"):
            try:
                # 個別のJSONファイルを処理
                study_systems, file_errors = process_syllabus_study_system_json(json_file, session)
                
                if study_systems:
                    all_study_systems.extend(study_systems)
                    processed_count += len(study_systems)
                    stats["successful_files"] += 1
                    stats["total_study_systems"] += len(study_systems)
                else:
                    skipped_count += 1
                    stats["error_files"] += 1
                
                # エラー情報を収集
                if file_errors:
                    errors.extend(file_errors)
                    for error in file_errors:
                        error_type = error.get('error_type', '不明なエラー')
                        if error_type not in stats['specific_errors']:
                            stats['specific_errors'][error_type] = 0
                        stats['specific_errors'][error_type] += 1
                    
            except Exception as e:
                error_count += 1
                stats["error_files"] += 1
                error_info = {
                    'file_name': os.path.basename(json_file),
                    'subject_name': '',
                    'syllabus_code': '',
                    'syllabus_year': '',
                    'error_type': 'ファイル処理エラー',
                    'error_detail': f'ファイル処理中にエラーが発生: {str(e)}',
                    'normalized_subject_name': '',
                    'processed_at': datetime.now().isoformat()
                }
                errors.append(error_info)
                continue
        
        # エラー情報をCSVファイルに出力
        if errors:
            warning_file = create_warning_csv(year, errors)
        
        # 処理結果をまとめて表示
        print(f"\n{'='*60}")
        print(f"シラバス学習システムパーサー - 対象年度: {year}")
        print(f"{'='*60}")
        print(f"処理対象ファイル数: {stats['total_files']}")
        print(f"処理開始: {stats['total_files']}個のJSONファイル")
        
        print(f"\n処理結果:")
        print(f"- 総ファイル数: {stats['total_files']}")
        print(f"- 成功ファイル数: {stats['successful_files']}")
        print(f"- エラーファイル数: {stats['error_files']}")
        print(f"- 総学習システム数: {stats['total_study_systems']}")
        print(f"- 成功: {processed_count}件")
        print(f"- エラー: {error_count}件")
        print(f"- スキップ: {skipped_count}件")
        
        # 特定エラーの詳細表示
        if stats['specific_errors']:
            print(f"\nエラー詳細:")
            for error_type, count in stats['specific_errors'].items():
                print(f"  {error_type}: {count}件")
        
        # エラー情報をまとめて表示
        if errors:
            print(f"\nエラー詳細 ({len(errors)}件):")
            print("=" * 80)
            for i, error in enumerate(errors, 1):
                print(f"{i:3d}. {error['file_name']}: {error['error_detail']}")
            print("=" * 80)
            print(f"⚠️  エラー詳細をCSVファイルに出力しました: {warning_file}")
        
        print("="*60)
        
        # 結果サマリーの表示
        print(f"\n{'='*60}")
        print("📊 抽出結果サマリー")
        print(f"{'='*60}")
        print(f"✅ 正常データ: {len(all_study_systems)}件")
        print(f"⚠️  エラーデータ: {len(errors)}件")
        print(f"📈 合計: {stats['total_files']}件")
        
        # JSONファイルの作成
        if all_study_systems:
            output_file = create_syllabus_study_system_json(all_study_systems)
            print(f"JSONファイルを作成しました: {output_file}")
        else:
            print("\n処理可能な学習システムデータが見つかりませんでした。")
        
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        print(f"エラーの種類: {type(e)}")
        raise
    finally:
        if 'session' in locals():
            session.close()

if __name__ == "__main__":
    main() 