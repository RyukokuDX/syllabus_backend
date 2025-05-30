import os
import json
import re
import argparse
from datetime import datetime
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
from tqdm import tqdm

def get_current_year() -> int:
    """現在の年を取得"""
    return datetime.now().year

def get_year_from_user() -> int:
    """ユーザーから年度を取得"""
    year = input(f"年度を入力してください（Enterで{get_current_year()}年）: ").strip()
    return int(year) if year else get_current_year()

def get_html_files(year: int, test_mode: bool = False) -> List[str]:
    """指定年度のHTMLファイル一覧を取得"""
    html_dir = f"src/syllabus/{year}/raw_html"
    if not os.path.exists(html_dir):
        print(f"エラー: {html_dir} ディレクトリが存在しません")
        return []
    
    files = [os.path.join(html_dir, f) for f in os.listdir(html_dir) if f.endswith('.html')]
    
    if test_mode:
        print("テストモード: 最初の10件のファイルのみ処理します")
        return files[:10]
    
    return files

def parse_instructor_name(name: str) -> Dict:
    """教員名を解析して姓と名に分割"""
    if not name:
        return {"last_name": "", "first_name": ""}
    
    # 空白で姓と名に分割
    name_parts = name.split()
    if len(name_parts) >= 2:
        return {
            "last_name": name_parts[0],
            "first_name": " ".join(name_parts[1:])
        }
    return {"last_name": name, "first_name": ""}

