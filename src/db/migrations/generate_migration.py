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
    base_dir = Path(directory)
    
    # registeredディレクトリとaddディレクトリの両方を処理
    for subdir in ['registered', 'add']:
        json_dir = base_dir / subdir
        if not json_dir.exists():
            print(f"Directory not found: {json_dir}")
            continue
            
        json_files = list(json_dir.glob('*.json'))
        if not json_files:
            print(f"No JSON files found in {json_dir}")
            continue
            
        for file in json_files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                    # テーブル名に応じた配列名を取得
                    array_name = {
                        'class': 'classes',
                        'subclass': 'subclasses',
                        'faculty': 'faculties',
                        'subject_name': 'subject_names',
                        'subject': 'subjects',
                        'instructor': 'instructors',
                        'book': 'books',
                        'syllabus': 'syllabuses',
                        'lecture_session': 'lecture_sessions',
                        'syllabus_instructor': 'syllabus_instructors',
                        'syllabus_book': 'syllabus_books',
                        'grading_criterion': 'grading_criteria',
                        'subject_grade': 'subject_grades',
                        'subject_attribute': 'subject_attributes',
                        'subject_attribute_value': 'subject_attribute_values',
                        'subject_syllabus': 'subject_syllabuses',
                        'syllabus_study_system': 'syllabus_study_systems',
                        'lecture_session_instructor': 'lecture_session_instructors',
                        'lecture_time': 'lecture_times',
                        'book_author': 'book_authors'
                    }.get(table_name, f"{table_name}s")
                    
                    if array_name in json_data:
                        records = json_data[array_name]
                        # bookテーブルの場合、roleカラムを除外
                        if table_name == 'book':
                            records = [{k: v for k, v in record.items() if k != 'role'} for record in records]
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
    # bookテーブルの場合、authorカラムを除外
    if table_name == 'book':
        columns = [col for col in columns if col != 'author']
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

    # テーブルごとのON CONFLICT句を設定（structure.mdに準拠）
    conflict_columns = {
        'class': ['class_name'],
        'subclass': ['subclass_name'],
        'faculty': ['faculty_name'],
        'subject_name': ['name'],
        'instructor': ['instructor_code'],
        'book': ['isbn'],
        'book_author': ['book_id', 'author_name'],
        'syllabus_master': ['syllabus_code', 'syllabus_year'],
        'syllabus': ['syllabus_id'],
        'subject_grade': ['syllabus_id', 'grade'],
        'lecture_time': ['syllabus_id', 'day_of_week', 'period'],
        'lecture_session': ['lecture_session_id'],
        'lecture_session_instructor': ['lecture_session_id', 'instructor_id'],
        'syllabus_instructor': ['syllabus_id', 'instructor_id'],
        'syllabus_book': ['syllabus_id', 'book_id'],
        'grading_criterion': ['syllabus_id', 'criteria_type'],
        'subject_attribute': ['attribute_name'],
        'subject': ['subject_name_id', 'faculty_id', 'class_id', 'subclass_id', 'curriculum_year'],
        'subject_syllabus': ['subject_id', 'syllabus_id'],
        'subject_attribute_value': ['subject_id', 'attribute_id'],
        'syllabus_study_system': ['source_syllabus_id', 'target']
    }
    
    # 更新対象のカラムを設定（structure.mdに準拠）
    update_columns = {
        'class': None,  # 更新しない
        'subclass': None,  # 更新しない
        'faculty': None,  # 更新しない
        'subject_name': None,  # 更新しない
        'instructor': ['last_name', 'first_name', 'last_name_kana', 'first_name_kana', 'updated_at'],
        'book': ['title', 'publisher', 'price', 'updated_at'],
        'book_author': None,  # 更新しない
        'syllabus_master': ['updated_at'],
        'syllabus': ['subject_name_id', 'subtitle', 'term', 'campus', 'credits', 'goals', 'summary', 'attainment', 'methods', 'outside_study', 'notes', 'remarks', 'updated_at'],
        'subject_grade': ['updated_at'],
        'lecture_time': ['updated_at'],
        'lecture_session': ['session_number', 'contents', 'other_info', 'updated_at'],
        'lecture_session_instructor': None,  # 更新しない
        'syllabus_instructor': None,  # 更新しない
        'syllabus_book': ['role', 'note'],
        'grading_criterion': ['ratio', 'note'],
        'subject_attribute': None,  # 更新しない
        'subject': ['updated_at'],
        'subject_syllabus': ['updated_at'],
        'subject_attribute_value': ['value', 'updated_at'],
        'syllabus_study_system': ['updated_at']
    }

    # ON CONFLICT句を生成
    conflict_cols = conflict_columns.get(table_name, [])
    update_cols = update_columns.get(table_name, [])
    
    if not conflict_cols:
        return f"""-- {table_name} テーブルへのデータ挿入
INSERT INTO {table_name} (
    {columns_str}
) VALUES
{values_str};
"""
    
    conflict_str = ', '.join(conflict_cols)
    
    # update_colsがNoneの場合はON CONFLICT DO NOTHINGを使用
    if update_cols is None:
        update_str = "DO NOTHING"
    # update_colsが空の場合はupdated_atのみを更新
    elif not update_cols:
        update_str = "DO NOTHING"
    else:
        update_str = ',\n    '.join([f"{col} = EXCLUDED.{col}" for col in update_cols if col != 'updated_at'])
        if 'updated_at' in columns:
            update_str += ",\n    updated_at = CURRENT_TIMESTAMP"

    sql = f"""-- {table_name} テーブルへのデータ挿入
INSERT INTO {table_name} (
    {columns_str}
) VALUES
{values_str}
ON CONFLICT ({conflict_str}) {update_str};
"""
    return sql

