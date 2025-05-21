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

def generate_table_definitions():
    """テーブル定義のSQLを生成する"""
    table_definitions = {
        'class': """
CREATE TABLE IF NOT EXISTS class (
    class_id SERIAL PRIMARY KEY,
    class_name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);""",
        'subclass': """
CREATE TABLE IF NOT EXISTS subclass (
    subclass_id SERIAL PRIMARY KEY,
    subclass_name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);""",
        'class_note': """
CREATE TABLE IF NOT EXISTS class_note (
    class_note_id SERIAL PRIMARY KEY,
    class_note TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);""",
        'subject_name': """
CREATE TABLE IF NOT EXISTS subject_name (
    subject_name_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);""",
        'subject': """
CREATE TABLE IF NOT EXISTS subject (
    syllabus_code TEXT PRIMARY KEY,
    subject_name_id INTEGER NOT NULL,
    class_id INTEGER NOT NULL,
    subclass_id INTEGER,
    class_note_id INTEGER,
    lecture_code TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (subject_name_id) REFERENCES subject_name(subject_name_id) ON DELETE RESTRICT,
    FOREIGN KEY (class_id) REFERENCES class(class_id) ON DELETE RESTRICT,
    FOREIGN KEY (subclass_id) REFERENCES subclass(subclass_id) ON DELETE RESTRICT,
    FOREIGN KEY (class_note_id) REFERENCES class_note(class_note_id) ON DELETE RESTRICT
);""",
        'faculty': """
CREATE TABLE IF NOT EXISTS faculty (
    faculty_id SERIAL PRIMARY KEY,
    faculty_name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);""",
        'instructor': """
CREATE TABLE IF NOT EXISTS instructor (
    instructor_code TEXT PRIMARY KEY,
    last_name TEXT NOT NULL,
    first_name TEXT NOT NULL,
    last_name_kana TEXT,
    first_name_kana TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);""",
        'criteria': """
CREATE TABLE IF NOT EXISTS criteria (
    criteria_id SERIAL PRIMARY KEY,
    criteria_type TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);""",
        'book': """
CREATE TABLE IF NOT EXISTS book (
    id SERIAL PRIMARY KEY,
    author TEXT,
    title TEXT NOT NULL,
    publisher TEXT,
    price INTEGER,
    isbn TEXT UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);""",
        'syllabus': """
CREATE TABLE IF NOT EXISTS syllabus (
    syllabus_code TEXT,
    year INTEGER,
    subtitle TEXT,
    term TEXT NOT NULL,
    grade_b1 BOOLEAN NOT NULL,
    grade_b2 BOOLEAN NOT NULL,
    grade_b3 BOOLEAN NOT NULL,
    grade_b4 BOOLEAN NOT NULL,
    grade_m1 BOOLEAN NOT NULL,
    grade_m2 BOOLEAN NOT NULL,
    grade_d1 BOOLEAN NOT NULL,
    grade_d2 BOOLEAN NOT NULL,
    grade_d3 BOOLEAN NOT NULL,
    campus TEXT NOT NULL,
    credits INTEGER NOT NULL,
    summary TEXT,
    goals TEXT,
    methods TEXT,
    outside_study TEXT,
    notes TEXT,
    remarks TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    PRIMARY KEY (syllabus_code, year),
    FOREIGN KEY (syllabus_code) REFERENCES subject(syllabus_code) ON DELETE CASCADE
);""",
        'lecture_session': """
CREATE TABLE IF NOT EXISTS lecture_session (
    id SERIAL PRIMARY KEY,
    syllabus_code TEXT NOT NULL,
    year INTEGER NOT NULL,
    day_of_week TEXT NOT NULL,
    period INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (syllabus_code, year) REFERENCES syllabus(syllabus_code, year) ON DELETE CASCADE
);""",
        'syllabus_instructor': """
CREATE TABLE IF NOT EXISTS syllabus_instructor (
    id SERIAL PRIMARY KEY,
    syllabus_code TEXT NOT NULL,
    instructor_code TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (syllabus_code) REFERENCES subject(syllabus_code) ON DELETE CASCADE,
    FOREIGN KEY (instructor_code) REFERENCES instructor(instructor_code) ON DELETE CASCADE
);""",
        'syllabus_book': """
CREATE TABLE IF NOT EXISTS syllabus_book (
    id SERIAL PRIMARY KEY,
    syllabus_code TEXT NOT NULL,
    book_id INTEGER NOT NULL,
    role INTEGER NOT NULL,
    note TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (syllabus_code) REFERENCES subject(syllabus_code) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES book(id) ON DELETE CASCADE
);""",
        'grading_criterion': """
CREATE TABLE IF NOT EXISTS grading_criterion (
    id SERIAL PRIMARY KEY,
    syllabus_code TEXT NOT NULL,
    year INTEGER NOT NULL,
    criteria_id INTEGER NOT NULL,
    ratio INTEGER,
    note TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (syllabus_code, year) REFERENCES syllabus(syllabus_code, year) ON DELETE CASCADE,
    FOREIGN KEY (criteria_id) REFERENCES criteria(criteria_id) ON DELETE RESTRICT
);""",
        'syllabus_faculty': """
CREATE TABLE IF NOT EXISTS syllabus_faculty (
    id SERIAL PRIMARY KEY,
    syllabus_code TEXT NOT NULL,
    faculty_id INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (syllabus_code) REFERENCES subject(syllabus_code) ON DELETE CASCADE,
    FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id) ON DELETE CASCADE
);"""
    }
    
    # インデックス定義
    index_definitions = {
        'subject_name': """
CREATE UNIQUE INDEX IF NOT EXISTS idx_subject_name_name ON subject_name(name);""",
        'subject': """
CREATE INDEX IF NOT EXISTS idx_subject_name ON subject(subject_name_id);
CREATE INDEX IF NOT EXISTS idx_subject_class ON subject(class_id);""",
        'instructor': """
CREATE INDEX IF NOT EXISTS idx_instructor_name ON instructor(last_name, first_name);
CREATE INDEX IF NOT EXISTS idx_instructor_name_kana ON instructor(last_name_kana, first_name_kana);""",
        'criteria': """
CREATE UNIQUE INDEX IF NOT EXISTS idx_criteria_type ON criteria(criteria_type);""",
        'book': """
CREATE INDEX IF NOT EXISTS idx_book_title ON book(title);
CREATE INDEX IF NOT EXISTS idx_book_author ON book(author);""",
        'syllabus': """
CREATE INDEX IF NOT EXISTS idx_syllabus_year ON syllabus(year);
CREATE INDEX IF NOT EXISTS idx_syllabus_term ON syllabus(term);
CREATE INDEX IF NOT EXISTS idx_syllabus_grades ON syllabus(grade_b1, grade_b2, grade_b3, grade_b4, grade_m1, grade_m2, grade_d1, grade_d2, grade_d3);
CREATE INDEX IF NOT EXISTS idx_syllabus_campus ON syllabus(campus);""",
        'lecture_session': """
CREATE INDEX IF NOT EXISTS idx_lecture_session_day_period ON lecture_session(day_of_week, period);
CREATE INDEX IF NOT EXISTS idx_lecture_session_syllabus ON lecture_session(syllabus_code, year);""",
        'syllabus_instructor': """
CREATE INDEX IF NOT EXISTS idx_syllabus_instructor_syllabus ON syllabus_instructor(syllabus_code);
CREATE INDEX IF NOT EXISTS idx_syllabus_instructor_instructor ON syllabus_instructor(instructor_code);""",
        'syllabus_book': """
CREATE INDEX IF NOT EXISTS idx_syllabus_book_syllabus ON syllabus_book(syllabus_code);
CREATE INDEX IF NOT EXISTS idx_syllabus_book_book ON syllabus_book(book_id);""",
        'grading_criterion': """
CREATE INDEX IF NOT EXISTS idx_grading_criterion_criteria ON grading_criterion(criteria_id);
CREATE INDEX IF NOT EXISTS idx_grading_criterion_syllabus_criteria ON grading_criterion(syllabus_code, year, criteria_id);""",
        'syllabus_faculty': """
CREATE INDEX IF NOT EXISTS idx_syllabus_faculty_syllabus ON syllabus_faculty(syllabus_code);
CREATE INDEX IF NOT EXISTS idx_syllabus_faculty_faculty ON syllabus_faculty(faculty_id);"""
    }
    
    # テーブル定義とインデックスを結合
    sql = []
    for table_name in table_definitions.keys():
        sql.append(table_definitions[table_name])
        if table_name in index_definitions:
            sql.append(index_definitions[table_name])
    
    return '\n\n'.join(sql)

