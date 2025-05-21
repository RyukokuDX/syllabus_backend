import json
import os
from datetime import datetime
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional, Dict, Any
import sys

# src/dbをPythonパスに追加
sys.path.append(str(Path(__file__).parent.parent))
from models import Base

# データベース接続設定
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/syllabus')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def read_json_files(directory, table_name):
    """指定されたディレクトリ内のすべてのJSONファイルを読み込む"""
    data = []
    json_files = list(Path(directory).glob('*.json'))
    
    if not json_files:
        print(f"No JSON files found in {directory}")
        return data
        
    for file in json_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
                # テーブル名に応じた配列名を取得
                array_name = {
                    'class': 'classes',
                    'subclass': 'subclasses'
                }.get(table_name, f"{table_name}s")
                
                if array_name in json_data:
                    records = json_data[array_name]
                    print(f"Found {len(records)} records in {file}")
                    data.extend(records)
                else:
                    print(f"Warning: {file} does not contain '{array_name}' array")
        except Exception as e:
            print(f"Error reading {file}: {str(e)}")
    
    print(f"Total records found for {table_name}: {len(data)}")
    return data

def generate_sql_insert(table_name, records):
    """SQLのINSERT文を生成する"""
    if not records:
        return ""

    # カラム名を取得
    columns = records[0].keys()
    columns_str = ', '.join(columns)

    # VALUES句を生成
    values = []
    for record in records:
        values_list = []
        for column in columns:
            value = record[column]
            if value is None:
                values_list.append('NULL')
            elif isinstance(value, (int, float)):
                values_list.append(str(value))
            elif isinstance(value, str):
                # 文字列のエスケープ処理
                escaped_value = value.replace("'", "''")
                values_list.append(f"'{escaped_value}'")
            else:
                values_list.append(f"'{value}'")
        values.append(f"    ({', '.join(values_list)})")

    values_str = ',\n'.join(values)

    # テーブルごとのON CONFLICT句を設定
    conflict_columns = {
        'class': ['class_name'],
        'subclass': ['subclass_name'],
        'class_note': ['class_note'],
        'subject_name': ['name'],
        'subject': ['syllabus_code'],
        'syllabus': ['syllabus_code', 'year', 'term'],
        'lecture_session': ['syllabus_code', 'session_number'],
        'instructor': ['instructor_code'],
        'syllabus_instructor': ['syllabus_code', 'instructor_code'],
        'book': ['isbn'],
        'syllabus_book': ['syllabus_code', 'isbn'],
        'grading_criterion': ['syllabus_code', 'criteria_id'],
        'syllabus_faculty': ['syllabus_code', 'faculty_id']
    }
    
    # 更新対象のカラムを設定
    update_columns = {
        'class': [col for col in columns if col not in ['class_name', 'created_at']],
        'subclass': [col for col in columns if col not in ['subclass_name', 'created_at']],
        'class_note': [col for col in columns if col not in ['class_note', 'created_at']],
        'subject_name': [col for col in columns if col not in ['name', 'created_at']],
        'subject': [col for col in columns if col not in ['syllabus_code', 'created_at']],
        'syllabus': [col for col in columns if col not in ['syllabus_code', 'year', 'term', 'created_at']],
        'lecture_session': [col for col in columns if col not in ['syllabus_code', 'session_number', 'created_at']],
        'instructor': [col for col in columns if col not in ['instructor_code', 'created_at']],
        'syllabus_instructor': [col for col in columns if col not in ['syllabus_code', 'instructor_code', 'created_at']],
        'book': [col for col in columns if col not in ['isbn', 'created_at']],
        'syllabus_book': [col for col in columns if col not in ['syllabus_code', 'isbn', 'created_at']],
        'grading_criterion': [col for col in columns if col not in ['syllabus_code', 'criteria_id', 'created_at']],
        'syllabus_faculty': [col for col in columns if col not in ['syllabus_code', 'faculty_id', 'created_at']]
    }

    # ON CONFLICT句を生成
    conflict_cols = conflict_columns.get(table_name, ['syllabus_code'])
    update_cols = update_columns.get(table_name, [col for col in columns if col not in ['syllabus_code', 'created_at']])
    
    conflict_str = ', '.join(conflict_cols)
    update_str = ',\n    '.join([f"{col} = EXCLUDED.{col}" for col in update_cols])
    update_str += ",\n    updated_at = CURRENT_TIMESTAMP"

    sql = f"""-- {table_name} テーブルへのデータ挿入
INSERT INTO {table_name} (
    {columns_str}
) VALUES
{values_str}
ON CONFLICT ({conflict_str}) DO UPDATE SET
    {update_str};
"""
    return sql

