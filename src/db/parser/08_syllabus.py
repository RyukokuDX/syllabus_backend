from bs4 import BeautifulSoup
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import re
import os
import json
import argparse
from pathlib import Path
import psycopg2
from tqdm import tqdm
import sys
import contextlib
import io
import logging
import traceback

# プロジェクトのルートディレクトリをPythonパスに追加
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.append(project_root)

from src.db.models import Syllabus, SubjectName, SyllabusData

# データベース接続情報
DB_HOST = os.environ.get('PGHOST', 'localhost')
DB_PORT = os.environ.get('PGPORT', '5432')
DB_NAME = os.environ.get('POSTGRES_DB', 'syllabus_db')
DB_USER = os.environ.get('POSTGRES_USER', 'postgres')
DB_PASSWORD = os.environ.get('POSTGRES_PASSWORD', 'postgres')

def get_id(conn, table, column, value):
    with conn.cursor() as cur:
        cur.execute(f"SELECT {table}_id FROM {table} WHERE {column} = %s", (value,))
        row = cur.fetchone()
        return row[0] if row else None

def parse_syllabus_html(html_content: str, filename: str, conn) -> Dict:
    """
    HTMLからシラバス情報を解析する
    
    Args:
        html_content (str): シラバスのHTMLコンテンツ
        filename (str): HTMLファイル名（シラバス管理番号を含む）
        conn: データベース接続オブジェクト
        
    Returns:
        Dict: 解析されたシラバス情報
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # シラバス情報テーブルを取得
    syllabus_info = soup.find('table', class_='syllabus-info')
    if not syllabus_info:
        raise ValueError("シラバス情報テーブルが見つかりません")
    
    # 基本情報を取得
    info_dict = {}
    for row in syllabus_info.find_all('tr'):
        th = row.find('th')
        td = row.find('td')
        if th and td:
            key = th.text.strip().split('／')[0]  # 日本語部分のみを取得
            value = td.text.strip()
            info_dict[key] = value
    
    # シラバス管理番号をファイル名から取得
    syllabus_code = os.path.splitext(filename)[0]
    
    # subject_name_idを取得
    subject_name = info_dict.get('科目名', '')
    subject_name_id = get_id(conn, 'subject_name', 'name', subject_name)
    if not subject_name_id:
        raise ValueError(f"科目名 '{subject_name}' に対応するIDが見つかりません")
    
    # 講義概要を取得
    summary_table = soup.find('table', recursive=True)
    summary = None
    goals = None
    methods = None
    outside_study = None
    remarks = None
    
    for table in soup.find_all('table', recursive=True):
        th = table.find('th')
        if th:
            text = th.text.strip()
            if '講義概要' in text:
                td = table.find('td')
                if td:
                    span = td.find('span')
                    if span:
                        summary = span.text.strip()
            elif '到達目標' in text:
                td = table.find('td')
                if td:
                    span = td.find('span')
                    if span:
                        goals = span.text.strip()
            elif '講義方法' in text:
                td = table.find('td')
                if td:
                    span = td.find('span')
                    if span:
                        methods = span.text.strip()
            elif '授業外学習' in text:
                td = table.find('td')
                if td:
                    span = td.find('span')
                    if span:
                        outside_study = span.text.strip()
            elif '履修上の注意' in text:
                td = table.find('td')
                if td:
                    span = td.find('span')
                    if span:
                        remarks = span.text.strip()
    
    # 備考を取得
    notes = soup.find('th', string=lambda x: x and '備考' in x)
    notes_text = notes.find_next('td').text.strip() if notes else None
    
    # 成績評価方法を取得
    grading = soup.find('th', string=lambda x: x and '成績評価の方法' in x)
    grading_text = grading.find_next('td').text.strip() if grading else None
    
    # 学年マスクを生成
    grade_mask = 0
    if '配当年次' in info_dict:
        grades = info_dict['配当年次']
        # 全角チルダ（～）で区切られた範囲を処理
        if '～' in grades:
            start, end = grades.split('～')
            start_year = int(start[0])  # "1年次" から "1" を取得
            end_year = int(end[0])      # "4年次" から "4" を取得
            for year in range(start_year, end_year + 1):
                grade_mask |= (1 << (year - 1))  # 2^(year-1) を設定
        else:
            # 個別の年次指定の場合
            for year in range(1, 5):  # 1年次から4年次まで
                if f"{year}年次" in grades:
                    grade_mask |= (1 << (year - 1))
    
    # termを全角スペースで区切って左側のみを取得
    term = info_dict.get('開講期　曜講時', '').split('　')[0]
    
    return {
        'syllabus_code': syllabus_code,
        'subject_name_id': subject_name_id,
        'subtitle': info_dict.get('サブタイトル', ''),
        'term': term,
        'grade_mask': grade_mask,
        'campus': info_dict.get('開講キャンパス', ''),
        'credits': int(info_dict.get('単位', 0)),
        'summary': summary,
        'goals': goals,
        'methods': methods,
        'outside_study': outside_study,
        'notes': notes_text,
        'remarks': remarks
    }

def save_json(entries: List[Dict[str, Any]], year: str) -> None:
    """
    シラバス情報をJSONファイルとして保存する
    
    Args:
        entries (List[Dict[str, Any]]): 保存するシラバス情報のリスト
        year (str): 年度
    """
    if not entries:
        print("  No entries to save")
        return
        
    filepath = f"updates/syllabus/add/syllabus_{year}.json"
    
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        json_data = {
            "syllabi": [{
                **entry,
                "created_at": datetime.now().isoformat(),
                "updated_at": None
            } for entry in entries]
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        print(f"  Saved {len(entries)} entries to {filepath}")
    except Exception as e:
        print(f"  Error saving {filepath}: {str(e)}")

def setup_logger(year: str) -> logging.Logger:
    """
    ロガーを設定する
    
    Args:
        year (str): 処理対象の年
        
    Returns:
        logging.Logger: 設定されたロガー
    """
    # ログディレクトリの作成
    log_dir = "log/db/parser"
    os.makedirs(log_dir, exist_ok=True)
    
    # 現在の日時を取得
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # ログファイル名の設定（年度と日時を含める）
    log_file = f"{log_dir}/06_syllabus_{year}_{current_time}.log"
    
    # ロガーの設定
    logger = logging.getLogger(f"syllabus_parser_{year}")
    logger.setLevel(logging.INFO)
    
    # 既存のハンドラを削除
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # ファイルハンドラの設定
    file_handler = logging.FileHandler(log_file, encoding='utf-8', mode='w')  # mode='w'で上書き
    file_handler.setLevel(logging.INFO)
    
    # フォーマッタの設定
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    
    # ハンドラの追加
    logger.addHandler(file_handler)
    
    return logger

def process_syllabus_data(year: str) -> None:
    """
    指定された年のシラバスデータを処理する
    
    Args:
        year (str): 処理対象の年
    """
    # ロガーの設定
    logger = setup_logger(year)
    logger.info(f"Starting syllabus processing for year {year}")
    
    # データベース接続
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        logger.info("Database connection established")
    except Exception as e:
        logger.error(f"Failed to connect to database: {str(e)}")
        logger.error(traceback.format_exc())
        return

    # HTMLファイルの処理
    html_dir = f"src/syllabus/{year}/raw_html"
    if not os.path.exists(html_dir):
        logger.error(f"HTML directory not found: {html_dir}")
        return

    entries = []
    processed_files = 0
    error_files = 0
    error_messages = []
    error_types = {}  # エラーの種類ごとのカウント

    try:
        html_files = [f for f in os.listdir(html_dir) if f.endswith('.html')]
        total = len(html_files)
        logger.info(f"Found {total} HTML files to process")
        
        # tqdmの出力を一時的に抑制
        with contextlib.redirect_stdout(io.StringIO()):
            for html_file in tqdm(html_files, total=total, desc="Processing HTML files"):
                filepath = os.path.join(html_dir, html_file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                        syllabus_data = parse_syllabus_html(html_content, html_file, conn)
                        entries.append(syllabus_data)
                        processed_files += 1
                        logger.debug(f"Successfully processed {html_file}")
                except Exception as e:
                    error_type = type(e).__name__
                    error_types[error_type] = error_types.get(error_type, 0) + 1
                    
                    error_msg = f"Error processing {filepath}: {str(e)}"
                    error_detail = traceback.format_exc()
                    logger.error(error_msg)
                    logger.error(error_detail)
                    error_messages.append(f"{error_msg}\n{error_detail}")
                    error_files += 1
                    continue

        if entries:
            save_json(entries, year)
            
            # エラー率の計算
            error_rate = (error_files / total) * 100 if total > 0 else 0
            
            # ログに詳細な統計情報を記録
            logger.info("=== Processing Statistics ===")
            logger.info(f"Total files: {total}")
            logger.info(f"Successfully processed: {processed_files}")
            logger.info(f"Files with errors: {error_files}")
            logger.info(f"Overall error rate: {error_rate:.1f}%")
            
            logger.info("\n=== Error Type Breakdown ===")
            for error_type, count in error_types.items():
                error_type_rate = (count / total) * 100 if total > 0 else 0
                logger.info(f"{error_type}: {count} occurrences ({error_type_rate:.1f}%)")
            
            # エラー詳細の記録
            if error_messages:
                logger.info("\n=== Error Details ===")
                for msg in error_messages:
                    logger.error(msg)
            
            # コンソール出力用のサマリー
            summary = f"""
Processing Summary:
Total files: {total}
Successfully processed: {processed_files}
Files with errors: {error_files}
Overall error rate: {error_rate:.1f}%

Error Type Breakdown:
"""
            for error_type, count in error_types.items():
                error_type_rate = (count / total) * 100 if total > 0 else 0
                summary += f"- {error_type}: {count} occurrences ({error_type_rate:.1f}%)\n"
            
            print(summary)
            
            if error_messages:
                print("\nError Details:")
                for msg in error_messages:
                    print(msg)
        else:
            logger.warning("No entries found in HTML files")
            print("No entries found in HTML files")
    except Exception as e:
        error_msg = f"Error processing HTML files: {str(e)}"
        error_detail = traceback.format_exc()
        logger.error(error_msg)
        logger.error(error_detail)
        print(error_msg)
    finally:
        conn.close()
        logger.info("Database connection closed")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate syllabus insert JSON from HTML files")
    parser.add_argument("-y", "--year", help="Year to process")
    args = parser.parse_args()
    
    year = args.year
    if not year:
        year = input("年度を入力してください（空の場合は今年）: ").strip()
        if not year:
            year = datetime.now().year
    
    process_syllabus_data(str(year)) 