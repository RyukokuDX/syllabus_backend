-- テーブル名の変更
ALTER TABLE syllabus_grade RENAME TO syllabus_eligible_grade;

-- インデックス名の変更
ALTER INDEX uix_syllabus_grade RENAME TO uix_syllabus_eligible_grade;
ALTER INDEX idx_syllabus_grade_syllabus RENAME TO idx_syllabus_eligible_grade_syllabus;
ALTER INDEX idx_syllabus_grade_grade RENAME TO idx_syllabus_eligible_grade_grade; 