def generate_migration():
    """マイグレーションファイルを生成"""
    try:
        # プロジェクトルートからの相対パス
        project_root = Path(__file__).parent.parent.parent.parent
        
        # テーブル定義を生成
        table_definitions = generate_table_definitions()
        
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
            }
        ]
        
        # マイグレーションファイルの出力先ディレクトリ
        migrations_dir = project_root / 'docker' / 'postgresql' / 'init' / 'migrations'
        migrations_dir.mkdir(parents=True, exist_ok=True)
        
        # 現在のタイムスタンプを取得
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        
        # テーブル定義を含むSQLファイルを生成
        init_sql_path = project_root / 'docker' / 'postgresql' / 'init' / '02-init.sql'
        with open(init_sql_path, 'w', encoding='utf-8') as f:
            f.write(table_definitions)
        
        # 各テーブルのデータ挿入用SQLを生成
        for target in targets:
            json_dir = target['json_dir']
            table_name = target['table_name']
            source = target['source']
            
            if not json_dir.exists():
                print(f"Directory not found: {json_dir}")
                continue
            
            # JSONファイルからデータを読み込む
            records = read_json_files(json_dir, table_name)
            if not records:
                print(f"No records found for {table_name}")
                continue
            
            # SQLを生成
            sql = generate_sql_insert(table_name, records)
            if not sql:
                print(f"No SQL generated for {table_name}")
                continue
            
            # マイグレーションファイル名を生成
            migration_file = migrations_dir / f"V{timestamp}__insert_{table_name}s.sql"
            
            # SQLをファイルに書き込む
            with open(migration_file, 'w', encoding='utf-8') as f:
                f.write(sql)
            
            print(f"Generated migration file: {migration_file}")
        
        print("Migration files generation completed successfully")
        
    except Exception as e:
        print(f"Error generating migration files: {str(e)}")
        raise

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