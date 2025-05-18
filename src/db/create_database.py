import sqlite3
import os
from pathlib import Path

def init_database():
    """SQLiteデータベースを初期化"""
    # データベースファイルのパス
    db_dir = Path("db")
    db_dir.mkdir(parents=True, exist_ok=True)
    
    db_path = db_dir / "syllabus.db"

    # データベースの初期化
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # テーブルの作成
    # subject（科目基本情報）テーブル
    cur.execute("""
    CREATE TABLE IF NOT EXISTS subject (
        subject_code TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        class_name TEXT NOT NULL,
        subclass_name TEXT,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP
    )
    """)

    # syllabus（シラバス情報）テーブル
    cur.execute("""
    CREATE TABLE IF NOT EXISTS syllabus (
        subject_code TEXT PRIMARY KEY,
        year INTEGER NOT NULL,
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
        lecture_code TEXT NOT NULL,
        summary TEXT,
        goals TEXT,
        methods TEXT,
        outside_study TEXT,
        notes TEXT,
        remarks TEXT,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP,
        FOREIGN KEY (subject_code) REFERENCES subject(subject_code) ON DELETE CASCADE
    )
    """)

    # syllabus_time（講義時間）テーブル
    cur.execute("""
    CREATE TABLE IF NOT EXISTS syllabus_time (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_code TEXT NOT NULL,
        day_of_week TINYINT NOT NULL,
        period TINYINT NOT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (subject_code) REFERENCES subject(subject_code) ON DELETE CASCADE
    )
    """)

    # instructor（教員）テーブル
    cur.execute("""
    CREATE TABLE IF NOT EXISTS instructor (
        instructor_code TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        name_kana TEXT,
        name_en TEXT,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP
    )
    """)

    # syllabus_instructor（シラバス-教員関連）テーブル
    cur.execute("""
    CREATE TABLE IF NOT EXISTS syllabus_instructor (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_code TEXT NOT NULL,
        instructor_code TEXT NOT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (subject_code) REFERENCES subject(subject_code) ON DELETE CASCADE,
        FOREIGN KEY (instructor_code) REFERENCES instructor(instructor_code) ON DELETE CASCADE
    )
    """)

    # lecture_session（講義計画）テーブル
    cur.execute("""
    CREATE TABLE IF NOT EXISTS lecture_session (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_code TEXT NOT NULL,
        session_number INTEGER NOT NULL,
        description TEXT NOT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (subject_code) REFERENCES subject(subject_code) ON DELETE CASCADE
    )
    """)

    # book（書籍）テーブル
    cur.execute("""
    CREATE TABLE IF NOT EXISTS book (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        author TEXT,
        title TEXT NOT NULL,
        publisher TEXT,
        price INTEGER,
        isbn TEXT UNIQUE,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP
    )
    """)

    # syllabus_textbook（シラバス-教科書関連）テーブル
    cur.execute("""
    CREATE TABLE IF NOT EXISTS syllabus_textbook (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_code TEXT NOT NULL,
        book_id INTEGER NOT NULL,
        note TEXT,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (subject_code) REFERENCES subject(subject_code) ON DELETE CASCADE,
        FOREIGN KEY (book_id) REFERENCES book(id) ON DELETE CASCADE
    )
    """)

    # syllabus_reference（シラバス-参考文献関連）テーブル
    cur.execute("""
    CREATE TABLE IF NOT EXISTS syllabus_reference (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_code TEXT NOT NULL,
        book_id INTEGER NOT NULL,
        note TEXT,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (subject_code) REFERENCES subject(subject_code) ON DELETE CASCADE,
        FOREIGN KEY (book_id) REFERENCES book(id) ON DELETE CASCADE
    )
    """)

    # grading_criterion（成績評価基準）テーブル
    cur.execute("""
    CREATE TABLE IF NOT EXISTS grading_criterion (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_code TEXT NOT NULL,
        criteria_type VARCHAR(4) NOT NULL CHECK (criteria_type IN ('平常', '小テ', '定期', 'レポ', '他', '自由')),
        ratio TINYINT,
        note TEXT,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (subject_code) REFERENCES subject(subject_code) ON DELETE CASCADE
    )
    """)

    # syllabus_faculty（シラバス-学部/課程関連）テーブル
    cur.execute("""
    CREATE TABLE IF NOT EXISTS syllabus_faculty (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_code TEXT NOT NULL,
        faculty VARCHAR(60) NOT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (subject_code) REFERENCES subject(subject_code) ON DELETE CASCADE
    )
    """)

    # subject_requirement（科目要件・属性）テーブル
    cur.execute("""
    CREATE TABLE IF NOT EXISTS subject_requirement (
        subject_code TEXT PRIMARY KEY,
        requirement_type TEXT NOT NULL,
        applied_science_available BOOLEAN NOT NULL,
        graduation_credit_limit BOOLEAN NOT NULL,
        year_restriction BOOLEAN NOT NULL,
        first_year_only BOOLEAN NOT NULL,
        up_to_second_year BOOLEAN NOT NULL,
        guidance_required BOOLEAN NOT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP,
        FOREIGN KEY (subject_code) REFERENCES subject(subject_code) ON DELETE CASCADE
    )
    """)

    # subject_program（科目-学習プログラム関連）テーブル
    cur.execute("""
    CREATE TABLE IF NOT EXISTS subject_program (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_code TEXT NOT NULL,
        program_code TEXT NOT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (subject_code) REFERENCES subject(subject_code) ON DELETE CASCADE
    )
    """)

    # インデックスの作成
    # subject テーブルのインデックス
    cur.execute("CREATE INDEX IF NOT EXISTS idx_subject_name ON subject(name)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_subject_class ON subject(class_name)")

    # syllabus テーブルのインデックス
    cur.execute("CREATE INDEX IF NOT EXISTS idx_syllabus_year ON syllabus(year)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_syllabus_term ON syllabus(term)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_syllabus_campus ON syllabus(campus)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_syllabus_grades ON syllabus(grade_b1, grade_b2, grade_b3, grade_b4, grade_m1, grade_m2, grade_d1, grade_d2, grade_d3)")

    # syllabus_time テーブルのインデックス
    cur.execute("CREATE INDEX IF NOT EXISTS idx_syllabus_time_day_period ON syllabus_time(day_of_week, period)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_syllabus_time_subject ON syllabus_time(subject_code)")

    # instructor テーブルのインデックス
    cur.execute("CREATE INDEX IF NOT EXISTS idx_instructor_name ON instructor(name)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_instructor_name_kana ON instructor(name_kana)")

    # syllabus_instructor テーブルのインデックス
    cur.execute("CREATE INDEX IF NOT EXISTS idx_syllabus_instructor_subject ON syllabus_instructor(subject_code)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_syllabus_instructor_instructor ON syllabus_instructor(instructor_code)")

    # lecture_session テーブルのインデックス
    cur.execute("CREATE INDEX IF NOT EXISTS idx_lecture_session_subject_num ON lecture_session(subject_code, session_number)")

    # book テーブルのインデックス
    cur.execute("CREATE INDEX IF NOT EXISTS idx_book_title ON book(title)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_book_author ON book(author)")

    # syllabus_textbook テーブルのインデックス
    cur.execute("CREATE INDEX IF NOT EXISTS idx_syllabus_textbook_subject ON syllabus_textbook(subject_code)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_syllabus_textbook_book ON syllabus_textbook(book_id)")

    # syllabus_reference テーブルのインデックス
    cur.execute("CREATE INDEX IF NOT EXISTS idx_syllabus_reference_subject ON syllabus_reference(subject_code)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_syllabus_reference_book ON syllabus_reference(book_id)")

    # grading_criterion テーブルのインデックス
    cur.execute("CREATE INDEX IF NOT EXISTS idx_grading_criterion_type ON grading_criterion(criteria_type)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_grading_criterion_subject_type ON grading_criterion(subject_code, criteria_type)")

    # syllabus_faculty テーブルのインデックス
    cur.execute("CREATE INDEX IF NOT EXISTS idx_syllabus_faculty_subject ON syllabus_faculty(subject_code)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_syllabus_faculty_faculty ON syllabus_faculty(faculty)")

    # subject_requirement テーブルのインデックス
    cur.execute("CREATE INDEX IF NOT EXISTS idx_requirement_type ON subject_requirement(requirement_type)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_requirement_restrictions ON subject_requirement(applied_science_available, graduation_credit_limit, year_restriction)")

    # subject_program テーブルのインデックス
    cur.execute("CREATE INDEX IF NOT EXISTS idx_subject_program_subject ON subject_program(subject_code)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_subject_program_program ON subject_program(program_code)")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_database()
    print("データベースの初期化が完了しました。") 