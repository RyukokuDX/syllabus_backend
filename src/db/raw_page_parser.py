import argparse
import os
import json
from bs4 import BeautifulSoup
from glob import glob
from datetime import datetime
import re

def parse_html_file(filepath, table_name):
    print(f"Processing: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    # 整形されたHTMLを初回のみ保存（多重保存を防ぐ）
    pretty_path = filepath.replace('.pretty.html', '') + '.pretty.html'
    if not os.path.exists(pretty_path):
        with open(pretty_path, 'w', encoding='utf-8') as f:
            f.write(soup.prettify())

    if table_name == 'subject':
        return parse_subject_table(soup)
    elif table_name == 'syllabus':
        return parse_syllabus_detail(soup)
    elif table_name == 'syllabus_time':
        return parse_syllabus_time(soup)
    else:
        print(f"  Unknown table name: {table_name}")
        return []

def parse_subject_table(soup):
    # 明示的にテーブルを検索する（複数候補の中から属性と科目名を含むものを特定）
    tables = soup.find_all('table', class_='dataT')
    table = None
    for t in tables:
        headers = t.find_all('th')
        if any('属性' in th.get_text(strip=True) for th in headers) and any('科目名' in th.get_text(strip=True) for th in headers):
            table = t
            break

    if not table:
        print("  No matching table found.")
        return []

    data = []
    rows = table.find_all('tr')[1:]  # Skip header row
    print(f"  Found {len(rows)} data rows.")
    for i, row in enumerate(rows):
        cols = row.find_all('td')
        if len(cols) < 4:
            print(f"    Row {i} skipped (not enough columns).")
            continue

        # 属性の処理
        attr_text = cols[2].get_text(strip=True)
        note = ''
        class_name = attr_text
        subclass_name = ''

        if '：' in attr_text:
            note, rest = attr_text.split('：', 1)
            class_name = rest

        if '・' in class_name:
            class_name, subclass_name = class_name.split('・', 1)

        # 科目名の処理
        name_part = cols[3].get_text(strip=True).split('\n')[0].strip()
        name_part = name_part.split('@')[0].strip()
        links = cols[3].find_all('a', href=True)
        subject_code = ''
        for link in links:
            href = link['href']
            if 'do?i=' in href:
                subject_code = href.split('do?i=')[1].split('&')[0]
                break

        if subject_code:
            current_time = datetime.now().isoformat()
            entry = {
                "subject_code": subject_code,
                "name": name_part,
                "class_name": class_name,
                "subclass_name": subclass_name,
                "class_note": note,
                "created_at": current_time,
                "updated_at": None
            }
            print(f"    Parsed entry: {entry}")
            data.append(entry)
        else:
            print(f"    Row {i} skipped (no subject_code).")

    return data

def parse_syllabus_detail(soup):
    try:
        # シラバス管理番号を取得
        syllabus_id = None
        syllabus_id_table = soup.find('table', id='s_kanri_bango')
        if syllabus_id_table:
            syllabus_id_td = syllabus_id_table.find('td', class_='data-n0')
            if syllabus_id_td:
                syllabus_id = syllabus_id_td.get_text(strip=True)

        if not syllabus_id:
            print("  No syllabus ID found.")
            return []

        # 科目コードを取得（シラバス管理番号を使用）
        subject_code = syllabus_id  # 例：G250110001

        # 開講年度を取得
        try:
            if syllabus_id.startswith('G'):
                year = int(syllabus_id[1:5])  # G250110001 -> 2025
            else:
                # Yで始まる場合は開講年度のtdから取得
                year_td = soup.find('td', class_='data-n0')
                if year_td:
                    year = int(year_td.get_text(strip=True))
                else:
                    print(f"  Could not find year for syllabus_id '{syllabus_id}'")
                    return []
        except (ValueError, IndexError) as e:
            print(f"  Error parsing year from syllabus_id '{syllabus_id}': {str(e)}")
            return []

        # サブタイトルを取得
        subtitle = ''
        subtitle_th = soup.find('th', string=lambda x: x and 'サブタイトル' in x)
        if subtitle_th:
            subtitle_td = subtitle_th.find_next('td')
            if subtitle_td:
                subtitle = subtitle_td.get_text(strip=True)

        # 開講期と講義コードを取得
        term = ''
        lecture_code = ''
        term_elem = soup.find('th', string=lambda x: x and '開講期' in x)
        if term_elem:
            term_td = term_elem.find_next('td')
            if term_td:
                term_text = term_td.get_text(strip=True)
                if '前期' in term_text:
                    term = '前期'
                elif '後期' in term_text:
                    term = '後期'
                elif '通年' in term_text:
                    term = '通年'
                
                # 講義コードを取得（例：火１(G111)のG111部分）
                lecture_code_match = re.search(r'\((G\d+)\)', term_text)
                if lecture_code_match:
                    lecture_code = lecture_code_match.group(1)

        # 配当年次を取得
        grade_b1 = False
        grade_b2 = False
        grade_b3 = False
        grade_b4 = False
        grade_m1 = False
        grade_m2 = False
        grade_d1 = False
        grade_d2 = False
        grade_d3 = False

        grade_elem = soup.find('th', string=lambda x: x and '配当年次' in x)
        if grade_elem:
            grade_td = grade_elem.find_next('td')
            if grade_td:
                grade_text = grade_td.get_text(strip=True)
                print(f"  Found grade text: {grade_text}")
                
                # 範囲指定の処理（例：1～2年次）
                if '～' in grade_text:
                    try:
                        start, end = grade_text.split('～')
                        start_year = int(start[0]) if start[0].isdigit() else 0
                        end_year = int(end[0]) if end[0].isdigit() else 0
                        
                        for year in range(start_year, end_year + 1):
                            if year == 1:
                                grade_b1 = True
                            elif year == 2:
                                grade_b2 = True
                            elif year == 3:
                                grade_b3 = True
                            elif year == 4:
                                grade_b4 = True
                    except Exception as e:
                        print(f"  Error parsing grade range '{grade_text}': {str(e)}")
                else:
                    # 個別指定の処理
                    if '1年次' in grade_text:
                        grade_b1 = True
                    if '2年次' in grade_text:
                        grade_b2 = True
                    if '3年次' in grade_text:
                        grade_b3 = True
                    if '4年次' in grade_text:
                        grade_b4 = True
                    if 'M1' in grade_text:
                        grade_m1 = True
                    if 'M2' in grade_text:
                        grade_m2 = True
                    if 'D1' in grade_text:
                        grade_d1 = True
                    if 'D2' in grade_text:
                        grade_d2 = True
                    if 'D3' in grade_text:
                        grade_d3 = True

        # キャンパスを取得
        campus = ''
        campus_elem = soup.find('th', string=lambda x: x and '開講キャンパス' in x)
        if campus_elem:
            campus_td = campus_elem.find_next('td')
            if campus_td:
                campus = campus_td.get_text(strip=True)

        # 単位数を取得
        credits = 0
        credits_elem = soup.find('th', string=lambda x: x and '単位' in x)
        if credits_elem:
            credits_td = credits_elem.find_next('td')
            if credits_td:
                try:
                    credits = int(credits_td.get_text(strip=True))
                except ValueError as e:
                    print(f"  Error parsing credits: {str(e)}")

        # 講義概要を取得
        summary = ''
        outline_elem = soup.find('th', string=lambda x: x and '講義概要' in x)
        if outline_elem:
            outline_td = outline_elem.find_next('td')
            if outline_td:
                summary = outline_td.get_text(strip=True)

        # 到達目標を取得
        goals = ''
        objectives_elem = soup.find('th', string=lambda x: x and '到達目標' in x)
        if objectives_elem:
            objectives_td = objectives_elem.find_next('td')
            if objectives_td:
                goals = objectives_td.get_text(strip=True)

        # 講義方法を取得
        methods = ''
        method_elem = soup.find('th', string=lambda x: x and '講義方法' in x)
        if method_elem:
            method_td = method_elem.find_next('td')
            if method_td:
                methods = method_td.get_text(strip=True)

        # 授業外学習を取得
        outside_study = ''
        outside_elem = soup.find('th', string=lambda x: x and '授業外学習' in x)
        if outside_elem:
            outside_td = outside_elem.find_next('td')
            if outside_td:
                outside_study = outside_td.get_text(strip=True)

        # 備考を取得
        notes = ''
        notes_elem = soup.find('th', string=lambda x: x and '備考' in x)
        if notes_elem:
            notes_td = notes_elem.find_next('td')
            if notes_td:
                notes = notes_td.get_text(strip=True)

        # 担当者からの一言を取得
        remarks = ''
        remarks_elem = soup.find('th', string=lambda x: x and '担当者からの一言' in x)
        if remarks_elem:
            remarks_td = remarks_elem.find_next('td')
            if remarks_td:
                remarks = remarks_td.get_text(strip=True)

        current_time = datetime.now().isoformat()
        entry = {
            "subject_code": subject_code,
            "year": year,
            "subtitle": subtitle,
            "term": term,
            "grade_b1": grade_b1,
            "grade_b2": grade_b2,
            "grade_b3": grade_b3,
            "grade_b4": grade_b4,
            "grade_m1": grade_m1,
            "grade_m2": grade_m2,
            "grade_d1": grade_d1,
            "grade_d2": grade_d2,
            "grade_d3": grade_d3,
            "campus": campus,
            "credits": credits,
            "lecture_code": lecture_code,
            "summary": summary,
            "goals": goals,
            "methods": methods,
            "outside_study": outside_study,
            "notes": notes,
            "remarks": remarks,
            "created_at": current_time,
            "updated_at": None
        }
        print(f"    Parsed syllabus detail: {entry}")
        return [entry]
    except Exception as e:
        print(f"  Error in parse_syllabus_detail: {str(e)}")
        import traceback
        print(f"  Traceback: {traceback.format_exc()}")
        return []

def parse_syllabus_time(soup):
    try:
        # シラバス管理番号を取得
        subject_code = None
        syllabus_id_table = soup.find('table', id='s_kanri_bango')
        if syllabus_id_table:
            syllabus_id_td = syllabus_id_table.find('td', class_='data-n0')
            if syllabus_id_td:
                subject_code = syllabus_id_td.get_text(strip=True)

        if not subject_code:
            print("  No syllabus ID found.")
            return []

        # 開講期と時間割情報を取得
        time_slots = []
        term_elem = soup.find('th', string=lambda x: x and '開講期' in x)
        if term_elem:
            term_td = term_elem.find_next('td')
            if term_td:
                term_text = term_td.get_text(strip=True)
                
                # 時間割情報を抽出（例：火３(Y119)・火４（ペア）など）
                # 曜日と時限のパターンを抽出
                time_pattern = r'([月火水木金土日])([１-５])'
                time_matches = list(re.finditer(time_pattern, term_text))
                
                # 時間割情報を処理
                i = 0
                while i < len(time_matches):
                    current_match = time_matches[i]
                    day_char = current_match.group(1)
                    period_char = current_match.group(2)
                    
                    # 曜日と時限を数値に変換
                    day_map = {'月': 1, '火': 2, '水': 3, '木': 4, '金': 5, '土': 6, '日': 7}
                    period_map = {'１': 1, '２': 2, '３': 3, '４': 4, '５': 5}
                    
                    day = day_map[day_char]
                    period = period_map[period_char]
                    
                    # 現在の時限の前後のテキストを取得
                    current_pos = current_match.start()
                    next_pos = current_match.end()
                    after_text = term_text[next_pos:next_pos+20]
                    before_text = term_text[max(0, current_pos-20):current_pos]

                    periods = []
                    # 現在の時限を追加
                    periods.append(period)

                    # ペアの講義時間をチェック
                    if 'ペア' in term_text:
                        # ケース1: 現在の時限の直後に（ペア）がある場合、次の時限を追加
                        if '（ペア）' in after_text:
                            periods.append(period + 1)
                            i += 1  # 次の時限をスキップ
                        # ケース2: 次の時限とペアの場合（例：火３(Y119)・火４（ペア））
                        elif '・' in after_text and i + 1 < len(time_matches):
                            next_match = time_matches[i+1]
                            next_day = day_map[next_match.group(1)]
                            next_period = period_map[next_match.group(2)]
                            if next_day == day and next_period == period + 1:
                                periods.append(next_period)
                                i += 1  # 次の時限をスキップ
                        # ケース3: 前の時限とペアの場合
                        elif '・' in before_text and i > 0:
                            prev_match = time_matches[i-1]
                            prev_day = day_map[prev_match.group(1)]
                            prev_period = period_map[prev_match.group(2)]
                            if prev_day == day and prev_period == period - 1:
                                periods = [prev_period, period]  # 前の時限と現在の時限を追加

                    # エントリーを作成
                    entry = {
                        "subject_code": subject_code,
                        "day_of_week": day,
                        "periods": sorted(periods),  # 時限を昇順でソート
                        "created_at": datetime.now().isoformat()
                    }
                    time_slots.append(entry)
                    i += 1

        return time_slots

    except Exception as e:
        print(f"  Error parsing syllabus time: {str(e)}")
        return []

def save_json(entry, year, table_name):
    if table_name == 'subject':
        subject_code = entry["subject_code"]
    elif table_name == 'syllabus_time':
        subject_code = entry["subject_code"]
    else:  # syllabus
        subject_code = entry["subject_code"]  # シラバス管理番号を使用

    out_dir = f"db/updates/{table_name}/add"
    os.makedirs(out_dir, exist_ok=True)
    filepath = os.path.join(out_dir, f"{subject_code}.json")
    
    # contentフィールドを持つ形式に変更
    json_data = {
        "content": entry
    }
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    print(f"  Saved: {filepath}")

def main():
    parser = argparse.ArgumentParser(description='Parse syllabus HTML and output JSON files.')
    parser.add_argument('-y', '--year', required=True, help='Target year')
    parser.add_argument(
        '-t', '--table',
        required=True,
        choices=['subject', 'syllabus', 'syllabus_time'],
        help='''Target table name:
            subject: Extract subject information (code, name, etc.)
            syllabus: Extract syllabus details (summary, goals, etc.)
            syllabus_time: Extract class schedule information (day of week, period)'''
    )
    args = parser.parse_args()

    if args.table == 'subject':
        html_files = glob(f"src/syllabus/{args.year}/search_page/*.html")
    else:  # syllabus or syllabus_time
        html_files = glob(f"src/syllabus/{args.year}/raw_page/*.html")
        # .pretty.htmlファイルを除外
        html_files = [f for f in html_files if not f.endswith('.pretty.html')]

    total_files = len(html_files)
    print(f"Found {total_files} HTML files.")

    processed_count = 0
    for file in html_files:
        processed_count += 1
        print(f"\nProcessing file {processed_count}/{total_files}: {file}")
        try:
            entries = parse_html_file(file, args.table)
            for entry in entries:
                save_json(entry, args.year, args.table)
        except Exception as e:
            print(f"Error processing {file}: {str(e)}")
            continue

    print(f"\nCompleted processing {processed_count} files.")

if __name__ == '__main__':
    main()
