-- ========== データベースの作成 ==========

CREATE DATABASE syllabus;

-- ========== ユーザーの作成 ==========

-- master_user: 全操作
CREATE USER master_user WITH PASSWORD 'master_pass';

-- dev_user: dev_db 全操作 + master_db 読み取り専用
CREATE USER dev_user WITH PASSWORD 'dev_pass';

-- app_user: master_db 読み取り専用
CREATE USER app_user WITH PASSWORD 'app_pass';

-- ========== 権限付与 ==========

-- master_user に全DBへのフルアクセス（明示）
GRANT ALL PRIVILEGES ON DATABASE syllabus TO master_user;
GRANT ALL PRIVILEGES ON DATABASE syllabus TO dev_user;

-- dev_user に dev_db の全権限
GRANT ALL PRIVILEGES ON DATABASE syllabus TO dev_user;

-- app_user/dev_user に master_db への読み取り権限のみ
-- ※ PostgreSQL では DATABASE への GRANT だけではなく、スキーマやテーブルに対する明示的な付与が必要

-- === master_db に対して dev_user/app_user を読み取り専用で設定 ===

-- 接続切替（master_db）
\connect syllabus

-- 共有スキーマ public に接続・参照許可
GRANT CONNECT ON DATABASE syllabus TO dev_user, app_user;
GRANT USAGE ON SCHEMA public TO dev_user, app_user;

-- ========== テーブル作成（master_db） ==========

