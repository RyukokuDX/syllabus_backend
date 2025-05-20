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

def read_json_files(directory):
    """指定されたディレクトリ内のすべてのJSONファイルを読み込む"""
    data = []
    for file in Path(directory).glob('*.json'):
        with open(file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            data.append(json_data['content'])
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
            else:
                values_list.append(f"'{value}'")
        values.append(f"    ({', '.join(values_list)})")

    values_str = ',\n'.join(values)

    # テーブルごとのON CONFLICT句を設定
    conflict_columns = {
        'subject': ['subject_code'],
        'syllabus': ['subject_code', 'year', 'term'],
        'syllabus_time': ['subject_code', 'day_of_week', 'period'],
        'instructor': ['instructor_code'],
        'syllabus_instructor': ['subject_code', 'instructor_code'],
        'lecture_session': ['subject_code', 'session_number'],
        'book': ['isbn'],
        'syllabus_textbook': ['subject_code', 'book_id'],
        'syllabus_reference': ['subject_code', 'book_id'],
        'grading_criterion': ['subject_code', 'criteria_type'],
        'syllabus_faculty': ['subject_code', 'faculty']
    }
    
    # 更新対象のカラムを設定
    update_columns = {
        'subject': [col for col in columns if col not in ['subject_code', 'created_at']],
        'syllabus': [col for col in columns if col not in ['subject_code', 'year', 'term', 'created_at']],
        'syllabus_time': [col for col in columns if col not in ['subject_code', 'day_of_week', 'period', 'created_at']],
        'instructor': [col for col in columns if col not in ['instructor_code', 'created_at']],
        'syllabus_instructor': [col for col in columns if col not in ['subject_code', 'instructor_code', 'created_at']],
        'lecture_session': [col for col in columns if col not in ['subject_code', 'session_number', 'created_at']],
        'book': [col for col in columns if col not in ['isbn', 'created_at']],
        'syllabus_textbook': [col for col in columns if col not in ['subject_code', 'book_id', 'created_at']],
        'syllabus_reference': [col for col in columns if col not in ['subject_code', 'book_id', 'created_at']],
        'grading_criterion': [col for col in columns if col not in ['subject_code', 'criteria_type', 'created_at']],
        'syllabus_faculty': [col for col in columns if col not in ['subject_code', 'faculty', 'created_at']]
    }

    # ON CONFLICT句を生成
    conflict_cols = conflict_columns.get(table_name, ['subject_code'])
    update_cols = update_columns.get(table_name, [col for col in columns if col not in ['subject_code', 'created_at']])
    
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
        # マイグレーションファイルのパスを設定
        migration_dir = os.path.dirname(__file__)
        
        # 現在の日時を取得してファイル名を生成
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        migration_file = os.path.join(migration_dir, f'migration_{timestamp}.sql')
        
        # マイグレーションSQLを生成
        migration_sql = generate_migration_sql()
        
        # ファイルに書き込み
        with open(migration_file, 'w', encoding='utf-8') as f:
            f.write(migration_sql)
        
        print(f'Migration file generated: {migration_file}')
        return True
    except Exception as e:
        print(f'Error generating migration: {str(e)}')
        return False

def generate_migration_sql() -> str:
    """マイグレーションSQLを生成"""
    sql = []
    
    # テーブル作成
    sql.append("""
-- 科目基本情報テーブル
CREATE TABLE IF NOT EXISTS subject (
    syllabus_code TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    class_name TEXT NOT NULL,
    subclass_name TEXT,
    class_note TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- シラバス情報テーブル
CREATE TABLE IF NOT EXISTS syllabus (
    syllabus_code TEXT,
    year INTEGER,
    subtitle TEXT,
    term VARCHAR(10) NOT NULL,
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
    lecture_code TEXT NOT NULL,
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
);

-- 講義時間テーブル
CREATE TABLE IF NOT EXISTS lecture_session (
    id SERIAL PRIMARY KEY,
    syllabus_code TEXT NOT NULL,
    day_of_week INTEGER NOT NULL,
    period INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (syllabus_code) REFERENCES syllabus(syllabus_code) ON DELETE CASCADE
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

-- 書籍テーブル
CREATE TABLE IF NOT EXISTS book (
    id SERIAL PRIMARY KEY,
    author TEXT,
    title TEXT NOT NULL,
    publisher TEXT,
    price INTEGER,
    isbn VARCHAR(20),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- シラバス-教員関連テーブル
CREATE TABLE IF NOT EXISTS syllabus_instructor (
    id SERIAL PRIMARY KEY,
    syllabus_code TEXT NOT NULL,
    instructor_code TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (syllabus_code) REFERENCES subject(syllabus_code) ON DELETE CASCADE,
    FOREIGN KEY (instructor_code) REFERENCES instructor(instructor_code) ON DELETE CASCADE
);

-- シラバス-書籍関連テーブル
CREATE TABLE IF NOT EXISTS syllabus_book (
    id SERIAL PRIMARY KEY,
    syllabus_code TEXT NOT NULL,
    book_id INTEGER NOT NULL,
    role INTEGER NOT NULL,
    note TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (syllabus_code) REFERENCES subject(syllabus_code) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES book(id) ON DELETE CASCADE
);

-- 成績評価基準テーブル
CREATE TABLE IF NOT EXISTS grading_criterion (
    id SERIAL PRIMARY KEY,
    syllabus_code TEXT NOT NULL,
    criteria_type TEXT NOT NULL,
    ratio INTEGER,
    note TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (syllabus_code) REFERENCES syllabus(syllabus_code) ON DELETE CASCADE,
    CONSTRAINT check_grading_criterion_type_valid CHECK (criteria_type IN ('平常', '小テ', '定期', 'レポ', '他', '自由'))
);

-- シラバス-学部/課程関連テーブル
CREATE TABLE IF NOT EXISTS syllabus_faculty (
    id SERIAL PRIMARY KEY,
    syllabus_code TEXT NOT NULL,
    faculty VARCHAR(60) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (syllabus_code) REFERENCES subject(syllabus_code) ON DELETE CASCADE
);

-- 科目要件・属性テーブル
CREATE TABLE IF NOT EXISTS requirement (
    requirement_code TEXT PRIMARY KEY,
    subject_name TEXT NOT NULL,
    requirement_type TEXT NOT NULL,
    applied_science_available BOOLEAN NOT NULL,
    graduation_credit_limit BOOLEAN NOT NULL,
    year_restriction BOOLEAN NOT NULL,
    first_year_only BOOLEAN NOT NULL,
    up_to_second_year BOOLEAN NOT NULL,
    guidance_required BOOLEAN NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- 科目-要綱関連テーブル
CREATE TABLE IF NOT EXISTS subject_requirement (
    id SERIAL PRIMARY KEY,
    syllabus_code TEXT NOT NULL,
    requirement_code TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (syllabus_code) REFERENCES subject(syllabus_code) ON DELETE CASCADE,
    FOREIGN KEY (requirement_code) REFERENCES requirement(requirement_code) ON DELETE CASCADE
);

-- 科目-学習プログラム関連テーブル
CREATE TABLE IF NOT EXISTS subject_program (
    id SERIAL PRIMARY KEY,
    syllabus_code TEXT NOT NULL,
    program_code TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (syllabus_code) REFERENCES subject(syllabus_code) ON DELETE CASCADE
);
""")

    # インデックス作成
    sql.append("""
-- 講義時間テーブルのインデックス
CREATE INDEX IF NOT EXISTS idx_lecture_session_day_period ON lecture_session(day_of_week, period);
CREATE INDEX IF NOT EXISTS idx_lecture_session_syllabus ON lecture_session(syllabus_code);

-- 教員テーブルのインデックス
CREATE INDEX IF NOT EXISTS idx_instructor_name ON instructor(last_name, first_name);
CREATE INDEX IF NOT EXISTS idx_instructor_name_kana ON instructor(last_name_kana, first_name_kana);

-- 書籍テーブルのインデックス
CREATE INDEX IF NOT EXISTS idx_book_title ON book(title);
CREATE INDEX IF NOT EXISTS idx_book_author ON book(author);

-- シラバス-教員関連テーブルのインデックス
CREATE INDEX IF NOT EXISTS idx_syllabus_instructor_syllabus ON syllabus_instructor(syllabus_code);
CREATE INDEX IF NOT EXISTS idx_syllabus_instructor_instructor ON syllabus_instructor(instructor_code);

-- シラバス-書籍関連テーブルのインデックス
CREATE INDEX IF NOT EXISTS idx_syllabus_book_syllabus ON syllabus_book(syllabus_code);
CREATE INDEX IF NOT EXISTS idx_syllabus_book_book ON syllabus_book(book_id);

-- 成績評価基準テーブルのインデックス
CREATE INDEX IF NOT EXISTS idx_grading_criterion_type ON grading_criterion(criteria_type);
CREATE INDEX IF NOT EXISTS idx_grading_criterion_syllabus_type ON grading_criterion(syllabus_code, criteria_type);

-- シラバス-学部/課程関連テーブルのインデックス
CREATE INDEX IF NOT EXISTS idx_syllabus_faculty_syllabus ON syllabus_faculty(syllabus_code);
CREATE INDEX IF NOT EXISTS idx_syllabus_faculty_faculty ON syllabus_faculty(faculty);

-- 科目要件・属性テーブルのインデックス
CREATE INDEX IF NOT EXISTS idx_requirement_type ON requirement(requirement_type);
CREATE INDEX IF NOT EXISTS idx_requirement_restrictions ON requirement(applied_science_available, graduation_credit_limit, year_restriction);

-- 科目-要綱関連テーブルのインデックス
CREATE INDEX IF NOT EXISTS idx_subject_requirement_syllabus ON subject_requirement(syllabus_code);
CREATE INDEX IF NOT EXISTS idx_subject_requirement_requirement ON subject_requirement(requirement_code);

-- 科目-学習プログラム関連テーブルのインデックス
CREATE INDEX IF NOT EXISTS idx_subject_program_syllabus ON subject_program(syllabus_code);
CREATE INDEX IF NOT EXISTS idx_subject_program_program ON subject_program(program_code);
""")

    return '\n'.join(sql)

def main():
    # プロジェクトルートからの相対パス
    project_root = Path(__file__).parent.parent.parent.parent
    
    # 処理対象のディレクトリとテーブル名のマッピング
    targets = [
        {
            'json_dir': project_root / 'updates' / 'subject' / 'add',
            'table_name': 'subject',
            'source': 'syllabus_search'
        },
        {
            'json_dir': project_root / 'updates' / 'syllabus' / 'add',
            'table_name': 'syllabus',
            'source': 'web_syllabus'
        },
        {
            'json_dir': project_root / 'updates' / 'syllabus_time' / 'add',
            'table_name': 'syllabus_time',
            'source': 'web_syllabus'
        },
        {
            'json_dir': project_root / 'updates' / 'instructor' / 'add',
            'table_name': 'instructor',
            'source': 'web_syllabus'
        },
        {
            'json_dir': project_root / 'updates' / 'syllabus_instructor' / 'add',
            'table_name': 'syllabus_instructor',
            'source': 'web_syllabus'
        },
        {
            'json_dir': project_root / 'updates' / 'lecture_session' / 'add',
            'table_name': 'lecture_session',
            'source': 'web_syllabus'
        },
        {
            'json_dir': project_root / 'updates' / 'book' / 'add',
            'table_name': 'book',
            'source': 'web_syllabus'
        },
        {
            'json_dir': project_root / 'updates' / 'syllabus_textbook' / 'add',
            'table_name': 'syllabus_textbook',
            'source': 'web_syllabus'
        },
        {
            'json_dir': project_root / 'updates' / 'syllabus_reference' / 'add',
            'table_name': 'syllabus_reference',
            'source': 'web_syllabus'
        },
        {
            'json_dir': project_root / 'updates' / 'grading_criterion' / 'add',
            'table_name': 'grading_criterion',
            'source': 'web_syllabus'
        },
        {
            'json_dir': project_root / 'updates' / 'syllabus_faculty' / 'add',
            'table_name': 'syllabus_faculty',
            'source': 'web_syllabus'
        }
    ]
    
    # 出力先ディレクトリ
    output_dir = project_root / 'docker' / 'postgresql' / 'init' / 'migrations'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for target in targets:
        if not target['json_dir'].exists():
            print(f"Skipping {target['json_dir']} as it doesn't exist")
            continue
            
        # JSONデータを読み込む
        records = read_json_files(target['json_dir'])
        if not records:
            print(f"No JSON files found in {target['json_dir']}")
            continue
        
        # SQL生成
        sql = generate_sql_insert(target['table_name'], records)
        
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

if __name__ == '__main__':
    generate_migration() 