-- ========== ユーザーの作成 ==========

-- dev_user: syllabus_db 読み取り専用
CREATE USER dev_user WITH PASSWORD 'dev_pass';

-- app_user: syllabus_db 読み取り専用
CREATE USER app_user WITH PASSWORD 'app_pass';

-- ========== データベースの作成 ==========

DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'syllabus_db') THEN
        CREATE DATABASE syllabus_db OWNER postgres;
    END IF;
END
$$;

-- ========== 権限付与 ==========

-- データベース権限
GRANT ALL PRIVILEGES ON DATABASE syllabus_db TO dev_user;
GRANT CONNECT ON DATABASE syllabus_db TO app_user;

-- 接続切替（syllabus_db）
\connect syllabus_db

-- スキーマ権限
GRANT CONNECT ON DATABASE syllabus_db TO dev_user, app_user;
GRANT USAGE ON SCHEMA public TO dev_user, app_user;
GRANT ALL PRIVILEGES ON SCHEMA public TO dev_user;

-- テーブルとシーケンスの権限
GRANT SELECT ON ALL TABLES IN SCHEMA public TO dev_user, app_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO dev_user, app_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO dev_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO dev_user;

-- デフォルト権限の設定
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT ON TABLES TO dev_user, app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT USAGE, SELECT ON SEQUENCES TO dev_user, app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT ALL PRIVILEGES ON TABLES TO dev_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT ALL PRIVILEGES ON SEQUENCES TO dev_user;

-- カタログ参照権限
GRANT SELECT ON pg_catalog.pg_tables TO dev_user, app_user;
GRANT SELECT ON information_schema.tables TO dev_user, app_user;

-- ========== テーブル作成（syllabus_db） ==========