def generate_table_definitions():
    """テーブル定義のSQLを生成する"""
    table_definitions = {
        'class': """
CREATE TABLE IF NOT EXISTS class (
    class_id INTEGER PRIMARY KEY,
    class_name TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);""",
        'subclass': """
CREATE TABLE IF NOT EXISTS subclass (
    subclass_id INTEGER PRIMARY KEY,
    subclass_name TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);""",
        'faculty': """
CREATE TABLE IF NOT EXISTS faculty (
    faculty_id INTEGER PRIMARY KEY,
    faculty_name TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);""",
        'subject_name': """
CREATE TABLE IF NOT EXISTS subject_name (
    subject_name_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);""",
        'instructor': """
CREATE TABLE IF NOT EXISTS instructor (
    instructor_id INTEGER PRIMARY KEY,
    instructor_code TEXT NOT NULL UNIQUE,
    last_name TEXT NOT NULL,
    first_name TEXT NOT NULL,
    last_name_kana TEXT,
    first_name_kana TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);""",
        'book': """
CREATE TABLE IF NOT EXISTS book (
    book_id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    publisher TEXT,
    price INTEGER,
    isbn TEXT UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);""",
        'book_author': """
CREATE TABLE IF NOT EXISTS book_author (
    book_author_id INTEGER PRIMARY KEY,
    book_id INTEGER NOT NULL REFERENCES book(book_id) ON DELETE CASCADE,
    author_name TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);""",
        'syllabus_master': """
CREATE TABLE IF NOT EXISTS syllabus_master (
    syllabus_id INTEGER PRIMARY KEY,
    syllabus_code TEXT NOT NULL,
    syllabus_year INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    UNIQUE(syllabus_code, syllabus_year)
);""",
        'syllabus': """
CREATE TABLE IF NOT EXISTS syllabus (
    syllabus_id INTEGER PRIMARY KEY REFERENCES syllabus_master(syllabus_id) ON DELETE CASCADE,
    subject_name_id INTEGER NOT NULL REFERENCES subject_name(subject_name_id) ON DELETE RESTRICT,
    subtitle TEXT,
    term TEXT NOT NULL,
    campus TEXT NOT NULL,
    credits INTEGER NOT NULL,
    goals TEXT,
    summary TEXT,
    attainment TEXT,
    methods TEXT,
    outside_study TEXT,
    notes TEXT,
    remarks TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);""",
        'subject_grade': """
CREATE TABLE IF NOT EXISTS subject_grade (
    id INTEGER PRIMARY KEY,
    syllabus_id INTEGER NOT NULL REFERENCES syllabus_master(syllabus_id) ON DELETE CASCADE,
    grade TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    UNIQUE(syllabus_id, grade)
);""",
        'lecture_time': """
CREATE TABLE IF NOT EXISTS lecture_time (
    id INTEGER PRIMARY KEY,
    syllabus_id INTEGER NOT NULL REFERENCES syllabus_master(syllabus_id) ON DELETE CASCADE,
    day_of_week TEXT NOT NULL,
    period SMALLINT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);""",
        'lecture_session': """
CREATE TABLE IF NOT EXISTS lecture_session (
    lecture_session_id INTEGER PRIMARY KEY,
    syllabus_id INTEGER NOT NULL REFERENCES syllabus_master(syllabus_id) ON DELETE CASCADE,
    session_number INTEGER NOT NULL,
    contents TEXT,
    other_info TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);""",
        'lecture_session_instructor': """
CREATE TABLE IF NOT EXISTS lecture_session_instructor (
    id INTEGER PRIMARY KEY,
    lecture_session_id INTEGER NOT NULL REFERENCES lecture_session(lecture_session_id) ON DELETE CASCADE,
    instructor_id INTEGER NOT NULL REFERENCES instructor(instructor_id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);""",
        'syllabus_instructor': """
CREATE TABLE IF NOT EXISTS syllabus_instructor (
    id INTEGER PRIMARY KEY,
    syllabus_id INTEGER NOT NULL REFERENCES syllabus_master(syllabus_id) ON DELETE CASCADE,
    instructor_id INTEGER NOT NULL REFERENCES instructor(instructor_id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);""",
        'syllabus_book': """
CREATE TABLE IF NOT EXISTS syllabus_book (
    id INTEGER PRIMARY KEY,
    syllabus_id INTEGER NOT NULL REFERENCES syllabus_master(syllabus_id) ON DELETE CASCADE,
    book_id INTEGER NOT NULL REFERENCES book(book_id) ON DELETE CASCADE,
    role TEXT NOT NULL,
    note TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);""",
        'grading_criterion': """
CREATE TABLE IF NOT EXISTS grading_criterion (
    id INTEGER PRIMARY KEY,
    syllabus_id INTEGER NOT NULL REFERENCES syllabus_master(syllabus_id) ON DELETE CASCADE,
    criteria_type TEXT NOT NULL,
    ratio INTEGER,
    note TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);""",
        'subject_attribute': """
CREATE TABLE IF NOT EXISTS subject_attribute (
    attribute_id INTEGER PRIMARY KEY,
    attribute_name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);""",
        'subject': """
CREATE TABLE IF NOT EXISTS subject (
    subject_id INTEGER PRIMARY KEY,
    subject_name_id INTEGER NOT NULL REFERENCES subject_name(subject_name_id) ON DELETE RESTRICT,
    faculty_id INTEGER NOT NULL REFERENCES faculty(faculty_id) ON DELETE RESTRICT,
    class_id INTEGER NOT NULL REFERENCES class(class_id) ON DELETE RESTRICT,
    subclass_id INTEGER REFERENCES subclass(subclass_id) ON DELETE RESTRICT,
    curriculum_year INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    UNIQUE(subject_name_id, faculty_id, class_id, subclass_id, curriculum_year)
);""",
        'subject_syllabus': """
CREATE TABLE IF NOT EXISTS subject_syllabus (
    id INTEGER PRIMARY KEY,
    subject_id INTEGER NOT NULL REFERENCES subject(subject_id) ON DELETE CASCADE,
    syllabus_id INTEGER NOT NULL REFERENCES syllabus_master(syllabus_id) ON DELETE RESTRICT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    UNIQUE(subject_id, syllabus_id)
);""",
        'subject_attribute_value': """
CREATE TABLE IF NOT EXISTS subject_attribute_value (
    id INTEGER PRIMARY KEY,
    subject_id INTEGER NOT NULL REFERENCES subject(subject_id) ON DELETE CASCADE,
    attribute_id INTEGER NOT NULL REFERENCES subject_attribute(attribute_id) ON DELETE RESTRICT,
    value TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    UNIQUE(subject_id, attribute_id)
);""",
        'syllabus_study_system': """
CREATE TABLE IF NOT EXISTS syllabus_study_system (
    id INTEGER PRIMARY KEY,
    source_syllabus_id INTEGER NOT NULL REFERENCES syllabus_master(syllabus_id) ON DELETE CASCADE,
    target TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    UNIQUE(source_syllabus_id, target)
);"""
    }
    
    # インデックス定義
    index_definitions = {
        'class': """
CREATE INDEX IF NOT EXISTS idx_class_name ON class(class_name);""",
        'faculty': """
CREATE INDEX IF NOT EXISTS idx_faculty_name ON faculty(faculty_name);""",
        'subject_name': """
CREATE UNIQUE INDEX IF NOT EXISTS idx_subject_name ON subject_name(name);""",
        'subject': """
CREATE INDEX IF NOT EXISTS idx_subject_subject_name ON subject(subject_name_id);
CREATE INDEX IF NOT EXISTS idx_subject_class ON subject(class_id);
CREATE INDEX IF NOT EXISTS idx_subject_faculty ON subject(faculty_id);
CREATE INDEX IF NOT EXISTS idx_subject_curriculum_year ON subject(curriculum_year);""",
        'subject_syllabus': """
CREATE INDEX IF NOT EXISTS idx_subject_syllabus_subject ON subject_syllabus(subject_id);
CREATE INDEX IF NOT EXISTS idx_subject_syllabus_syllabus ON subject_syllabus(syllabus_id);""",
        'subject_attribute_value': """
CREATE INDEX IF NOT EXISTS idx_subject_attribute_value_subject ON subject_attribute_value(subject_id);
CREATE INDEX IF NOT EXISTS idx_subject_attribute_value_attribute ON subject_attribute_value(attribute_id);""",
        'instructor': """
CREATE INDEX IF NOT EXISTS idx_instructor_name ON instructor(last_name, first_name);
CREATE INDEX IF NOT EXISTS idx_instructor_name_kana ON instructor(last_name_kana, first_name_kana);""",
        'book': """
CREATE INDEX IF NOT EXISTS idx_book_title ON book(title);""",
        'book_author': """
CREATE INDEX IF NOT EXISTS idx_book_author_book ON book_author(book_id);
CREATE INDEX IF NOT EXISTS idx_book_author_name ON book_author(author_name);""",
        'syllabus_master': """
CREATE INDEX IF NOT EXISTS idx_syllabus_master_code ON syllabus_master(syllabus_code);
CREATE INDEX IF NOT EXISTS idx_syllabus_master_year ON syllabus_master(syllabus_year);""",
        'syllabus': """
CREATE INDEX IF NOT EXISTS idx_syllabus_term ON syllabus(term);
CREATE INDEX IF NOT EXISTS idx_syllabus_campus ON syllabus(campus);
CREATE INDEX IF NOT EXISTS idx_syllabus_subject_name ON syllabus(subject_name_id);""",
        'lecture_time': """
CREATE INDEX IF NOT EXISTS idx_lecture_time_day_period ON lecture_time(day_of_week, period);
CREATE INDEX IF NOT EXISTS idx_lecture_time_syllabus ON lecture_time(syllabus_id);""",
        'lecture_session': """
CREATE INDEX IF NOT EXISTS idx_lecture_session_syllabus ON lecture_session(syllabus_id);
CREATE INDEX IF NOT EXISTS idx_lecture_session_number ON lecture_session(session_number);""",
        'lecture_session_instructor': """
CREATE INDEX IF NOT EXISTS idx_lecture_session_instructor_session ON lecture_session_instructor(lecture_session_id);
CREATE INDEX IF NOT EXISTS idx_lecture_session_instructor_instructor ON lecture_session_instructor(instructor_id);""",
        'syllabus_instructor': """
CREATE INDEX IF NOT EXISTS idx_syllabus_instructor_syllabus ON syllabus_instructor(syllabus_id);
CREATE INDEX IF NOT EXISTS idx_syllabus_instructor_instructor ON syllabus_instructor(instructor_id);""",
        'syllabus_book': """
CREATE INDEX IF NOT EXISTS idx_syllabus_book_syllabus ON syllabus_book(syllabus_id);
CREATE INDEX IF NOT EXISTS idx_syllabus_book_book ON syllabus_book(book_id);""",
        'grading_criterion': """
CREATE INDEX IF NOT EXISTS idx_grading_criterion_type ON grading_criterion(criteria_type);
CREATE INDEX IF NOT EXISTS idx_grading_criterion_syllabus ON grading_criterion(syllabus_id);""",
        'syllabus_study_system': """
CREATE INDEX IF NOT EXISTS idx_syllabus_study_system_source ON syllabus_study_system(source_syllabus_id);
CREATE INDEX IF NOT EXISTS idx_syllabus_study_system_target ON syllabus_study_system(target);""",
        'subject_grade': """
CREATE INDEX IF NOT EXISTS idx_subject_grade_grade ON subject_grade(grade);
CREATE INDEX IF NOT EXISTS idx_subject_grade_syllabus ON subject_grade(syllabus_id);"""
    }
    
    sql = []
    for table_name in table_definitions:
        sql.append(table_definitions[table_name])
        if table_name in index_definitions:
            sql.append(index_definitions[table_name])
    
    return '\n\n'.join(sql)

