from bs4 import BeautifulSoup
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from sqlalchemy.orm import Session
from src.db.models import Syllabus, SubjectName, SyllabusData
import re
import os
import json
import argparse
from pathlib import Path

def parse_syllabus_html(html_content: str) -> Dict:
    """
    HTMLからシラバス情報を解析する
    
    Args:
        html_content (str): シラバスのHTMLコンテンツ
        
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
            key = th.text.strip()
            value = td.text.strip()
            info_dict[key] = value
    
    # 講義概要を取得
    summary = soup.find('th', string=lambda x: x and '講義概要' in x)
    summary_text = summary.find_next('td').text.strip() if summary else None
    
    # 到達目標を取得
    goals = soup.find('th', string=lambda x: x and '到達目標' in x)
    goals_text = goals.find_next('td').text.strip() if goals else None
    
    # 講義方法を取得
    methods = soup.find('th', string=lambda x: x and '講義方法' in x)
    methods_text = methods.find_next('td').text.strip() if methods else None
    
    # 授業外学習を取得
    outside_study = soup.find('th', string=lambda x: x and '授業外学習' in x)
    outside_study_text = outside_study.find_next('td').text.strip() if outside_study else None
    
    # 備考を取得
    notes = soup.find('th', string=lambda x: x and '備考' in x)
    notes_text = notes.find_next('td').text.strip() if notes else None
    
    # 履修上の注意を取得
    remarks = soup.find('th', string=lambda x: x and '履修上の注意' in x)
    remarks_text = remarks.find_next('td').text.strip() if remarks else None
    
    # 成績評価方法を取得
    grading = soup.find('th', string=lambda x: x and '成績評価の方法' in x)
    grading_text = grading.find_next('td').text.strip() if grading else None
    
    # 学年マスクを生成
    grade_mask = 0
    if '配当年次' in info_dict:
        grades = info_dict['配当年次']
        if '1年次' in grades:
            grade_mask |= 1
        if '2年次' in grades:
            grade_mask |= 2
        if '3年次' in grades:
            grade_mask |= 4
        if '4年次' in grades:
            grade_mask |= 8
    
    return {
        'syllabus_code': info_dict.get('科目コード', ''),
        'subject_name': info_dict.get('科目名', ''),
        'subtitle': info_dict.get('サブタイトル', ''),
        'term': info_dict.get('開講期　曜講時', ''),
        'grade_mask': grade_mask,
        'campus': info_dict.get('開講キャンパス', ''),
        'credits': int(info_dict.get('単位', 0)),
        'summary': summary_text,
        'goals': goals_text,
        'methods': methods_text,
        'outside_study': outside_study_text,
        'notes': notes_text,
        'remarks': remarks_text
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

def process_syllabus_data(year: str) -> None:
    """
    指定された年のシラバスデータを処理する
    
    Args:
        year (str): 処理対象の年
    """
    # HTMLファイルの処理
    html_dir = f"src/syllabus/{year}/raw_html"
    if not os.path.exists(html_dir):
        print(f"HTML directory not found: {html_dir}")
        return

    entries = []
    processed_files = 0
    error_files = 0

    try:
        for html_file in os.listdir(html_dir):
            if html_file.endswith('.html'):
                filepath = os.path.join(html_dir, html_file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                        syllabus_data = parse_syllabus_html(html_content)
                        entries.append(syllabus_data)
                        processed_files += 1
                except Exception as e:
                    print(f"  Error processing {filepath}: {str(e)}")
                    error_files += 1
                    continue

        if entries:
            save_json(entries, year)
            print(f"\nProcessing Summary:")
            print(f"Total files processed: {processed_files}")
            print(f"Total entries saved: {len(entries)}")
            print(f"Files with errors: {error_files}")
        else:
            print("No entries found in HTML files")
    except Exception as e:
        print(f"Error processing HTML files: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process syllabus data for a specific year")
    parser.add_argument("-y", "--year", help="Year to process")
    args = parser.parse_args()
    
    year = args.year
    if not year:
        year = input("年度を入力してください（空の場合は今年）: ").strip()
        if not year:
            year = datetime.now().year
    
    process_syllabus_data(str(year)) 