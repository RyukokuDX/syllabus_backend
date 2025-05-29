def generate_subject_table():
    return """
    CREATE TABLE subject (
        subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    """ 