def move_json_to_registered(json_dir: Path, table_name: str) -> None:
    """JSONファイルをregisteredディレクトリに移動する"""
    add_dir = json_dir.parent / 'add'
    if not add_dir.exists():
        print(f"No add directory found for {table_name}")
        return

    # registeredディレクトリが存在しない場合は作成
    json_dir.mkdir(parents=True, exist_ok=True)

    # addディレクトリ内のJSONファイルを移動
    for json_file in add_dir.glob('*.json'):
        try:
            # 移動先のファイルパスを生成
            dest_file = json_dir / json_file.name
            # ファイルを移動
            json_file.rename(dest_file)
            print(f"Moved {json_file} to {dest_file}")
        except Exception as e:
            print(f"Error moving {json_file}: {str(e)}")

def generate_migration():
    """マイグレーションファイルを生成"""
    try:
        # プロジェクトルートからの相対パス
        project_root = Path(__file__).parent.parent.parent.parent
        
        # 処理対象のディレクトリとテーブル名のマッピング
        targets = [
            # 基本マスターテーブル
            {
                'json_dir': project_root / 'updates' / 'class',
                'table_name': 'class',
                'source': 'syllabus_search'
            },
            {
                'json_dir': project_root / 'updates' / 'subclass',
                'table_name': 'subclass',
                'source': 'syllabus_search'
            },
            {
                'json_dir': project_root / 'updates' / 'faculty',
                'table_name': 'faculty',
                'source': 'syllabus_search'
            },
            {
                'json_dir': project_root / 'updates' / 'subject_name',
                'table_name': 'subject_name',
                'source': 'syllabus_search'
            },
            # 中間テーブル
            {
                'json_dir': project_root / 'updates' / 'subject',
                'table_name': 'subject',
                'source': 'syllabus_search'
            },
            {
                'json_dir': project_root / 'updates' / 'instructor',
                'table_name': 'instructor',
                'source': 'web_syllabus'
            },
            {
                'json_dir': project_root / 'updates' / 'book',
                'table_name': 'book',
                'source': 'web_syllabus'
            },
            # シラバス関連テーブル
            {
                'json_dir': project_root / 'updates' / 'syllabus',
                'table_name': 'syllabus',
                'source': 'web_syllabus'
            },
            {
                'json_dir': project_root / 'updates' / 'lecture_session',
                'table_name': 'lecture_session',
                'source': 'web_syllabus'
            },
            {
                'json_dir': project_root / 'updates' / 'syllabus_instructor',
                'table_name': 'syllabus_instructor',
                'source': 'web_syllabus'
            },
            {
                'json_dir': project_root / 'updates' / 'syllabus_book',
                'table_name': 'syllabus_book',
                'source': 'web_syllabus'
            },
            {
                'json_dir': project_root / 'updates' / 'grading_criterion',
                'table_name': 'grading_criterion',
                'source': 'web_syllabus'
            }
        ]
        
        # マイグレーションファイルの出力先ディレクトリ
        migrations_dir = project_root / 'docker' / 'postgresql' / 'init' / 'migrations'
        migrations_dir.mkdir(parents=True, exist_ok=True)
        
        # 現在のタイムスタンプを取得
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        
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
            
            # マイグレーションファイル生成が成功したら、JSONファイルを移動
            move_json_to_registered(json_dir, table_name)
        
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
    class_id INTEGER PRIMARY KEY,
    class_name TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 科目小区分テーブル