-- subject（科目基本情報）
CREATE TABLE IF NOT EXISTS subject (
    syllabus_code TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    class_name TEXT NOT NULL,
    subclass_name TEXT,
    class_note TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE INDEX idx_subject_name ON subject(name);
CREATE INDEX idx_subject_class ON subject(class_name);

-- syllabus（シラバス情報）
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

CREATE INDEX idx_syllabus_year ON syllabus(year);
CREATE INDEX idx_syllabus_term ON syllabus(term);
CREATE INDEX idx_syllabus_grades ON syllabus(grade_b1, grade_b2, grade_b3, grade_b4, grade_m1, grade_m2, grade_d1, grade_d2, grade_d3);
CREATE INDEX idx_syllabus_campus ON syllabus(campus);

-- syllabus_time（講義時間）
CREATE TABLE IF NOT EXISTS lecture_session (
    id SERIAL PRIMARY KEY,
    syllabus_code TEXT NOT NULL,
    day_of_week INTEGER NOT NULL,
    period INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (syllabus_code) REFERENCES syllabus(syllabus_code) ON DELETE CASCADE
);

CREATE INDEX idx_lecture_session_day_period ON lecture_session(day_of_week, period);
CREATE INDEX idx_lecture_session_syllabus ON lecture_session(syllabus_code);

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

-- syllabus_instructor（シラバス-教員関連）
CREATE TABLE IF NOT EXISTS syllabus_instructor (
    id SERIAL PRIMARY KEY,
    syllabus_code TEXT NOT NULL,
    instructor_code TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (syllabus_code) REFERENCES subject(syllabus_code) ON DELETE CASCADE,
    FOREIGN KEY (instructor_code) REFERENCES instructor(instructor_code) ON DELETE CASCADE
);

CREATE INDEX idx_syllabus_instructor_syllabus ON syllabus_instructor(syllabus_code);
CREATE INDEX idx_syllabus_instructor_instructor ON syllabus_instructor(instructor_code);

-- book（書籍）
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

CREATE INDEX idx_book_title ON book(title);
CREATE INDEX idx_book_author ON book(author);

-- syllabus_textbook（シラバス-教科書関連）
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

CREATE INDEX idx_syllabus_book_syllabus ON syllabus_book(syllabus_code);
CREATE INDEX idx_syllabus_book_book ON syllabus_book(book_id);

-- syllabus_reference（シラバス-参考文献関連）
CREATE TABLE IF NOT EXISTS syllabus_reference (
    id SERIAL PRIMARY KEY,
    syllabus_code TEXT NOT NULL,
    book_id INTEGER NOT NULL,
    note TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (syllabus_code) REFERENCES subject(syllabus_code) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES book(id) ON DELETE CASCADE
);

CREATE INDEX idx_syllabus_reference_syllabus ON syllabus_reference(syllabus_code);
CREATE INDEX idx_syllabus_reference_book ON syllabus_reference(book_id);

-- grading_criterion（成績評価基準）
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

CREATE INDEX idx_grading_criterion_type ON grading_criterion(criteria_type);
CREATE INDEX idx_grading_criterion_syllabus_type ON grading_criterion(syllabus_code, criteria_type);

-- syllabus_faculty（シラバス-学部関連）
CREATE TABLE IF NOT EXISTS syllabus_faculty (
    id SERIAL PRIMARY KEY,
    syllabus_code TEXT NOT NULL,
    faculty VARCHAR(60) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (syllabus_code) REFERENCES subject(syllabus_code) ON DELETE CASCADE
);

CREATE INDEX idx_syllabus_faculty_syllabus ON syllabus_faculty(syllabus_code);
CREATE INDEX idx_syllabus_faculty_faculty ON syllabus_faculty(faculty);

-- subject_requirement（科目要件）
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

CREATE INDEX idx_requirement_type ON requirement(requirement_type);
CREATE INDEX idx_requirement_restrictions ON requirement(applied_science_available, graduation_credit_limit, year_restriction);

-- subject_program（科目-プログラム関連）
CREATE TABLE IF NOT EXISTS subject_requirement (
    id SERIAL PRIMARY KEY,
    syllabus_code TEXT NOT NULL,
    requirement_code TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (syllabus_code) REFERENCES subject(syllabus_code) ON DELETE CASCADE,
    FOREIGN KEY (requirement_code) REFERENCES requirement(requirement_code) ON DELETE CASCADE
);

CREATE INDEX idx_subject_requirement_syllabus ON subject_requirement(syllabus_code);
CREATE INDEX idx_subject_requirement_requirement ON subject_requirement(requirement_code);

-- 全テーブルに SELECT 許可
GRANT SELECT ON ALL TABLES IN SCHEMA public TO dev_user, app_user;

-- シーケンス読み取り許可
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO dev_user, app_user;

-- 新規テーブル・シーケンスへの SELECT 自動付与
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT ON TABLES TO dev_user, app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT USAGE, SELECT ON SEQUENCES TO dev_user, app_user;

-- カタログ参照許可（.tables, PRAGMA 相当）
GRANT SELECT ON pg_catalog.pg_tables TO dev_user, app_user;
GRANT SELECT ON information_schema.tables TO dev_user, app_user;

-- 接続切替（dev_db）
\connect syllabus

-- dev_user に dev_db の public スキーマ操作権限（必要なら）
GRANT ALL PRIVILEGES ON SCHEMA public TO dev_user;

-- ========== テーブル作成（dev_db） ==========

-- 上記と同じテーブル定義を dev_db にも作成
-- subject（科目基本情報）
CREATE TABLE IF NOT EXISTS subject (
    syllabus_code TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    class_name TEXT NOT NULL,
    subclass_name TEXT,
    class_note TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE INDEX idx_subject_name ON subject(name);
CREATE INDEX idx_subject_class ON subject(class_name);

-- 以下、master_dbと同じテーブル定義を繰り返し...
-- （以下、上記のテーブル定義と同じ内容を繰り返すため省略）

-- ========== マイグレーションファイルの実行 ==========

-- マイグレーションファイルを実行
\i /docker-entrypoint-initdb.d/02-migrations/V20250518211454__insert_subjects.sql
\i /docker-entrypoint-initdb.d/02-migrations/V20250519022619__insert_syllabuss.sql
\i /docker-entrypoint-initdb.d/02-migrations/V20250519023115__insert_syllabus_times.sql
