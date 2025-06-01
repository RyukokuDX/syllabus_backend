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
    class_name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_class_name ON class(class_name);

-- subclass（科目小区分）
CREATE TABLE IF NOT EXISTS subclass (
    subclass_id SERIAL PRIMARY KEY,
    subclass_name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- faculty（開講学部・課程）
CREATE TABLE IF NOT EXISTS faculty (
    faculty_id SERIAL PRIMARY KEY,
    faculty_name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_faculty_name ON faculty(faculty_name);

-- subject_name（科目名マスタ）
CREATE TABLE IF NOT EXISTS subject_name (
    subject_name_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- syllabus_master（シラバスマスタ）
CREATE TABLE IF NOT EXISTS syllabus_master (
    syllabus_id SERIAL PRIMARY KEY,
    syllabus_code TEXT NOT NULL,
    syllabus_year INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(syllabus_code, syllabus_year)
);

CREATE INDEX IF NOT EXISTS idx_syllabus_master_code ON syllabus_master(syllabus_code);
CREATE INDEX IF NOT EXISTS idx_syllabus_master_year ON syllabus_master(syllabus_year);

-- syllabus（シラバス情報）
CREATE TABLE IF NOT EXISTS syllabus (
    syllabus_id INTEGER PRIMARY KEY REFERENCES syllabus_master(syllabus_id) ON DELETE CASCADE,
    subject_name_id INTEGER NOT NULL REFERENCES subject_name(subject_name_id) ON DELETE RESTRICT,
    subtitle TEXT,
    term TEXT NOT NULL,
    campus TEXT NOT NULL,
    credits INTEGER NOT NULL,
    summary TEXT,
    goals TEXT,
    attainment TEXT,
    methods TEXT,
    outside_study TEXT,
    notes TEXT,
    remarks TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_syllabus_term ON syllabus(term);
CREATE INDEX IF NOT EXISTS idx_syllabus_campus ON syllabus(campus);
CREATE INDEX IF NOT EXISTS idx_syllabus_subject_name ON syllabus(subject_name_id);

-- subject（科目基本情報）
CREATE TABLE IF NOT EXISTS subject (
    subject_id SERIAL PRIMARY KEY,
    subject_name_id INTEGER NOT NULL,
    faculty_id INTEGER NOT NULL,
    class_id INTEGER NOT NULL,
    subclass_id INTEGER,
    curriculum_year INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (subject_name_id) REFERENCES subject_name(subject_name_id),
    FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id),
    FOREIGN KEY (class_id) REFERENCES class(class_id),
    FOREIGN KEY (subclass_id) REFERENCES subclass(subclass_id),
    UNIQUE (subject_name_id, faculty_id, class_id, subclass_id, curriculum_year)
);

CREATE INDEX idx_subject_subject_name ON subject(subject_name_id);
CREATE INDEX idx_subject_class ON subject(class_id);
CREATE INDEX idx_subject_faculty ON subject(faculty_id);
CREATE INDEX idx_subject_curriculum_year ON subject(curriculum_year);

-- subject_syllabus（科目シラバス関連）
CREATE TABLE IF NOT EXISTS subject_syllabus (
    id SERIAL PRIMARY KEY,
    subject_id INTEGER NOT NULL REFERENCES subject(subject_id) ON DELETE CASCADE,
    syllabus_id INTEGER NOT NULL REFERENCES syllabus_master(syllabus_id) ON DELETE RESTRICT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    UNIQUE(subject_id, syllabus_id)
);

CREATE INDEX IF NOT EXISTS idx_subject_syllabus_subject ON subject_syllabus(subject_id);
CREATE INDEX IF NOT EXISTS idx_subject_syllabus_syllabus ON subject_syllabus(syllabus_id);

-- subject_attribute（科目属性）
CREATE TABLE IF NOT EXISTS subject_attribute (
    attribute_id SERIAL PRIMARY KEY,
    attribute_name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- subject_attribute_value（科目属性値）
CREATE TABLE IF NOT EXISTS subject_attribute_value (
    id SERIAL PRIMARY KEY,
    subject_id INTEGER NOT NULL REFERENCES subject(subject_id) ON DELETE CASCADE,
    attribute_id INTEGER NOT NULL REFERENCES subject_attribute(attribute_id) ON DELETE RESTRICT,
    value TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    UNIQUE(subject_id, attribute_id)
);

CREATE INDEX IF NOT EXISTS idx_subject_attribute_value_subject ON subject_attribute_value(subject_id);
CREATE INDEX IF NOT EXISTS idx_subject_attribute_value_attribute ON subject_attribute_value(attribute_id);

-- instructor（教員）
CREATE TABLE IF NOT EXISTS instructor (
    instructor_id SERIAL PRIMARY KEY,
    last_name TEXT NOT NULL,
    first_name TEXT NOT NULL,
    last_name_kana TEXT,
    first_name_kana TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(last_name, first_name)
);

CREATE INDEX IF NOT EXISTS idx_instructor_name ON instructor(last_name, first_name);
CREATE INDEX IF NOT EXISTS idx_instructor_name_kana ON instructor(last_name_kana, first_name_kana);

-- book（書籍）
CREATE TABLE IF NOT EXISTS book (
    book_id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    publisher TEXT,
    price INTEGER,
    isbn TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_book_title ON book(title);

-- book_author（書籍著者）
CREATE TABLE IF NOT EXISTS book_author (
    book_author_id SERIAL PRIMARY KEY,
    book_id INTEGER NOT NULL REFERENCES book(book_id) ON DELETE CASCADE,
    author_name TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_book_author_book ON book_author(book_id);
CREATE INDEX IF NOT EXISTS idx_book_author_name ON book_author(author_name);

-- lecture_time（講義時間）
CREATE TABLE IF NOT EXISTS lecture_time (
    id SERIAL PRIMARY KEY,
    syllabus_id INTEGER NOT NULL REFERENCES syllabus_master(syllabus_id) ON DELETE CASCADE,
    day_of_week TEXT NOT NULL,
    period SMALLINT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_lecture_time_day_period ON lecture_time(day_of_week, period);
CREATE INDEX IF NOT EXISTS idx_lecture_time_syllabus ON lecture_time(syllabus_id);

-- lecture_session（講義セッション）
CREATE TABLE IF NOT EXISTS lecture_session (
    lecture_session_id SERIAL PRIMARY KEY,
    syllabus_id INTEGER NOT NULL REFERENCES syllabus_master(syllabus_id) ON DELETE CASCADE,
    session_number INTEGER NOT NULL,
    contents TEXT,
    other_info TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_lecture_session_syllabus ON lecture_session(syllabus_id);
CREATE INDEX IF NOT EXISTS idx_lecture_session_number ON lecture_session(session_number);

-- lecture_session_instructor（講義セッション教員）
CREATE TABLE IF NOT EXISTS lecture_session_instructor (
    id SERIAL PRIMARY KEY,
    lecture_session_id INTEGER NOT NULL REFERENCES lecture_session(lecture_session_id) ON DELETE CASCADE,
    instructor_id INTEGER NOT NULL REFERENCES instructor(instructor_id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_lecture_session_instructor_session ON lecture_session_instructor(lecture_session_id);
CREATE INDEX IF NOT EXISTS idx_lecture_session_instructor_instructor ON lecture_session_instructor(instructor_id);

-- syllabus_instructor（シラバス教員関連）
CREATE TABLE IF NOT EXISTS syllabus_instructor (
    id SERIAL PRIMARY KEY,
    syllabus_id INTEGER NOT NULL REFERENCES syllabus_master(syllabus_id) ON DELETE CASCADE,
    instructor_id INTEGER NOT NULL REFERENCES instructor(instructor_id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_syllabus_instructor_syllabus ON syllabus_instructor(syllabus_id);
CREATE INDEX IF NOT EXISTS idx_syllabus_instructor_instructor ON syllabus_instructor(instructor_id);

-- syllabus_book（シラバス教科書関連）
CREATE TABLE IF NOT EXISTS syllabus_book (
    id SERIAL PRIMARY KEY,
    syllabus_id INTEGER NOT NULL REFERENCES syllabus_master(syllabus_id) ON DELETE CASCADE,
    book_id INTEGER NOT NULL REFERENCES book(book_id) ON DELETE CASCADE,
    role TEXT NOT NULL,
    note TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_syllabus_book_syllabus ON syllabus_book(syllabus_id);
CREATE INDEX IF NOT EXISTS idx_syllabus_book_book ON syllabus_book(book_id);

-- grading_criterion（成績評価基準）
CREATE TABLE IF NOT EXISTS grading_criterion (
    id SERIAL PRIMARY KEY,
    syllabus_id INTEGER NOT NULL REFERENCES syllabus_master(syllabus_id) ON DELETE CASCADE,
    criteria_type TEXT NOT NULL,
    ratio INTEGER,
    note TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_grading_criterion_type ON grading_criterion(criteria_type);
CREATE INDEX IF NOT EXISTS idx_grading_criterion_syllabus ON grading_criterion(syllabus_id);

-- syllabus_study_system（シラバス学習システム）
CREATE TABLE IF NOT EXISTS syllabus_study_system (
    id SERIAL PRIMARY KEY,
    source_syllabus_id INTEGER NOT NULL REFERENCES syllabus_master(syllabus_id) ON DELETE CASCADE,
    target TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    UNIQUE(source_syllabus_id, target)
);

CREATE INDEX IF NOT EXISTS idx_syllabus_study_system_source ON syllabus_study_system(source_syllabus_id);
CREATE INDEX IF NOT EXISTS idx_syllabus_study_system_target ON syllabus_study_system(target);

-- subject_grade（科目履修可能学年）
CREATE TABLE IF NOT EXISTS subject_grade (
    id SERIAL PRIMARY KEY,
    syllabus_id INTEGER NOT NULL REFERENCES syllabus_master(syllabus_id) ON DELETE CASCADE,
    grade TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    UNIQUE(syllabus_id, grade)
);

CREATE INDEX IF NOT EXISTS idx_subject_grade_grade ON subject_grade(grade);
CREATE INDEX IF NOT EXISTS idx_subject_grade_syllabus ON subject_grade(syllabus_id);

-- ========== マイグレーションファイルの実行 ==========

-- （この部分はgenerate-init.shで自動挿入されます）
\i /docker-entrypoint-initdb.d/migrations/V20250531153113__insert_classs.sql
\i /docker-entrypoint-initdb.d/migrations/V20250531153113__insert_facultys.sql
\i /docker-entrypoint-initdb.d/migrations/V20250531153113__insert_instructors.sql
\i /docker-entrypoint-initdb.d/migrations/V20250531153113__insert_subclasss.sql
\i /docker-entrypoint-initdb.d/migrations/V20250531192920__insert_syllabus_masters.sql