def extract_syllabus_info(html_content: str, file_path: str) -> Dict:
    """HTMLからシラバス情報を抽出"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # シラバス管理番号をファイル名から取得
    syllabus_code = os.path.splitext(os.path.basename(file_path))[0]
    
    # 基本情報の抽出
    info = {
        "syllabus_code": syllabus_code,
        "syllabus_year": int(re.search(r'/(\d{4})/', file_path).group(1)),
        "subject_name": "",  # 科目名を文字列で取得
        "faculty": "",  # 対象学部
        "subtitle": "",
        "term": "",
        "campus": "",
        "credits": 0,
        "summary": "",
        "goals": "",
        "methods": "",
        "outside_study": "",
        "notes": "",
        "remarks": "",
        "created_at": datetime.now().isoformat(),
        "updated_at": None,
        # 関連情報
        "grades": [],  # 履修可能学年
        "lecture_sessions": [],  # 講義時間
        "instructors": [],  # 教員情報
        "books": [],  # 教科書・参考書情報
        "grading_criteria": []  # 成績評価基準
    }
    
    # シラバス情報テーブルから基本情報を抽出
    syllabus_table = soup.find('table', class_='syllabus-info')
    if syllabus_table:
        for row in syllabus_table.find_all('tr'):
            cells = row.find_all(['th', 'td'])
            if len(cells) >= 2:
                key = cells[0].get_text(strip=True)
                value = cells[1].get_text(strip=True)
                
                if "科目名" in key:
                    info["subject_name"] = value
                elif "対象学部" in key:
                    info["faculty"] = value
                elif "サブタイトル" in key:
                    info["subtitle"] = value
                elif "配当年次" in key:
                    # 学年情報の解析（例: "2年次～4年次"）
                    grade_range = value.split('～')
                    if len(grade_range) >= 2:
                        start_grade = grade_range[0].strip()
                        end_grade = grade_range[1].strip()
                        # 開始学年から終了学年までの範囲を生成
                        start_num = int(re.search(r'(\d+)', start_grade).group(1))
                        end_num = int(re.search(r'(\d+)', end_grade).group(1))
                        for i in range(start_num, end_num + 1):
                            info["grades"].append(f"{i}年次")
                elif "開講キャンパス" in key:
                    info["campus"] = value
                elif "開講期" in key:
                    # 学期と曜日・時限の解析
                    term_parts = value.split()
                    if term_parts:
                        info["term"] = term_parts[0]  # 前期/後期
                        if len(term_parts) > 1:
                            # 曜日と時限の解析
                            time_info = term_parts[1]
                            day_match = re.search(r'([月火水木金土日])', time_info)
                            period_match = re.search(r'(\d+)', time_info)
                            if day_match and period_match:
                                info["lecture_sessions"].append({
                                    "day_of_week": day_match.group(1),
                                    "period": int(period_match.group(1))
                                })
                elif "単位" in key:
                    try:
                        info["credits"] = int(value)
                    except ValueError:
                        info["credits"] = 0
                elif "担当者Instructorカナ氏名" in key:
                    if value:
                        # カンマで分割して複数の教員を処理
                        for instructor in value.split(','):
                            instructor = instructor.strip()
                            if instructor:
                                name_info = parse_instructor_name(instructor)
                                info["instructors"].append({
                                    "last_name_kana": name_info["last_name"],
                                    "first_name_kana": name_info["first_name"],
                                    "last_name_kanji": "",
                                    "first_name_kanji": ""
                                })
                elif "担当者Instructor漢字氏名" in key:
                    if value:
                        # カンマで分割して複数の教員を処理
                        instructors = value.split(',')
                        for i, instructor in enumerate(instructors):
                            instructor = instructor.strip()
                            if instructor and i < len(info["instructors"]):
                                name_info = parse_instructor_name(instructor)
                                info["instructors"][i].update({
                                    "last_name_kanji": name_info["last_name"],
                                    "first_name_kanji": name_info["first_name"]
                                })
    
    # 講義概要セクションから情報を抽出
    for section in soup.find_all('div', class_='section'):
        title = section.find('h3')
        if not title:
            continue
            
        title_text = title.get_text(strip=True)
        content = section.find('div', class_='content')
        if not content:
            continue
            
        content_text = content.get_text(strip=True)
        
        if "講義概要" in title_text:
            info["summary"] = content_text
        elif "到達目標" in title_text:
            info["goals"] = content_text
        elif "講義方法" in title_text:
            info["methods"] = content_text
        elif "授業外学習" in title_text:
            info["outside_study"] = content_text
        elif "履修上の注意" in title_text:
            info["notes"] = content_text
        elif "その他備考" in title_text:
            info["remarks"] = content_text
        elif "成績評価" in title_text:
            # 成績評価基準の解析
            for row in content.find_all('tr'):
                cells = row.find_all(['th', 'td'])
                if len(cells) >= 2:
                    criteria = cells[0].get_text(strip=True)
                    ratio = cells[1].get_text(strip=True)
                    if criteria and ratio.strip():
                        try:
                            info["grading_criteria"].append({
                                "criteria_type": criteria,
                                "ratio": int(ratio)
                            })
                        except ValueError:
                            continue
        elif "テキスト" in title_text or "参考文献" in title_text:
            # 書籍情報の解析
            role = "教科書" if "テキスト" in title_text else "参考書"
            # テキスト/参考文献の次のtdを取得
            next_td = content.find('td')
            if next_td:
                text = next_td.get_text(strip=True)
                if text and text != "特になし":
                    # 著者名、タイトル、出版社、価格、ISBNを抽出
                    parts = text.split('『')
                    if len(parts) >= 2:
                        author = parts[0].strip()
                        title_parts = parts[1].split('』')
                        if len(title_parts) >= 2:
                            title = title_parts[0].strip()
                            remaining = title_parts[1].strip()
                            
                            # 出版社、価格、ISBNを抽出
                            publisher = ""
                            price = 0
                            isbn = ""
                            
                            if "（" in remaining:
                                publisher = remaining.split("（")[0].strip()
                                remaining = remaining.split("（")[1].strip("）")
                            
                            if "円" in remaining:
                                price_str = remaining.split("円")[0].strip()
                                try:
                                    price = int(price_str.replace(",", ""))
                                except ValueError:
                                    pass
                                remaining = remaining.split("円")[1].strip()
                            
                            if "ISBN:" in remaining:
                                isbn = remaining.split("ISBN:")[1].strip()
                            
                            info["books"].append({
                                "title": title,
                                "author": author,
                                "publisher": publisher,
                                "price": price,
                                "isbn": isbn,
                                "role": role
                            })
    
    return info

def save_to_json(data: List[Dict], year: int) -> str:
    """データをJSONファイルとして保存"""
    output_dir = f"src/syllabus/{year}/data"
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_file = os.path.join(output_dir, f"syllabus_{timestamp}.json")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({"content": data}, f, ensure_ascii=False, indent=2)
    
    print(f"保存先: {output_file}")
    return output_file

def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(description='Web SyllabusのHTMLファイルをJSONに変換')
    parser.add_argument('--test', action='store_true', help='テストモード（最初の10件のみ処理）')
    args = parser.parse_args()
    
    # オプションが指定されていない場合は確認（デフォルトはy）
    if not args.test:
        response = input("テストモードで実行しますか？ (y/n) [y]: ").strip().lower()
        args.test = response != 'n'  # 空文字列またはyの場合はテストモード
    
    year = get_year_from_user()
    html_files = get_html_files(year, args.test)
    
    if not html_files:
        print("処理対象のHTMLファイルが見つかりません")
        return
    
    print(f"{len(html_files)}件のHTMLファイルを処理します...")
    print(f"出力先ディレクトリ: src/syllabus/{year}/data/")
    
    all_syllabus_info = []
    for html_file in tqdm(html_files, desc="HTMLファイル処理中"):
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            syllabus_info = extract_syllabus_info(html_content, html_file)
            all_syllabus_info.append(syllabus_info)
            
        except Exception as e:
            print(f"エラー: {html_file} の処理中にエラーが発生しました: {str(e)}")
            continue
    
    if all_syllabus_info:
        output_file = save_to_json(all_syllabus_info, year)
        print(f"全{len(all_syllabus_info)}件のシラバス情報を{output_file}に保存しました")
    
    print("処理が完了しました")

if __name__ == "__main__":
    main() 