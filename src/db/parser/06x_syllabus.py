from bs4 import BeautifulSoup
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import re
import os
import json
import argparse
from pathlib import Path

def parse_syllabus_html(html_content: str, filename: str) -> Dict:
    """
    HTMLからシラバス情報を解析する
    
    Args:
        html_content (str): シラバスのHTMLコンテンツ
        filename (str): HTMLファイル名（シラバス管理番号を含む）
        
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
        'subject_name': info_dict.get('科目名', ''),
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
        
    filepath = f"updates/syllabus/test/syllabus_{year}.json"
    
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
    html_dir = f"src/syllabus/{year}/test_html"
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
                        syllabus_data = parse_syllabus_html(html_content, html_file)
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
    process_syllabus_data("2025") 