CREATE TABLE IF NOT EXISTS subclass (
    subclass_id INTEGER PRIMARY KEY,
    subclass_name TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 開講学部・課程テーブル
CREATE TABLE IF NOT EXISTS faculty (
    faculty_id INTEGER PRIMARY KEY,
    faculty_name TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 科目名マスタテーブル
CREATE TABLE IF NOT EXISTS subject_name (
    subject_name_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 教員テーブル
CREATE TABLE IF NOT EXISTS instructor (
    instructor_id INTEGER PRIMARY KEY,
    instructor_code TEXT NOT NULL UNIQUE,
    last_name TEXT NOT NULL,
    first_name TEXT NOT NULL,
    last_name_kana TEXT,
    first_name_kana TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- 書籍テーブル
CREATE TABLE IF NOT EXISTS book (
    book_id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    publisher TEXT,
    price INTEGER,
    isbn TEXT UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- 書籍著者テーブル
CREATE TABLE IF NOT EXISTS book_author (
    book_author_id INTEGER PRIMARY KEY,
    book_id INTEGER NOT NULL REFERENCES book(book_id) ON DELETE CASCADE,
    author_name TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- シラバスマスタテーブル
CREATE TABLE IF NOT EXISTS syllabus_master (
    syllabus_id INTEGER PRIMARY KEY,
    syllabus_code TEXT NOT NULL,
    syllabus_year INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    UNIQUE(syllabus_code, syllabus_year)
);

-- シラバス情報テーブル
CREATE TABLE IF NOT EXISTS syllabus (
    syllabus_id INTEGER PRIMARY KEY REFERENCES syllabus_master(syllabus_id) ON DELETE CASCADE,
    subject_name_id INTEGER NOT NULL REFERENCES subject_name(subject_name_id) ON DELETE RESTRICT,
    subtitle TEXT,
    term TEXT NOT NULL,
    campus TEXT NOT NULL,
    credits INTEGER NOT NULL,
    goals TEXT,
    summary TEXT,
    attainment TEXT,
    methods TEXT,
    outside_study TEXT,
    notes TEXT,
    remarks TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- 科目基本情報テーブル
CREATE TABLE IF NOT EXISTS subject (
    subject_id INTEGER PRIMARY KEY,
    subject_name_id INTEGER NOT NULL REFERENCES subject_name(subject_name_id),
    faculty_id INTEGER NOT NULL REFERENCES faculty(faculty_id),
    class_id INTEGER NOT NULL REFERENCES class(class_id),
    subclass_id INTEGER REFERENCES subclass(subclass_id),
    curriculum_year INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    UNIQUE(subject_name_id, faculty_id, class_id, subclass_id, curriculum_year)
);

-- 科目シラバス関連テーブル
CREATE TABLE IF NOT EXISTS subject_syllabus (
    id INTEGER PRIMARY KEY,
    subject_id INTEGER NOT NULL REFERENCES subject(subject_id) ON DELETE CASCADE,
    syllabus_id INTEGER NOT NULL REFERENCES syllabus_master(syllabus_id) ON DELETE RESTRICT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    UNIQUE(subject_id, syllabus_id)
);

-- 科目属性テーブル
CREATE TABLE IF NOT EXISTS subject_attribute (
    attribute_id INTEGER PRIMARY KEY,
    attribute_name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 科目属性値テーブル
CREATE TABLE IF NOT EXISTS subject_attribute_value (
    id INTEGER PRIMARY KEY,
    subject_id INTEGER NOT NULL REFERENCES subject(subject_id) ON DELETE CASCADE,
    attribute_id INTEGER NOT NULL REFERENCES subject_attribute(attribute_id) ON DELETE RESTRICT,
    value TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    UNIQUE(subject_id, attribute_id)
);

-- 講義時間テーブル
CREATE TABLE IF NOT EXISTS lecture_time (
    id INTEGER PRIMARY KEY,
    syllabus_id INTEGER NOT NULL REFERENCES syllabus_master(syllabus_id) ON DELETE CASCADE,
    day_of_week TEXT NOT NULL,
    period SMALLINT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- 講義セッションテーブル
CREATE TABLE IF NOT EXISTS lecture_session (
    lecture_session_id INTEGER PRIMARY KEY,
    syllabus_id INTEGER NOT NULL REFERENCES syllabus_master(syllabus_id) ON DELETE CASCADE,
    session_number INTEGER NOT NULL,
    contents TEXT,
    other_info TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- 講義セッション教員テーブル
CREATE TABLE IF NOT EXISTS lecture_session_instructor (
    id INTEGER PRIMARY KEY,
    lecture_session_id INTEGER NOT NULL REFERENCES lecture_session(lecture_session_id) ON DELETE CASCADE,
    instructor_id INTEGER NOT NULL REFERENCES instructor(instructor_id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- シラバス教員関連テーブル
CREATE TABLE IF NOT EXISTS syllabus_instructor (
    id INTEGER PRIMARY KEY,
    syllabus_id INTEGER NOT NULL REFERENCES syllabus_master(syllabus_id) ON DELETE CASCADE,
    instructor_id INTEGER NOT NULL REFERENCES instructor(instructor_id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- シラバス教科書関連テーブル
CREATE TABLE IF NOT EXISTS syllabus_book (
    id INTEGER PRIMARY KEY,
    syllabus_id INTEGER NOT NULL REFERENCES syllabus_master(syllabus_id) ON DELETE CASCADE,
    book_id INTEGER NOT NULL REFERENCES book(book_id) ON DELETE CASCADE,
    role TEXT NOT NULL,
    note TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 成績評価基準テーブル
CREATE TABLE IF NOT EXISTS grading_criterion (
    id INTEGER PRIMARY KEY,
    syllabus_id INTEGER NOT NULL REFERENCES syllabus_master(syllabus_id) ON DELETE CASCADE,
    criteria_type TEXT NOT NULL,
    ratio INTEGER,
    note TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- シラバス学習システムテーブル
CREATE TABLE IF NOT EXISTS syllabus_study_system (
    id INTEGER PRIMARY KEY,
    source_syllabus_id INTEGER NOT NULL REFERENCES syllabus_master(syllabus_id) ON DELETE CASCADE,
    target TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    UNIQUE(source_syllabus_id, target)
);

-- 科目履修可能学年テーブル
CREATE TABLE IF NOT EXISTS subject_grade (
    id INTEGER PRIMARY KEY,
    syllabus_id INTEGER NOT NULL REFERENCES syllabus_master(syllabus_id) ON DELETE CASCADE,
    grade TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    UNIQUE(syllabus_id, grade)
);

-- インデックスの作成
CREATE INDEX IF NOT EXISTS idx_class_name ON class(class_name);
CREATE INDEX IF NOT EXISTS idx_faculty_name ON faculty(faculty_name);
CREATE INDEX IF NOT EXISTS idx_subject_subject_name ON subject(subject_name_id);
CREATE INDEX IF NOT EXISTS idx_subject_class ON subject(class_id);
CREATE INDEX IF NOT EXISTS idx_subject_faculty ON subject(faculty_id);
CREATE INDEX IF NOT EXISTS idx_subject_curriculum_year ON subject(curriculum_year);
CREATE INDEX IF NOT EXISTS idx_subject_syllabus_subject ON subject_syllabus(subject_id);
CREATE INDEX IF NOT EXISTS idx_subject_syllabus_syllabus ON subject_syllabus(syllabus_id);
CREATE INDEX IF NOT EXISTS idx_subject_attribute_value_subject ON subject_attribute_value(subject_id);
CREATE INDEX IF NOT EXISTS idx_subject_attribute_value_attribute ON subject_attribute_value(attribute_id);
CREATE INDEX IF NOT EXISTS idx_instructor_name ON instructor(last_name, first_name);
CREATE INDEX IF NOT EXISTS idx_instructor_name_kana ON instructor(last_name_kana, first_name_kana);
CREATE INDEX IF NOT EXISTS idx_book_title ON book(title);
CREATE INDEX IF NOT EXISTS idx_book_author_book ON book_author(book_id);
CREATE INDEX IF NOT EXISTS idx_book_author_name ON book_author(author_name);
CREATE INDEX IF NOT EXISTS idx_syllabus_master_code ON syllabus_master(syllabus_code);
CREATE INDEX IF NOT EXISTS idx_syllabus_master_year ON syllabus_master(syllabus_year);
CREATE INDEX IF NOT EXISTS idx_syllabus_term ON syllabus(term);
CREATE INDEX IF NOT EXISTS idx_syllabus_campus ON syllabus(campus);
CREATE INDEX IF NOT EXISTS idx_syllabus_subject_name ON syllabus(subject_name_id);
CREATE INDEX IF NOT EXISTS idx_lecture_time_day_period ON lecture_time(day_of_week, period);
CREATE INDEX IF NOT EXISTS idx_lecture_time_syllabus ON lecture_time(syllabus_id);
CREATE INDEX IF NOT EXISTS idx_lecture_session_syllabus ON lecture_session(syllabus_id);
CREATE INDEX IF NOT EXISTS idx_lecture_session_number ON lecture_session(session_number);
CREATE INDEX IF NOT EXISTS idx_lecture_session_instructor_session ON lecture_session_instructor(lecture_session_id);
CREATE INDEX IF NOT EXISTS idx_lecture_session_instructor_instructor ON lecture_session_instructor(instructor_id);
CREATE INDEX IF NOT EXISTS idx_syllabus_instructor_syllabus ON syllabus_instructor(syllabus_id);
CREATE INDEX IF NOT EXISTS idx_syllabus_instructor_instructor ON syllabus_instructor(instructor_id);
CREATE INDEX IF NOT EXISTS idx_syllabus_book_syllabus ON syllabus_book(syllabus_id);
CREATE INDEX IF NOT EXISTS idx_syllabus_book_book ON syllabus_book(book_id);
CREATE INDEX IF NOT EXISTS idx_grading_criterion_type ON grading_criterion(criteria_type);
CREATE INDEX IF NOT EXISTS idx_grading_criterion_syllabus ON grading_criterion(syllabus_id);
CREATE INDEX IF NOT EXISTS idx_syllabus_study_system_source ON syllabus_study_system(source_syllabus_id);
CREATE INDEX IF NOT EXISTS idx_syllabus_study_system_target ON syllabus_study_system(target);
CREATE INDEX IF NOT EXISTS idx_subject_grade_grade ON subject_grade(grade);
CREATE INDEX IF NOT EXISTS idx_subject_grade_syllabus ON subject_grade(syllabus_id);
""")
    
    return '\n'.join(sql)

if __name__ == '__main__':
    generate_migration() 