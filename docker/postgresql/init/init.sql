-- ========== データベースの作成 ==========

CREATE DATABASE master_db;
CREATE DATABASE dev_db;

-- ========== ユーザーの作成 ==========

-- master_user: 全操作
CREATE USER master_user WITH PASSWORD 'master_pass';

-- dev_user: dev_db 全操作 + master_db 読み取り専用
CREATE USER dev_user WITH PASSWORD 'dev_pass';

-- app_user: master_db 読み取り専用
CREATE USER app_user WITH PASSWORD 'app_pass';

-- ========== 権限付与 ==========

-- master_user に全DBへのフルアクセス（明示）
GRANT ALL PRIVILEGES ON DATABASE master_db TO master_user;
GRANT ALL PRIVILEGES ON DATABASE dev_db TO master_user;

-- dev_user に dev_db の全権限
GRANT ALL PRIVILEGES ON DATABASE dev_db TO dev_user;

-- app_user/dev_user に master_db への読み取り権限のみ
-- ※ PostgreSQL では DATABASE への GRANT だけではなく、スキーマやテーブルに対する明示的な付与が必要

-- === master_db に対して dev_user/app_user を読み取り専用で設定 ===

-- 接続切替（master_db）
\connect master_db

-- 共有スキーマ public に接続・参照許可
GRANT CONNECT ON DATABASE master_db TO dev_user, app_user;
GRANT USAGE ON SCHEMA public TO dev_user, app_user;

-- ========== テーブル作成（master_db） ==========

-- subject（科目基本情報）
CREATE TABLE subject (
    subject_code TEXT PRIMARY KEY,
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
CREATE TABLE syllabus (
    subject_code TEXT PRIMARY KEY,
    year INTEGER NOT NULL,
    subtitle TEXT,
    term TEXT NOT NULL,
    grade_b0 BOOLEAN NOT NULL,
    grade_b1 BOOLEAN NOT NULL,
    grade_b2 BOOLEAN NOT NULL,
    grade_b3 BOOLEAN NOT NULL,
    grade_m0 BOOLEAN NOT NULL,
    grade_m1 BOOLEAN NOT NULL,
    grade_d0 BOOLEAN NOT NULL,
    grade_d1 BOOLEAN NOT NULL,
    grade_d2 BOOLEAN NOT NULL,
    campus VARCHAR(5) NOT NULL,
    credits SMALLINT NOT NULL,
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
);

CREATE INDEX idx_syllabus_year ON syllabus(year);
CREATE INDEX idx_syllabus_term ON syllabus(term);
CREATE INDEX idx_syllabus_grades ON syllabus(grade_b0, grade_b2, grade_b3, grade_b4, grade_m1, grade_m2, grade_d1, grade_d2, grade_d3);
CREATE INDEX idx_syllabus_campus ON syllabus(campus);

-- syllabus_time（講義時間）
CREATE TABLE syllabus_time (
    id SERIAL PRIMARY KEY,
    subject_code TEXT NOT NULL,
    day_of_week SMALLINT NOT NULL,
    period SMALLINT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subject_code) REFERENCES subject(subject_code) ON DELETE CASCADE
);

CREATE INDEX idx_syllabus_time_day_period ON syllabus_time(day_of_week, period);
CREATE INDEX idx_syllabus_time_subject ON syllabus_time(subject_code);

-- instructor（教員）
CREATE TABLE instructor (
    instructor_code TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    name_kana TEXT,
    name_en TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE INDEX idx_instructor_name ON instructor(name);
CREATE INDEX idx_instructor_name_kana ON instructor(name_kana);

-- syllabus_instructor（シラバス-教員関連）
CREATE TABLE syllabus_instructor (
    id SERIAL PRIMARY KEY,
    subject_code TEXT NOT NULL,
    instructor_code TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subject_code) REFERENCES subject(subject_code) ON DELETE CASCADE,
    FOREIGN KEY (instructor_code) REFERENCES instructor(instructor_code) ON DELETE CASCADE
);

CREATE INDEX idx_syllabus_instructor_subject ON syllabus_instructor(subject_code);
CREATE INDEX idx_syllabus_instructor_instructor ON syllabus_instructor(instructor_code);

