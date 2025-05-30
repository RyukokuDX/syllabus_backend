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

def log_debug(message, year):
    """評価基準に関するログのみを出力"""
    if not any(keyword in message for keyword in ["評価基準", "成績評価"]):
        return
    log_dir = f"src/syllabus/{year}/data"
    os.makedirs(log_dir, exist_ok=True)
    with open(f"{log_dir}/debug_scores.log", "a", encoding='utf-8') as f:
        f.write(f"{message}\n")

def clear_debug_log(year):
    """ログファイルをクリア"""
    log_dir = f"src/syllabus/{year}/data"
    os.makedirs(log_dir, exist_ok=True)
    with open(f"{log_dir}/debug_scores.log", "w", encoding='utf-8') as f:
        f.write("")

def parse_book_td(td, role):
    block = ' '.join([t.strip() for t in td.strings if t.strip()])
    # タイトル
    title_match = re.search(r'『(.+?)』', block)
    title = title_match.group(1).strip() if title_match else ""
    # 出版社
    publisher_match = re.search(r'（(.+?)）', block)
    publisher = publisher_match.group(1).strip() if publisher_match else ""
    # 価格
    price_match = re.search(r'([0-9,]+)円', block)
    price = int(price_match.group(1).replace(',', '')) if price_match else 0
    return {
        "title": title,
        "author": "",
        "publisher": publisher,
        "price": price,
        "isbn": "",
        "role": role
    }

def extract_books_from_table(soup, label, role, year, log_path, syllabus_code, file_path):
    # ラベルを部分一致で探す
    th = None
    for t in soup.find_all('th'):
        if label in t.get_text():
            th = t
            break
    if not th:
        return []
    table = th.find_parent('table')
    if not table:
        return []
    books = []
    for tr in table.find_all('tr'):
        tds = tr.find_all('td')
        for td in tds:
            block = ' '.join([t.strip() for t in td.strings if t.strip()])
            book = parse_book_td(td, role)
            if book["title"] or book["publisher"] or book["price"]:
                books.append(book)
    return books