-- class（科目区分）
CREATE TABLE IF NOT EXISTS class (
    class_id SERIAL PRIMARY KEY,
    class_name TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- subclass（科目小区分）
CREATE TABLE IF NOT EXISTS subclass (
    subclass_id SERIAL PRIMARY KEY,
    subclass_name TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- class_note（科目区分の備考）
CREATE TABLE IF NOT EXISTS class_note (
    class_note_id SERIAL PRIMARY KEY,
    class_note TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- faculty（開講学部・課程）
CREATE TABLE IF NOT EXISTS faculty (
    faculty_id SERIAL PRIMARY KEY,
    faculty_name TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE INDEX idx_faculty_name ON faculty(faculty_name);

-- subject_name（科目名マスタ）
CREATE TABLE IF NOT EXISTS subject_name (
    subject_name_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE UNIQUE INDEX idx_subject_name ON subject_name(name);

-- syllabus（シラバス情報）
CREATE TABLE IF NOT EXISTS syllabus (
    syllabus_code TEXT PRIMARY KEY,
    subject_name_id INTEGER NOT NULL REFERENCES subject_name(subject_name_id) ON DELETE RESTRICT,
    subtitle TEXT,
    term TEXT NOT NULL,
    grade_mask INTEGER NOT NULL,  -- ビットマスクで履修可能学年を表現
    campus TEXT NOT NULL,
    credits INTEGER NOT NULL,
    summary TEXT,
    goals TEXT,
    methods TEXT,
    outside_study TEXT,
    notes TEXT,
    remarks TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE INDEX idx_syllabus_term ON syllabus(term);
CREATE INDEX idx_syllabus_grade_mask ON syllabus(grade_mask);  -- ビットマスク用のインデックス
CREATE INDEX idx_syllabus_campus ON syllabus(campus);
CREATE INDEX idx_syllabus_subject_name ON syllabus(subject_name_id);

-- ビットマスクの定義をコメントとして追加
COMMENT ON COLUMN syllabus.grade_mask IS '履修可能学年のビットマスク
B1: 1, B2: 2, B3: 4, B4: 8
M1: 16, M2: 32
D1: 64, D2: 128, D3: 256
例：学部1-2年生のみ履修可能 = 3 (1 + 2)
例：学部3-4年生と修士1年生が履修可能 = 28 (4 + 8 + 16)';

-- subject（科目基本情報）
CREATE TABLE IF NOT EXISTS subject (
    subject_id SERIAL PRIMARY KEY,
    syllabus_code TEXT NOT NULL,
    syllabus_year INTEGER NOT NULL,
    faculty_id INTEGER NOT NULL,
    class_id INTEGER NOT NULL,
    subclass_id INTEGER,
    class_note_id INTEGER,
    lecture_code TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (syllabus_code) REFERENCES syllabus(syllabus_code) ON DELETE RESTRICT,
    FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id) ON DELETE RESTRICT,
    FOREIGN KEY (class_id) REFERENCES class(class_id) ON DELETE RESTRICT,
    FOREIGN KEY (subclass_id) REFERENCES subclass(subclass_id) ON DELETE RESTRICT,
    FOREIGN KEY (class_note_id) REFERENCES class_note(class_note_id) ON DELETE RESTRICT
);

CREATE INDEX idx_subject_syllabus ON subject(syllabus_code);
CREATE INDEX idx_subject_class ON subject(class_id);
CREATE INDEX idx_subject_faculty ON subject(faculty_id);
CREATE UNIQUE INDEX idx_subject_unique ON subject(syllabus_code, syllabus_year, faculty_id, class_id, subclass_id, class_note_id);

-- instructor（教員）
CREATE TABLE IF NOT EXISTS instructor (
    instructor_code TEXT PRIMARY KEY,
    last_name TEXT NOT NULL,
    first_name TEXT NOT NULL,
    last_name_kana TEXT,
    first_name_kana TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE INDEX idx_instructor_name ON instructor(last_name, first_name);
CREATE INDEX idx_instructor_name_kana ON instructor(last_name_kana, first_name_kana);

-- book（書籍）
CREATE TABLE IF NOT EXISTS book (
    book_id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    publisher TEXT,
    price INTEGER,
    isbn TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE INDEX idx_book_title ON book(title);
CREATE UNIQUE INDEX idx_book_isbn ON book(isbn);

-- book_author（書籍著者）
CREATE TABLE IF NOT EXISTS book_author (
    book_author_id SERIAL PRIMARY KEY,
    book_id INTEGER NOT NULL,
    author_name TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES book(book_id) ON DELETE CASCADE
);

CREATE INDEX idx_book_author_book ON book_author(book_id);
CREATE INDEX idx_book_author_name ON book_author(author_name);

-- lecture_session（講義時間）
CREATE TABLE IF NOT EXISTS lecture_session (
    id SERIAL PRIMARY KEY,
    syllabus_code TEXT NOT NULL,
    syllabus_year INTEGER NOT NULL,
    day_of_week TEXT NOT NULL,
    period INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (syllabus_code) REFERENCES syllabus(syllabus_code) ON DELETE CASCADE
);

CREATE INDEX idx_lecture_session_day_period ON lecture_session(day_of_week, period);
CREATE INDEX idx_lecture_session_syllabus ON lecture_session(syllabus_code, syllabus_year);

-- syllabus_faculty（シラバス-学部課程関連）
CREATE TABLE IF NOT EXISTS syllabus_faculty (
    id SERIAL PRIMARY KEY,
    syllabus_code TEXT NOT NULL,
    faculty_id INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (syllabus_code) REFERENCES syllabus(syllabus_code) ON DELETE CASCADE,
    FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id) ON DELETE CASCADE
);

CREATE INDEX idx_syllabus_faculty_syllabus ON syllabus_faculty(syllabus_code);
CREATE INDEX idx_syllabus_faculty_faculty ON syllabus_faculty(faculty_id);

-- syllabus_instructor（シラバス-教員関連）
CREATE TABLE IF NOT EXISTS syllabus_instructor (
    id SERIAL PRIMARY KEY,
    syllabus_code TEXT NOT NULL,
    instructor_code TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (syllabus_code) REFERENCES syllabus(syllabus_code) ON DELETE CASCADE,
    FOREIGN KEY (instructor_code) REFERENCES instructor(instructor_code) ON DELETE CASCADE
);

CREATE INDEX idx_syllabus_instructor_syllabus ON syllabus_instructor(syllabus_code);
CREATE INDEX idx_syllabus_instructor_instructor ON syllabus_instructor(instructor_code);

-- syllabus_book（シラバス-教科書関連）
CREATE TABLE IF NOT EXISTS syllabus_book (
    id SERIAL PRIMARY KEY,
    syllabus_code TEXT NOT NULL,
    book_id INTEGER NOT NULL,
    role INTEGER NOT NULL,
    note TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (syllabus_code) REFERENCES syllabus(syllabus_code) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES book(book_id) ON DELETE CASCADE
);

CREATE INDEX idx_syllabus_book_syllabus ON syllabus_book(syllabus_code);
CREATE INDEX idx_syllabus_book_book ON syllabus_book(book_id);

-- grading_criterion（成績評価基準）
CREATE TABLE IF NOT EXISTS grading_criterion (
    id SERIAL PRIMARY KEY,
    syllabus_code TEXT NOT NULL,
    criteria_type TEXT NOT NULL,
    ratio INTEGER,
    note TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (syllabus_code) REFERENCES syllabus(syllabus_code) ON DELETE CASCADE
);

CREATE INDEX idx_grading_criterion_type ON grading_criterion(criteria_type);
CREATE INDEX idx_grading_criterion_syllabus ON grading_criterion(syllabus_code);

-- program（学修プログラム）
CREATE TABLE IF NOT EXISTS program (
    program_id SERIAL PRIMARY KEY,
    program_name TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE INDEX idx_program_name ON program(program_name);

-- requirement（科目要件属性）
CREATE TABLE IF NOT EXISTS requirement (
    requirement_id SERIAL PRIMARY KEY,
    requirement_year INTEGER NOT NULL,
    faculty_id INTEGER NOT NULL,
    subject_name_id INTEGER NOT NULL,
    requirement_type TEXT NOT NULL,
    applied_science_available BOOLEAN NOT NULL,
    graduation_credit_limit BOOLEAN NOT NULL,
    year_restriction BOOLEAN NOT NULL,
    first_year_only BOOLEAN NOT NULL,
    up_to_second_year BOOLEAN NOT NULL,
    guidance_required BOOLEAN NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id) ON DELETE RESTRICT,
    FOREIGN KEY (subject_name_id) REFERENCES subject_name(subject_name_id) ON DELETE RESTRICT
);

CREATE INDEX idx_requirement_type ON requirement(requirement_type);
CREATE INDEX idx_requirement_restrictions ON requirement(applied_science_available, graduation_credit_limit, year_restriction);
CREATE INDEX idx_requirement_subject ON requirement(subject_name_id);

-- subject_program（科目-学習プログラム関連）
CREATE TABLE IF NOT EXISTS subject_program (
    id SERIAL PRIMARY KEY,
    requirement_id INTEGER NOT NULL,
    program_id INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (requirement_id) REFERENCES requirement(requirement_id) ON DELETE CASCADE,
    FOREIGN KEY (program_id) REFERENCES program(program_id) ON DELETE CASCADE
);

CREATE INDEX idx_subject_program_requirement ON subject_program(requirement_id);
CREATE INDEX idx_subject_program_program ON subject_program(program_id);

-- ========== マイグレーションファイルの実行 ==========

-- （この部分はgenerate-init.shで自動挿入されます）
\i /docker-entrypoint-initdb.d/migrations/V20250522111408__insert_class_notes.sql
\i /docker-entrypoint-initdb.d/migrations/V20250522111408__insert_classs.sql
\i /docker-entrypoint-initdb.d/migrations/V20250522111408__insert_subclasss.sql
\i /docker-entrypoint-initdb.d/migrations/V20250522111408__insert_subject_names.sql

-- ========== 開発用データベースの初期化 ==========

\i /docker-entrypoint-initdb.d/02-init-dev.sql
