import argparse
import os
import json
from bs4 import BeautifulSoup
from glob import glob
from datetime import datetime

def parse_html_file(filepath):
    print(f"Processing: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    # 整形されたHTMLを初回のみ保存（多重保存を防ぐ）
    pretty_path = filepath.replace('.pretty.html', '') + '.pretty.html'
    if not os.path.exists(pretty_path):
        with open(pretty_path, 'w', encoding='utf-8') as f:
            f.write(soup.prettify())

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

def save_json(entry, year):
    subject_code = entry["subject_code"]
    out_dir = f"db/updates/subject/add"
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
    args = parser.parse_args()

    html_files = glob(f"src/syllabus/{args.year}/search_page/*.html")
    print(f"Found {len(html_files)} HTML files.")
    for file in html_files:
        entries = parse_html_file(file)
        for entry in entries:
            save_json(entry, args.year)

if __name__ == '__main__':
    main()
