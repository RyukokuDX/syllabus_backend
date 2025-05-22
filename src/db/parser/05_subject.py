import os
import csv
import json
import psycopg2
from datetime import datetime
from pathlib import Path
from tqdm import tqdm
import re

DB_HOST = os.environ.get('PGHOST', 'localhost')
DB_PORT = os.environ.get('PGPORT', '5432')
DB_NAME = os.environ.get('POSTGRES_DB', 'syllabus_db')
DB_USER = os.environ.get('POSTGRES_USER', 'postgres')
DB_PASSWORD = os.environ.get('POSTGRES_PASSWORD', 'postgres')

# DBからIDを取得する関数
def get_id(conn, table, column, value):
    with conn.cursor() as cur:
        cur.execute(f"SELECT {table}_id FROM {table} WHERE {column} = %s", (value,))
        row = cur.fetchone()
        return row[0] if row else None

def parse_attribute(attribute):
    class_name = attribute
    subclass_name = None
    class_note = None

    # 「：」があれば、左側をclass_noteに
    if '：' in class_name:
        parts = class_name.split('：')
        if parts[0].strip() == "法学部専攻科目":
            class_note = parts[1].strip()
            class_name = parts[0].strip()
        else:
            class_note = parts[0].strip()
            class_name = parts[1].strip()

    # 「・」があれば、右側をsubclass_nameに、左側を保持
    if '・' in attribute:
        parts = class_name.split('・')
        class_name = parts[0].strip()
        subclass_name = parts[1].strip()

    return class_name, subclass_name, class_note

def extract_lecture_code(schedule):
    m = re.search(r'（(.+?)）', schedule)  # 全角カッコ
    if not m:
        m = re.search(r'\((.+?)\)', schedule)  # 半角カッコも念のため
    return m.group(1) if m else None

def normalize_class_name(name):
    # 全角・半角スペースを除去し、前後の空白も削除
    if name is None:
        return None
    return name.strip()

def main(year):
    csv_file = f"src/syllabus/{year}/search_page/syllabus_list.csv"
    if not os.path.exists(csv_file):
        print(f"CSV file not found: {csv_file}")
        return
    output_dir = Path(f"updates/subject/add")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"subject_{year}.json"

    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

    not_found_class_names = set()
    skipped_rows = []
    entries = []

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = list(csv.DictReader(f))
        total = len(reader)
        for row in tqdm(reader, total=total, desc="Processing rows"):
            try:
                syllabus_code = row.get('シラバス管理番号', '')
                name = row.get('科目名', '')
                attribute = row.get('属性', '')
                schedule = row.get('曜講時', '')
                lecture_code = extract_lecture_code(schedule)
                missing_fields = []
                if not syllabus_code:
                    missing_fields.append('シラバス管理番号')
                if not name:
                    missing_fields.append('科目名')
                if not attribute:
                    missing_fields.append('属性')
                if missing_fields:
                    print(f"[SKIP] {syllabus_code or '[NO CODE]'}: 欠損フィールド: {', '.join(missing_fields)}")
                    skipped_rows.append((syllabus_code, 'missing_fields', missing_fields))
                    continue
                class_name, subclass_name, class_note = parse_attribute(attribute)
                class_name_norm = normalize_class_name(class_name)
                subject_name_id = get_id(conn, 'subject_name', 'name', name)
                class_id = get_id(conn, 'class', 'class_name', class_name_norm)
                subclass_id = get_id(conn, 'subclass', 'subclass_name', subclass_name) if subclass_name else None
                class_note_id = get_id(conn, 'class_note', 'class_note', class_note) if class_note else None
                id_missing = []
                if not subject_name_id:
                    id_missing.append('subject_name_id')
                if not class_id:
                    id_missing.append('class_id')
                if id_missing:
                    print(f"[SKIP] {syllabus_code}: ID未発見: {', '.join(id_missing)} (class_name='{class_name_norm}')")
                    if not class_id:
                        not_found_class_names.add(class_name_norm)
                    skipped_rows.append((syllabus_code, 'id_missing', id_missing))
                    continue
                entry = {
                    "syllabus_code": syllabus_code,
                    "subject_name_id": subject_name_id,
                    "class_id": class_id,
                    "subclass_id": subclass_id,
                    "class_note_id": class_note_id,
                    "lecture_code": lecture_code,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": None
                }
                entries.append(entry)
            except Exception as e:
                print(f"[SKIP] {row.get('シラバス管理番号', '[NO CODE]')}: Error processing row: {str(e)}")
                skipped_rows.append((row.get('シラバス管理番号', '[NO CODE]'), 'exception', str(e)))
                continue
    conn.close()
    # 単一ファイルにまとめて保存
    if entries:
        with open(output_file, 'w', encoding='utf-8') as jf:
            json.dump({"subjects": entries}, jf, ensure_ascii=False, indent=2)
        print(f"Saved {len(entries)} subject JSON entries to {output_file}")
    else:
        print("No valid subject entries to save.")
    if not_found_class_names:
        print("\n[Not Found class_name候補一覧]")
        for cname in sorted(not_found_class_names):
            print(f"  - '{cname}'")
    if skipped_rows:
        print(f"\n[Summary] Skipped {len(skipped_rows)} rows. See above for details.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate subject insert JSON from syllabus_list.csv")
    parser.add_argument("-y", "--year", help="Year to process")
    args = parser.parse_args()
    
    year = args.year
    if not year:
        year = input("年度を入力してください（空の場合は今年）: ").strip()
        if not year:
            year = datetime.now().year
    
    main(str(year)) 