-- lecture_session（講義計画）
CREATE TABLE lecture_session (
    id SERIAL PRIMARY KEY,
    subject_code TEXT NOT NULL,
    session_number INTEGER NOT NULL,
    description TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subject_code) REFERENCES subject(subject_code) ON DELETE CASCADE
);

CREATE INDEX idx_lecture_session_subject_num ON lecture_session(subject_code, session_number);

-- book（書籍）
CREATE TABLE book (
    id SERIAL PRIMARY KEY,
    author TEXT,
    title TEXT NOT NULL,
    publisher TEXT,
    price INTEGER,
    isbn TEXT UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE INDEX idx_book_title ON book(title);
CREATE INDEX idx_book_author ON book(author);

-- syllabus_textbook（シラバス-教科書関連）
CREATE TABLE syllabus_textbook (
    id SERIAL PRIMARY KEY,
    subject_code TEXT NOT NULL,
    book_id INTEGER NOT NULL,
    note TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subject_code) REFERENCES subject(subject_code) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES book(id) ON DELETE CASCADE
);

CREATE INDEX idx_syllabus_textbook_subject ON syllabus_textbook(subject_code);
CREATE INDEX idx_syllabus_textbook_book ON syllabus_textbook(book_id);

-- syllabus_reference（シラバス-参考文献関連）
CREATE TABLE syllabus_reference (
    id SERIAL PRIMARY KEY,
    subject_code TEXT NOT NULL,
    book_id INTEGER NOT NULL,
    note TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subject_code) REFERENCES subject(subject_code) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES book(id) ON DELETE CASCADE
);

CREATE INDEX idx_syllabus_reference_subject ON syllabus_reference(subject_code);
CREATE INDEX idx_syllabus_reference_book ON syllabus_reference(book_id);

-- grading_criterion（成績評価基準）
CREATE TABLE grading_criterion (
    id SERIAL PRIMARY KEY,
    subject_code TEXT NOT NULL,
    criteria_type VARCHAR(3) NOT NULL,
    ratio SMALLINT,
    note TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subject_code) REFERENCES subject(subject_code) ON DELETE CASCADE,
    CHECK (criteria_type IN ('平常', '小テ', '定期', 'レポ', '他', '自由'))
);

CREATE INDEX idx_grading_criterion_type ON grading_criterion(criteria_type);
CREATE INDEX idx_grading_criterion_subject_type ON grading_criterion(subject_code, criteria_type);

-- syllabus_faculty（シラバス-学部/課程関連）
CREATE TABLE syllabus_faculty (
    id SERIAL PRIMARY KEY,
    subject_code TEXT NOT NULL,
    faculty VARCHAR(59) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subject_code) REFERENCES subject(subject_code) ON DELETE CASCADE
);

CREATE INDEX idx_syllabus_faculty_subject ON syllabus_faculty(subject_code);
CREATE INDEX idx_syllabus_faculty_faculty ON syllabus_faculty(faculty);

-- subject_requirement（科目要件・属性）
CREATE TABLE subject_requirement (
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
);

CREATE INDEX idx_requirement_type ON subject_requirement(requirement_type);
CREATE INDEX idx_requirement_restrictions ON subject_requirement(applied_science_available, graduation_credit_limit, year_restriction);

-- subject_program（科目-学習プログラム関連）
CREATE TABLE subject_program (
    id SERIAL PRIMARY KEY,
    subject_code TEXT NOT NULL,
    program_code TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subject_code) REFERENCES subject(subject_code) ON DELETE CASCADE
);

CREATE INDEX idx_subject_program_subject ON subject_program(subject_code);
CREATE INDEX idx_subject_program_program ON subject_program(program_code);

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
\connect dev_db

-- dev_user に dev_db の public スキーマ操作権限（必要なら）
GRANT ALL PRIVILEGES ON SCHEMA public TO dev_user;

-- ========== テーブル作成（dev_db） ==========

-- 上記と同じテーブル定義を dev_db にも作成
-- subject（科目基本情報）
CREATE TABLE subject (
    subject_code TEXT PRIMARY KEY,
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
