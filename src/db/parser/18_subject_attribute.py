# -*- coding: utf-8 -*-
# File Version: v2.0.0
# Project Version: v2.0.0
# Last Updated: 2025-06-30
# curosrはversionをいじるな

import os
import json
import csv
from typing import List, Dict, Set
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm
from dotenv import load_dotenv

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
    
    if subdirs:
        print(f"見つかったcsvサブディレクトリ: {', '.join(subdirs)}")
        while True:
            subdir_input = input("処理するcsvサブディレクトリを指定してください（空の場合は全て処理）: ").strip()
            if not subdir_input:
                # 全てのサブディレクトリを処理
                break
            elif subdir_input in subdirs:
                # 指定されたサブディレクトリのみ処理
                subdirs = [subdir_input]
                break
            else:
                print(f"無効なサブディレクトリです。有効な選択肢: {', '.join(subdirs)}")
    
    csv_files = []
    
    # メインディレクトリ（csv）のCSVファイルを取得
    for file in os.listdir(base_dir):
        if file.endswith('.csv'):
            csv_files.append(os.path.join(base_dir, file))
    
    # 指定されたサブディレクトリのCSVファイルを取得
    for subdir in subdirs:
        subdir_path = os.path.join(base_dir, subdir)
        if os.path.isdir(subdir_path):
            for file in os.listdir(subdir_path):
                if file.endswith('.csv'):
                    csv_files.append(os.path.join(subdir_path, file))
    
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

def extract_subject_attributes(csv_file: str) -> List[Dict]:
    """CSVから科目属性情報を抽出する（ヘッダーから指定列以外を取得）"""
    attributes = []
    excluded_columns = {'科目名', '学部課程', '年度', '科目区分', '科目小区分', '必須度'}
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')  # タブ区切り
        rows = list(reader)
        
        if not rows:
            return attributes
        
        # ヘッダー行を取得
        header = rows[0]
        
        # 除外列以外の列インデックスを取得
        attribute_columns = []
        for i, col_name in enumerate(header):
            if col_name.strip() not in excluded_columns:
                attribute_columns.append((i, col_name.strip()))
        
        # データ行から属性値を抽出
        for row in rows[1:]:  # ヘッダー行をスキップ
            if not row or len(row) < len(header):
                continue
            
            for col_idx, col_name in attribute_columns:
                if col_idx < len(row) and row[col_idx].strip():
                    attribute_value = row[col_idx].strip()
                    
                    # 空でない値のみを属性として追加
                    if attribute_value and attribute_value.lower() not in ['null', 'none', '']:
                        attribute_info = {
                            'attribute_name': col_name,
                            'description': None,  # CSVには説明がないためNone
                            'created_at': datetime.now().isoformat()
                        }
                        attributes.append(attribute_info)
    
    return attributes

def create_subject_attribute_json(attributes: List[Dict]) -> str:
    """科目属性情報のJSONファイルを作成する"""
    output_dir = os.path.join("updates", "subject_attribute", "add")
    os.makedirs(output_dir, exist_ok=True)
    
    # 現在の日時を取得してファイル名を生成
    current_time = datetime.now()
    filename = f"subject_attribute_{current_time.strftime('%Y%m%d_%H%M')}.json"
    output_file = os.path.join(output_dir, filename)
    
    data = {
        "subject_attributes": [{
            "attribute_name": attribute["attribute_name"],
            "description": attribute["description"],
            "created_at": attribute["created_at"]
        } for attribute in sorted(attributes, key=lambda x: x["attribute_name"])]
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return output_file

def main(db_config: Dict[str, str]):
    """メイン処理"""
    try:
        # 年度の取得
        year = get_year_from_user()
        print(f"処理対象年度: {year}")
        
        # CSVファイルの取得
        csv_files = get_csv_files(year)
        print(f"処理対象ファイル数: {len(csv_files)}")
        
        # 科目属性情報の抽出
        all_attributes = []
        for csv_file in tqdm(csv_files, desc="CSVファイル処理中"):
            try:
                attributes = extract_subject_attributes(csv_file)
                all_attributes.extend(attributes)
                tqdm.write(f"ファイル {os.path.basename(csv_file)}: {len(attributes)}件の属性を抽出")
            except Exception as e:
                tqdm.write(f"ファイル {os.path.basename(csv_file)} の処理でエラー: {str(e)}")
                continue
        
        # 重複を除去
        unique_attributes = []
        seen_names = set()
        for attr in all_attributes:
            if attr['attribute_name'] not in seen_names:
                seen_names.add(attr['attribute_name'])
                unique_attributes.append(attr)
        
        print(f"抽出された科目属性情報: {len(unique_attributes)}件")
        
        # JSONファイルの作成
        output_file = create_subject_attribute_json(unique_attributes)
        print(f"JSONファイルを作成しました: {output_file}")
        
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
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