def extract_syllabus_info(html_content: str, file_path: str, soup=None) -> Dict:
    """HTMLからシラバス情報を抽出"""
    if soup is None:
        soup = BeautifulSoup(html_content, 'html.parser', from_encoding='utf-8')
    
    # シラバス管理番号をファイル名から取得
    syllabus_code = os.path.splitext(os.path.basename(file_path))[0]
    
    # 年度をファイルパスから抽出
    year = int(re.search(r'/\d{4}/', file_path).group(0).strip('/'))
    
    # 基本情報の抽出
    info = {
        "syllabus_code": syllabus_code,
        "syllabus_year": year,
        "subject_name": "",
        "faculty": "",
        "subtitle": "",
        "term": "",
        "campus": "",
        "credits": 0,
        "summary": "",
        "goals": "",
        "attainment": "",
        "methods": "",
        "outside_study": "",
        "notes": "",
        "remarks": "",
        "grades": [],
        "lecture_sessions": [],
        "instructors": [],
        "books": [],
        "grading_criteria": [],
        "study_system": []
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
    for form in soup.find_all('form'):
        log_debug("フォームを発見", year)
        for table in form.find_all('table'):
            log_debug("テーブルを発見", year)
            # テーブルのヘッダーを探す
            header = table.find('th')
            if not header:
                log_debug("ヘッダーなし", year)
                continue
                
            header_text = header.get_text(strip=True)
            log_debug(f"ヘッダーテキスト: {header_text}", year)
            
            # 内容を取得（spanタグ内のテキストを優先）
            content = table.find('td')
            if not content:
                log_debug("コンテンツなし", year)
                continue
                
            # spanタグ内のテキストを取得
            span = content.find('span')
            if span:
                content_text = span.get_text(strip=True)
            else:
                content_text = content.get_text(strip=True)
            
            log_debug(f"コンテンツテキスト: {content_text}", year)
            
            # セクションタイトルに基づいて情報を分類
            if any(keyword in header_text for keyword in ["目的・ねらい", "Goal(s)", "目的"]):
                info["goals"] = content_text
            elif any(keyword in header_text for keyword in ["講義概要", "Course outline", "概要"]):
                info["summary"] = content_text
            elif any(keyword in header_text for keyword in ["到達目標", "Attainment objectives", "到達"]):
                info["attainment"] = content_text
            elif any(keyword in header_text for keyword in ["講義方法", "Teaching methods", "方法"]):
                info["methods"] = content_text
            elif any(keyword in header_text for keyword in ["授業外学習", "Outside study", "学習"]):
                info["outside_study"] = content_text
            elif any(keyword in header_text for keyword in ["履修上の注意", "Notes", "注意"]):
                info["notes"] = content_text
            elif any(keyword in header_text for keyword in ["履修上の注意・担当者からの一言", "Advice to students", "担当者からの一言"]):
                info["remarks"] = content_text  # advicesからremarksに変更
            elif "種別" in header_text or "Kind" in header_text:
                log_debug(f"成績評価セクションを発見: {header_text}", year)
                
                # 評価基準テーブルを探す
                content = table.find('td')
                if content:
                    # テーブルを探す
                    grading_table = content.find('table')
                    if grading_table:
                        log_debug("評価基準テーブルを発見", year)
                        rows = grading_table.find_all('tr')
                        for row in rows:
                            cells = row.find_all(['th', 'td'])
                            if len(cells) >= 2:  # 2列以上あれば処理
                                kind_cell = cells[0]
                                ratio_cell = cells[1]
                                note_cell = cells[2] if len(cells) > 2 else None
                                
                                kind_text = kind_cell.get_text(strip=True)
                                ratio_text = ratio_cell.get_text(strip=True)
                                note_text = note_cell.get_text(strip=True) if note_cell else ""
                                
                                # 種別行はスキップ
                                if kind_text == "種別" or not kind_text:
                                    continue
                                    
                                # 種別名の統一
                                if "その他" in kind_text:
                                    kind_text = "その他"
                                elif "自由記載" in kind_text or "Notebook" in kind_text:
                                    kind_text = "自由記載"
                                    # 次のtdの内容を取得
                                    next_td = row.find('td')
                                    if next_td:
                                        note_text = next_td.get_text(strip=True)
                                        if note_text:
                                            info["grading_criteria"].append({
                                                "criteria_type": kind_text,
                                                "ratio": None,
                                                "note": note_text
                                            })
                                    continue
                                    
                                # 割合が空の場合はスキップ
                                if not ratio_text.strip():
                                    continue
                                    
                                ratio_match = re.search(r'(\d+)', ratio_text)
                                if ratio_match:
                                    ratio = int(ratio_match.group(1))
                                    # 重複チェック
                                    if not any(c["criteria_type"] == kind_text and c["ratio"] == ratio for c in info["grading_criteria"]):
                                        log_debug(f"評価基準を追加: {kind_text} ({ratio}%) - {note_text}", year)
                                        info["grading_criteria"].append({
                                            "criteria_type": kind_text,
                                            "ratio": ratio,
                                            "note": note_text
                                        })
                    else:
                        log_debug("評価基準テーブルが見つかりません", year)
            elif any(keyword in header_text for keyword in ["テキスト", "Textbooks"]):
                # 教科書情報の解析
                if content_text != "特になし":
                    book = parse_book_td(content, "教科書")
                    if book["title"]:
                        info["books"].append(book)
            elif any(keyword in header_text for keyword in ["参考文献", "Reference books"]):
                # 参考文献情報の解析
                if content_text != "特になし":
                    book = parse_book_td(content, "参考書")
                    if book["title"]:
                        info["books"].append(book)
            elif any(keyword in header_text for keyword in ["履修条件", "Prerequisites", "条件"]):
                # 履修条件から系統的履修情報を抽出
                log_debug("履修条件の解析開始", year)
                for row in table.find_all('tr'):
                    cells = row.find_all(['th', 'td'])
                    if len(cells) >= 2:
                        condition = cells[0].get_text(strip=True)
                        value = cells[1].get_text(strip=True)
                        log_debug(f"条件: {condition}, 値: {value}", year)
                        if condition and value:
                            # 履修条件の種類を判定
                            if any(keyword in condition for keyword in ["履修済みであること", "履修していること"]):
                                # 科目コードを抽出（例: "ABC123"）
                                code_match = re.search(r'[A-Z]{2,3}\d{3}', value)
                                if code_match:
                                    info["study_system"].append({
                                        "target_syllabus_code": code_match.group(0),
                                        "condition_type": "prerequisite"  # 前提条件
                                    })
                                    log_debug(f"前提条件を追加: {code_match.group(0)}", year)
                            elif any(keyword in condition for keyword in ["履修すること", "履修することを推奨"]):
                                # 科目コードを抽出
                                code_match = re.search(r'[A-Z]{2,3}\d{3}', value)
                                if code_match:
                                    info["study_system"].append({
                                        "target_syllabus_code": code_match.group(0),
                                        "condition_type": "recommended"  # 推奨科目
                                    })
                                    log_debug(f"推奨科目を追加: {code_match.group(0)}", year)
    
    return info

def save_to_json(data: List[Dict], year: int) -> str:
    """データをJSONファイルとして保存"""
    output_dir = f"src/syllabus/{year}/data"
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_file = os.path.join(output_dir, f"syllabus_{timestamp}.json")
    
    # 評価基準のログ出力
    for syllabus in data:
        if syllabus.get("grading_criteria"):
            log_debug(f"シラバス {syllabus['syllabus_code']} の評価基準:", year)
            for criterion in syllabus["grading_criteria"]:
                log_debug(f"  - {criterion['criteria_type']} ({criterion['ratio']}%): {criterion.get('note', '備考なし')}", year)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({"content": data}, f, ensure_ascii=False, indent=2)
    
    print(f"保存先: {output_file}")
    return output_file

def save_pretty_html_onefile(pretty_html: str, year: int):
    """1ファイル分の整形済みHTMLをpretty.htmlに上書き保存"""
    output_dir = f"src/syllabus/{year}/data"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "pretty.html")
    # <!-- -->だけの行を除外
    lines = pretty_html.splitlines()
    filtered = [line for line in lines if not (line.strip() == '<!-- -->')]
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(filtered))

