import os
import json
import sqlite3
from typing import List, Dict, Set
from datetime import datetime
from bs4 import BeautifulSoup
from tqdm import tqdm
import re

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

def get_html_files(year: int) -> List[str]:
    """指定された年度のHTMLファイルのパスを取得する"""
    base_dir = os.path.join("src", "syllabus", str(year), "raw_html")
    if not os.path.exists(base_dir):
        raise FileNotFoundError(f"ディレクトリが見つかりません: {base_dir}")
    
    html_files = [f for f in os.listdir(base_dir) if f.endswith('.html')]
    if not html_files:
        raise FileNotFoundError(f"HTMLファイルが見つかりません: {base_dir}")
    
    return [os.path.join(base_dir, f) for f in html_files]

def create_pretty_html(html_content: str, output_path: str) -> None:
    """HTMLを整形して保存する"""
    soup = BeautifulSoup(html_content, 'html.parser')
    pretty_html = soup.prettify()
    
    # 出力ディレクトリの作成
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(pretty_html)

def find_th_with_text(soup: BeautifulSoup, text: str) -> BeautifulSoup:
    """指定されたテキストを含むthタグを探す"""
    for th in soup.find_all('th'):
        if text in th.text:
            return th
    return None

def get_next_td_content(element: BeautifulSoup) -> str:
    """指定された要素の次のtdタグの内容を取得する"""
    next_td = element.find_next('td')
    if not next_td:
        return ""
    return next_td.text.strip()

def expand_grade_range(grade_text: str) -> List[str]:
    """学年の範囲を展開する"""
    if not grade_text:
        return []
    
    # 全学年の場合
    if '全学年' in grade_text:
        return ['1年', '2年', '3年', '4年', '5年', '6年']
    
    # ～を含む範囲の場合
    if '～' in grade_text:
        parts = grade_text.split('～')
        if len(parts) != 2:
            return [grade_text]
        
        start = parts[0].strip()
        end = parts[1].strip()
        
        # 学年の数値を取得
        start_year = int(re.search(r'(\d+)年', start).group(1))
        end_year = int(re.search(r'(\d+)年', end).group(1))
        
        # 範囲内の学年を生成
        return [f"{year}年" for year in range(start_year, end_year + 1)]
    
    # カンマ区切りの場合
    if '、' in grade_text:
        return [grade.strip() for grade in grade_text.split('、')]
    
    # 単一の学年の場合
    return [grade_text]

def extract_grade_info(html_content: str, file_path: str) -> List[str]:
    """HTMLから学年情報を抽出する"""
    soup = BeautifulSoup(html_content, 'html.parser')
    grades = []
    
    # 履修可能学年を抽出
    grade_th = find_th_with_text(soup, '履修可能学年')
    if grade_th:
        grade_content = get_next_td_content(grade_th)
        if grade_content:
            grades.extend(expand_grade_range(grade_content))
    
    return grades

def get_latest_json(year: int) -> str:
    """指定された年度の最新のJSONファイルを取得する"""
    data_dir = os.path.join("src", "syllabus", str(year), "data")
    if not os.path.exists(data_dir):
        raise FileNotFoundError(f"ディレクトリが見つかりません: {data_dir}")
    
    json_files = [f for f in os.listdir(data_dir) if f.startswith('syllabus_') and f.endswith('.json')]
    if not json_files:
        raise FileNotFoundError(f"JSONファイルが見つかりません: {data_dir}")
    
    # ファイル名のタイムスタンプでソートして最新のものを取得
    latest_json = sorted(json_files)[-1]
    return os.path.join(data_dir, latest_json)

def extract_grade_info_from_json(json_data: Dict) -> List[Dict]:
    """JSONデータから学年情報を抽出する"""
    grades = []
    
    for syllabus in json_data.get("content", []):
        syllabus_code = syllabus.get("syllabus_code", "")
        grade_text = syllabus.get("grade", "")
        
        if grade_text:
            expanded_grades = expand_grade_range(grade_text)
            for grade in expanded_grades:
                grades.append({
                    'syllabus_code': syllabus_code,
                    'grade': grade
                })
    
    return grades

def create_grade_json(grades: List[Dict]) -> str:
    """学年情報のJSONファイルを作成する"""
    output_dir = os.path.join("updates", "subject_grade", "add")
    os.makedirs(output_dir, exist_ok=True)
    
    # 現在の日時を取得してファイル名を生成
    current_time = datetime.now()
    filename = f"subject_grade_{current_time.strftime('%Y%m%d_%H%M')}.json"
    output_file = os.path.join(output_dir, filename)
    
    data = {
        "subject_grades": [{
            "syllabus_code": grade["syllabus_code"],
            "grade": grade["grade"],
            "created_at": current_time.isoformat()
        } for grade in sorted(grades, key=lambda x: (x["syllabus_code"], x["grade"]))]
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return output_file

def get_pretty_html_path(raw_html_path: str) -> str:
    """raw_htmlのパスからpretty_htmlのパスを生成する"""
    return raw_html_path.replace('raw_html', 'pretty_html')

def process_html_file(html_file: str) -> List[str]:
    """HTMLファイルを処理して学年情報を抽出する"""
    # 元のHTMLファイルを読み込む
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # pretty_htmlのパスを生成
    pretty_html_path = get_pretty_html_path(html_file)
    
    # pretty_htmlが存在しない場合、または元のHTMLファイルより新しい場合は作成
    if not os.path.exists(pretty_html_path) or \
       os.path.getmtime(html_file) > os.path.getmtime(pretty_html_path):
        create_pretty_html(html_content, pretty_html_path)
        html_content = BeautifulSoup(html_content, 'html.parser').prettify()
    else:
        # 既存のpretty_htmlを読み込む
        with open(pretty_html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
    
    # 学年情報を抽出
    return extract_grade_info(html_content, html_file)

def get_subject_grades(year: int) -> List[Dict]:
    """データベースから学年情報を取得する"""
    db_path = os.path.join("src", "syllabus", str(year), "syllabus.db")
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # syllabus_basicテーブルから学年情報を取得
        cursor.execute("""
            SELECT syllabus_code, grade
            FROM syllabus_basic
            WHERE grade IS NOT NULL
        """)
        
        grades = []
        for row in cursor.fetchall():
            syllabus_code, grade_text = row
            if grade_text:
                expanded_grades = expand_grade_range(grade_text)
                for grade in expanded_grades:
                    grades.append({
                        'syllabus_code': syllabus_code,
                        'grade': grade
                    })
        
        return grades
        
    except sqlite3.Error as e:
        print(f"データベースエラー: {str(e)}")
        return []
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        return []
    finally:
        if conn:
            conn.close()

def main():
    """メイン処理"""
    try:
        # 年度の取得
        year = get_year_from_user()
        print(f"処理対象年度: {year}")
        
        # データベースから学年情報を取得
        grades = get_subject_grades(year)
        print(f"抽出された学年情報: {len(grades)}件")
        
        # JSONファイルの作成
        output_file = create_grade_json(grades)
        print(f"JSONファイルを作成しました: {output_file}")
        
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        raise

if __name__ == "__main__":
    main() 