def generate_migration():
    """マイグレーションファイルを生成"""
    try:
        # プロジェクトルートからの相対パス
        project_root = Path(__file__).parent.parent.parent.parent
        
        # 処理対象のディレクトリとテーブル名のマッピング
        targets = [
            {
                'json_dir': project_root / 'updates' / 'class' / 'add',
                'table_name': 'class',
                'source': 'syllabus_search'
            },
            {
                'json_dir': project_root / 'updates' / 'subclass' / 'add',
                'table_name': 'subclass',
                'source': 'syllabus_search'
            },
            {
                'json_dir': project_root / 'updates' / 'class_note' / 'add',
                'table_name': 'class_note',
                'source': 'syllabus_search'
            },
            {
                'json_dir': project_root / 'updates' / 'subject_name' / 'add',
                'table_name': 'subject_name',
                'source': 'syllabus_search'
            },
            {
                'json_dir': project_root / 'updates' / 'subject' / 'add',
                'table_name': 'subject',
                'source': 'syllabus_search'
            },
            {
                'json_dir': project_root / 'updates' / 'faculty' / 'add',
                'table_name': 'faculty',
                'source': 'syllabus_search'
            },
            {
                'json_dir': project_root / 'updates' / 'instructor' / 'add',
                'table_name': 'instructor',
                'source': 'web_syllabus'
            },
            {
                'json_dir': project_root / 'updates' / 'criteria' / 'add',
                'table_name': 'criteria',
                'source': 'web_syllabus'
            },
            {
                'json_dir': project_root / 'updates' / 'book' / 'add',
                'table_name': 'book',
                'source': 'web_syllabus'
            },
            {
                'json_dir': project_root / 'updates' / 'syllabus' / 'add',
                'table_name': 'syllabus',
                'source': 'web_syllabus'
            },
            {
                'json_dir': project_root / 'updates' / 'syllabus_faculty' / 'add',
                'table_name': 'syllabus_faculty',
                'source': 'web_syllabus'
            },
            {
                'json_dir': project_root / 'updates' / 'lecture_session' / 'add',
                'table_name': 'lecture_session',
                'source': 'web_syllabus'
            },
            {
                'json_dir': project_root / 'updates' / 'syllabus_instructor' / 'add',
                'table_name': 'syllabus_instructor',
                'source': 'web_syllabus'
            },
            {
                'json_dir': project_root / 'updates' / 'syllabus_book' / 'add',
                'table_name': 'syllabus_book',
                'source': 'web_syllabus'
            },
            {
                'json_dir': project_root / 'updates' / 'grading_criterion' / 'add',
                'table_name': 'grading_criterion',
                'source': 'web_syllabus'
            },
            {
                'json_dir': project_root / 'updates' / 'subject_requirement' / 'add',
                'table_name': 'subject_requirement',
                'source': 'web_syllabus'
            },
            {
                'json_dir': project_root / 'updates' / 'subject_program' / 'add',
                'table_name': 'subject_program',
                'source': 'web_syllabus'
            },
            {
                'json_dir': project_root / 'updates' / 'requirement' / 'add',
                'table_name': 'requirement',
                'source': 'web_syllabus'
            }
        ]
        
        # 出力先ディレクトリ
        output_dir = project_root / 'docker' / 'postgresql' / 'init' / 'migrations'
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for target in targets:
            print(f"\nProcessing {target['table_name']}...")
            if not target['json_dir'].exists():
                print(f"Creating directory: {target['json_dir']}")
                target['json_dir'].mkdir(parents=True, exist_ok=True)
                continue
                
            # JSONデータを読み込む
            records = read_json_files(target['json_dir'], target['table_name'])
            if not records:
                print(f"No records found for {target['table_name']}")
                continue
            
            # SQL生成
            sql = generate_sql_insert(target['table_name'], records)
            if not sql:
                print(f"No SQL generated for {target['table_name']}")
                continue
            
            # ファイルに書き出し
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            output_file = output_dir / f'V{timestamp}__insert_{target["table_name"]}s.sql'
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(sql)
            
            # 使用したJSONファイルを移動
            registered_dir = project_root / 'updates' / target['table_name'] / 'registered' / output_file.stem
            registered_dir.mkdir(parents=True, exist_ok=True)
            
            for json_file in target['json_dir'].glob('*.json'):
                json_file.rename(registered_dir / json_file.name)
            
            print(f'Generated migration file: {output_file}')
            print(f'Moved JSON files to: {registered_dir}')
        
        return True
    except Exception as e:
        print(f'Error generating migration: {str(e)}')
        return False

