-- シラバス入学年度制限テーブルの作成
CREATE TABLE syllabus_enrollment_year (
    id INTEGER PRIMARY KEY,
    syllabus_code TEXT NOT NULL,
    enrollment_year INTEGER NOT NULL,
    FOREIGN KEY (syllabus_code) REFERENCES syllabus(syllabus_code) ON DELETE CASCADE
);

-- インデックスの作成
CREATE INDEX idx_syllabus_enrollment_year_syllabus ON syllabus_enrollment_year(syllabus_code);
CREATE INDEX idx_syllabus_enrollment_year_year ON syllabus_enrollment_year(enrollment_year); 