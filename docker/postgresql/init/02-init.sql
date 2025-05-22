
CREATE TABLE IF NOT EXISTS class (
    class_id SERIAL PRIMARY KEY,
    class_name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);


CREATE TABLE IF NOT EXISTS subclass (
    subclass_id SERIAL PRIMARY KEY,
    subclass_name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);


CREATE TABLE IF NOT EXISTS class_note (
    class_note_id SERIAL PRIMARY KEY,
    class_note TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);


CREATE TABLE IF NOT EXISTS subject_name (
    subject_name_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);


CREATE UNIQUE INDEX IF NOT EXISTS idx_subject_name_name ON subject_name(name);


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
);


CREATE INDEX IF NOT EXISTS idx_subject_name ON subject(subject_name_id);
CREATE INDEX IF NOT EXISTS idx_subject_class ON subject(class_id);


CREATE TABLE IF NOT EXISTS faculty (
    faculty_id SERIAL PRIMARY KEY,
    faculty_name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);


CREATE TABLE IF NOT EXISTS instructor (
    instructor_code TEXT PRIMARY KEY,
    last_name TEXT NOT NULL,
    first_name TEXT NOT NULL,
    last_name_kana TEXT,
    first_name_kana TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);


CREATE INDEX IF NOT EXISTS idx_instructor_name ON instructor(last_name, first_name);
CREATE INDEX IF NOT EXISTS idx_instructor_name_kana ON instructor(last_name_kana, first_name_kana);


CREATE TABLE IF NOT EXISTS criteria (
    criteria_id SERIAL PRIMARY KEY,
    criteria_type TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);


CREATE UNIQUE INDEX IF NOT EXISTS idx_criteria_type ON criteria(criteria_type);


CREATE TABLE IF NOT EXISTS book (
    id SERIAL PRIMARY KEY,
    author TEXT,
    title TEXT NOT NULL,
    publisher TEXT,
    price INTEGER,
    isbn TEXT UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);


CREATE INDEX IF NOT EXISTS idx_book_title ON book(title);
CREATE INDEX IF NOT EXISTS idx_book_author ON book(author);


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
);


CREATE INDEX IF NOT EXISTS idx_syllabus_year ON syllabus(year);
CREATE INDEX IF NOT EXISTS idx_syllabus_term ON syllabus(term);
CREATE INDEX IF NOT EXISTS idx_syllabus_grades ON syllabus(grade_b1, grade_b2, grade_b3, grade_b4, grade_m1, grade_m2, grade_d1, grade_d2, grade_d3);
CREATE INDEX IF NOT EXISTS idx_syllabus_campus ON syllabus(campus);


CREATE TABLE IF NOT EXISTS lecture_session (
    id SERIAL PRIMARY KEY,
    syllabus_code TEXT NOT NULL,
    year INTEGER NOT NULL,
    day_of_week TEXT NOT NULL,
    period INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (syllabus_code, year) REFERENCES syllabus(syllabus_code, year) ON DELETE CASCADE
);


CREATE INDEX IF NOT EXISTS idx_lecture_session_day_period ON lecture_session(day_of_week, period);
CREATE INDEX IF NOT EXISTS idx_lecture_session_syllabus ON lecture_session(syllabus_code, year);


CREATE TABLE IF NOT EXISTS syllabus_instructor (
    id SERIAL PRIMARY KEY,
    syllabus_code TEXT NOT NULL,
    instructor_code TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (syllabus_code) REFERENCES subject(syllabus_code) ON DELETE CASCADE,
    FOREIGN KEY (instructor_code) REFERENCES instructor(instructor_code) ON DELETE CASCADE
);


CREATE INDEX IF NOT EXISTS idx_syllabus_instructor_syllabus ON syllabus_instructor(syllabus_code);
CREATE INDEX IF NOT EXISTS idx_syllabus_instructor_instructor ON syllabus_instructor(instructor_code);


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


CREATE INDEX IF NOT EXISTS idx_syllabus_book_syllabus ON syllabus_book(syllabus_code);
CREATE INDEX IF NOT EXISTS idx_syllabus_book_book ON syllabus_book(book_id);


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
);


CREATE INDEX IF NOT EXISTS idx_grading_criterion_criteria ON grading_criterion(criteria_id);
CREATE INDEX IF NOT EXISTS idx_grading_criterion_syllabus_criteria ON grading_criterion(syllabus_code, year, criteria_id);


CREATE TABLE IF NOT EXISTS syllabus_faculty (
    id SERIAL PRIMARY KEY,
    syllabus_code TEXT NOT NULL,
    faculty_id INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (syllabus_code) REFERENCES subject(syllabus_code) ON DELETE CASCADE,
    FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id) ON DELETE CASCADE
);


CREATE INDEX IF NOT EXISTS idx_syllabus_faculty_syllabus ON syllabus_faculty(syllabus_code);
CREATE INDEX IF NOT EXISTS idx_syllabus_faculty_faculty ON syllabus_faculty(faculty_id);