def generate_migration_sql() -> str:
    """マイグレーションSQLを生成"""
    sql = []
    
    # テーブル作成
    sql.append("""
-- 科目区分テーブル
CREATE TABLE IF NOT EXISTS class (
    class_id SERIAL PRIMARY KEY,
    class_name TEXT NOT NULL
);

-- 科目小区分テーブル
CREATE TABLE IF NOT EXISTS subclass (
    subclass_id SERIAL PRIMARY KEY,
    subclass_name TEXT NOT NULL
);

-- 科目区分の備考テーブル
CREATE TABLE IF NOT EXISTS class_note (
    class_note_id SERIAL PRIMARY KEY,
    class_note TEXT NOT NULL
);

-- 科目名マスタテーブル
CREATE TABLE IF NOT EXISTS subject_name (
    subject_name_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

-- 科目基本情報テーブル
CREATE TABLE IF NOT EXISTS subject (
    syllabus_code TEXT PRIMARY KEY,
    subject_name_id INTEGER NOT NULL REFERENCES subject_name(subject_name_id),
    class_id INTEGER NOT NULL REFERENCES class(class_id),
    subclass_id INTEGER REFERENCES subclass(subclass_id),
    class_note_id INTEGER REFERENCES class_note(class_note_id),
    lecture_code TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- 開講学部・課程テーブル
CREATE TABLE IF NOT EXISTS faculty (
    faculty_id SERIAL PRIMARY KEY,
    faculty_name TEXT NOT NULL
);

-- 教員テーブル
CREATE TABLE IF NOT EXISTS instructor (
    instructor_code TEXT PRIMARY KEY,
    last_name TEXT NOT NULL,
    first_name TEXT NOT NULL,
    last_name_kana TEXT,
    first_name_kana TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- 評価種別マスタテーブル
CREATE TABLE IF NOT EXISTS criteria (
    criteria_id SERIAL PRIMARY KEY,
    criteria_name TEXT NOT NULL
);

-- 書籍テーブル
CREATE TABLE IF NOT EXISTS book (
    isbn TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT,
    publisher TEXT,
    publication_year INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- シラバス情報テーブル
CREATE TABLE IF NOT EXISTS syllabus (
    syllabus_code TEXT PRIMARY KEY REFERENCES subject(syllabus_code),
    year INTEGER NOT NULL,
    term TEXT NOT NULL,
    subtitle TEXT,
    goals TEXT,
    methods TEXT,
    outside_study TEXT,
    notes TEXT,
    remarks TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- シラバス学部課程関連テーブル
CREATE TABLE IF NOT EXISTS syllabus_faculty (
    syllabus_code TEXT REFERENCES syllabus(syllabus_code),
    faculty_id INTEGER REFERENCES faculty(faculty_id),
    PRIMARY KEY (syllabus_code, faculty_id)
);

-- 講義時間テーブル
CREATE TABLE IF NOT EXISTS lecture_session (
    syllabus_code TEXT REFERENCES syllabus(syllabus_code),
    session_number INTEGER NOT NULL,
    day_of_week TEXT NOT NULL,
    period INTEGER NOT NULL,
    room TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    PRIMARY KEY (syllabus_code, session_number)
);

-- シラバス教員関連テーブル
CREATE TABLE IF NOT EXISTS syllabus_instructor (
    syllabus_code TEXT REFERENCES syllabus(syllabus_code),
    instructor_code TEXT REFERENCES instructor(instructor_code),
    PRIMARY KEY (syllabus_code, instructor_code)
);

-- シラバス教科書関連テーブル
CREATE TABLE IF NOT EXISTS syllabus_book (
    syllabus_code TEXT REFERENCES syllabus(syllabus_code),
    isbn TEXT REFERENCES book(isbn),
    is_textbook BOOLEAN NOT NULL,
    PRIMARY KEY (syllabus_code, isbn)
);

-- 成績評価基準テーブル
CREATE TABLE IF NOT EXISTS grading_criterion (
    syllabus_code TEXT REFERENCES syllabus(syllabus_code),
    criteria_id INTEGER REFERENCES criteria(criteria_id),
    percentage INTEGER NOT NULL,
    description TEXT,
    PRIMARY KEY (syllabus_code, criteria_id)
);

-- 科目要綱関連テーブル
CREATE TABLE IF NOT EXISTS subject_requirement (
    syllabus_code TEXT REFERENCES syllabus(syllabus_code),
    requirement_id INTEGER NOT NULL,
    PRIMARY KEY (syllabus_code, requirement_id)
);

-- 科目学習プログラム関連テーブル
CREATE TABLE IF NOT EXISTS subject_program (
    syllabus_code TEXT REFERENCES syllabus(syllabus_code),
    program_id INTEGER NOT NULL,
    PRIMARY KEY (syllabus_code, program_id)
);

-- 科目要件属性テーブル
CREATE TABLE IF NOT EXISTS requirement (
    requirement_id SERIAL PRIMARY KEY,
    requirement_name TEXT NOT NULL
);

-- インデックスの作成
CREATE INDEX IF NOT EXISTS idx_subject_name ON subject(subject_name_id);
CREATE INDEX IF NOT EXISTS idx_subject_class ON subject(class_id);
CREATE INDEX IF NOT EXISTS idx_instructor_name ON instructor(last_name, first_name);
CREATE INDEX IF NOT EXISTS idx_instructor_name_kana ON instructor(last_name_kana, first_name_kana);
""")
    
    return '\n'.join(sql)

if __name__ == '__main__':
    generate_migration() 