def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(description='Web SyllabusのHTMLファイルをJSONに変換')
    parser.add_argument('--test', action='store_true', help='テストモード（最初の10件のみ処理）')
    parser.add_argument('--year', '-y', type=int, help='処理する年度（例: 2025）')
    args = parser.parse_args()
    
    if not args.test:
        response = input("テストモードで実行しますか？ (y/n) [y]: ").strip().lower()
        args.test = response != 'n'
    
    if args.year:
        year = args.year
    else:
        year = get_year_from_user()
    html_files = get_html_files(year, args.test)
    
    if not html_files:
        print("処理対象のHTMLファイルが見つかりません")
        return
    
    print(f"{len(html_files)}件のHTMLファイルを処理します...")
    print(f"出力先ディレクトリ: src/syllabus/{year}/data/")
    
    all_syllabus_info = []
    clear_debug_log(year)  # ログファイルをクリア
    for html_file in tqdm(html_files, desc="HTMLファイル処理中"):
        try:
            # 1. 元HTMLをprettifyしてpretty.htmlに上書き保存
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            soup = BeautifulSoup(html_content, 'html.parser')
            save_pretty_html_onefile(soup.prettify(), year)

            # 2. pretty.htmlを再度読み込み直してパース
            pretty_path = f"src/syllabus/{year}/data/pretty.html"
            with open(pretty_path, 'r', encoding='utf-8') as f:
                pretty_content = f.read()
            pretty_soup = BeautifulSoup(pretty_content, 'html.parser')

            # 3. pretty_soupを使って抽出・ログ出力
            syllabus_info = extract_syllabus_info(pretty_content, html_file, soup=pretty_soup)
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