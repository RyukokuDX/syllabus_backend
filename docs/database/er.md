---
title: データベースER図
file_version: v1.3.5
project_version: v1.3.36
last_updated: 2025-06-24
---
<!-- Curosr はversion 弄るな -->

# データベースER図

- File Version: v1.3.5
- Project Version: v1.3.36
- Last Updated: 2025-06-24

[readmeへ](../../README.md) | [設計ポリシーへ](policy.md) | [構造定義へ](structure.md)


## 凡例
- `||--o{` : 1対多の関連（1つのエンティティが複数のエンティティを持つ）
- `}o--||` : 多対1の関連（複数のエンティティが1つのエンティティに属する）
- `}o--o|` : 多対0または1の関連（複数のエンティティが0または1つのエンティティに属する）
- `||--||` : 1対1の関連（1つのエンティティが1つのエンティティに属する）
- `}o--o{` : 多対多の関連（複数のエンティティが複数のエンティティに属する）

### 制約記号
- `PK` : 主キー（Primary Key）
- `FK` : 外部キー（Foreign Key）
- `UK` : ユニーク制約（Unique Constraint）
- `PK,UK` : 主キーかつユニーク制約
- `"NOT NULL"` : 非NULL制約（必ず最後に配置）

<!--
erDiagram template
Table{
   field_name field_type key(PK or FK or UK or PK/FK or "" )
   field_name field_type key(PK or FK or UK or PK/FK or "" ) "NOT NULL"
}
-->

```mermaid
erDiagram
%% ===========================
%% Master Tables
%% ===========================
CLASS_TABLE {
    class_id int PK
    class_name text UK "NOT NULL"
    created_at timestamp "NOT NULL"
}
SUBCLASS_TABLE {
    subclass_id int PK
    subclass_name text UK "NOT NULL"
    created_at timestamp "NOT NULL"
}
FACULTY {
    faculty_id int PK
    faculty_name text UK "NOT NULL"
    created_at timestamp "NOT NULL"
}
SUBJECT_NAME {
    subject_name_id int PK
    name text UK "NOT NULL"
    created_at timestamp "NOT NULL"
}
INSTRUCTOR {
    instructor_id int PK
    name text "NOT NULL"
    name_kana text
    created_at timestamp "NOT NULL"
}
SYLLABUS_MASTER {
    syllabus_id int PK
    syllabus_code text "NOT NULL"
    syllabus_year int "NOT NULL"
    created_at timestamp "NOT NULL"
    updated_at timestamp
}
BOOK {
    book_id int PK
    title text "NOT NULL"
    author text
    publisher text
    price int
    isbn text UK
    created_at timestamp "NOT NULL"
}
BOOK_UNCATEGORIZED {
    id int PK
    syllabus_id int FK "NOT NULL"
    title text "NOT NULL"
    author text
    publisher text
    price int
    role text "NOT NULL"
    isbn text
    categorization_status text
    created_at timestamp "NOT NULL"
    updated_at timestamp
}
SUBJECT_ATTRIBUTE {
    attribute_id int PK
    attribute_name text UK "NOT NULL"
    description text
    created_at timestamp "NOT NULL"
}

%% ===========================
%% Transaction Tables
%% ===========================
SYLLABUS {
    syllabus_id int PK,FK "NOT NULL"
    subject_name_id int FK "NOT NULL"
    subtitle text
    term text "NOT NULL"
    campus text "NOT NULL"
    credits int "NOT NULL"
    goals text
    summary text
    attainment text
    methods text
    outside_study text
    textbook_comment text
    reference_comment text
    advice text
    created_at timestamp "NOT NULL"
    updated_at timestamp
}
SUBJECT_GRADE {
    id int PK
    syllabus_id int FK "NOT NULL"
    grade text "NOT NULL"
    created_at timestamp "NOT NULL"
    updated_at timestamp
}
LECTURE_TIME {
    id int PK
    syllabus_id int FK "NOT NULL"
    day_of_week text "NOT NULL"
    period int "NOT NULL"
    created_at timestamp "NOT NULL"
    updated_at timestamp
}
LECTURE_SESSION {
    lecture_session_id int PK
    syllabus_id int FK "NOT NULL"
    session_number int "NOT NULL"
    contents text
    other_info text
    lecture_format text
    created_at timestamp "NOT NULL"
    updated_at timestamp
}
LECTURE_SESSION_IRREGULAR {
    lecture_session_irregular_id int PK
    syllabus_id int FK "NOT NULL"
    session_pattern text "NOT NULL"
    contents text
    other_info text
    instructor text
    error_message text "NOT NULL"
    lecture_format text
    created_at timestamp "NOT NULL"
    updated_at timestamp
}
SYLLABUS_INSTRUCTOR {
    id int PK
    syllabus_id int FK "NOT NULL"
    instructor_id int FK "NOT NULL"
    role text
    created_at timestamp "NOT NULL"
    updated_at timestamp
}
LECTURE_SESSION_INSTRUCTOR {
    id int PK
    lecture_session_id int FK "NOT NULL"
    instructor_id int FK "NOT NULL"
    role text
    created_at timestamp "NOT NULL"
    updated_at timestamp
}
SYLLABUS_BOOK {
    id int PK
    syllabus_id int FK "NOT NULL"
    book_id int FK "NOT NULL"
    role text "NOT NULL"
    note text
    created_at timestamp "NOT NULL"
}
GRADING_CRITERION {
    id int PK
    syllabus_id int FK "NOT NULL"
    criteria_type text "NOT NULL"
    ratio int
    note text
    created_at timestamp "NOT NULL"
}

%% ===========================
%% Basic Table
%% ===========================
SUBJECT {
    subject_id int PK
    subject_name_id int FK "NOT NULL"
    faculty_id int FK "NOT NULL"
    curriculum_year int "NOT NULL"
    class_id int FK "NOT NULL"
    subclass_id int FK
    requirement_type text "NOT NULL"
    created_at timestamp "NOT NULL"
    updated_at timestamp
}

%% ===========================
%% Relation Tables
%% ===========================
SUBJECT_SYLLABUS {
    id int PK
    subject_id int FK "NOT NULL"
    syllabus_id int FK "NOT NULL"
    created_at timestamp "NOT NULL"
    updated_at timestamp
}
SUBJECT_ATTRIBUTE_VALUE {
    id int PK
    subject_id int FK "NOT NULL"
    attribute_id int FK "NOT NULL"
    value text "NOT NULL"
    created_at timestamp "NOT NULL"
    updated_at timestamp
}
SYLLABUS_STUDY_SYSTEM {
    id int PK
    source_syllabus_id int FK "NOT NULL"
    target text "NOT NULL"
    created_at timestamp "NOT NULL"
    updated_at timestamp
}

%% ===========================
%% Relationships
%% ===========================
SUBJECT_NAME ||--o{ SUBJECT : subject_name_id
FACULTY ||--o{ SUBJECT : faculty_id
CLASS_TABLE ||--o{ SUBJECT : class_id
SUBCLASS_TABLE }o--o| SUBJECT : subclass_id

SUBJECT_NAME ||--o{ SYLLABUS : subject_name_id
INSTRUCTOR ||--o{ SYLLABUS_INSTRUCTOR : instructor_id
INSTRUCTOR ||--o{ LECTURE_SESSION_INSTRUCTOR : instructor_id
BOOK ||--o{ SYLLABUS_BOOK : book_id
SUBJECT_ATTRIBUTE ||--o{ SUBJECT_ATTRIBUTE_VALUE : attribute_id
SYLLABUS_MASTER ||--o{ BOOK_UNCATEGORIZED : syllabus_id

SUBJECT ||--o{ SUBJECT_SYLLABUS : subject_id
SUBJECT ||--o{ SUBJECT_ATTRIBUTE_VALUE : subject_id

SYLLABUS_MASTER ||--|| SYLLABUS : syllabus_id
SYLLABUS_MASTER ||--o{ SUBJECT_GRADE : syllabus_id
SYLLABUS_MASTER ||--o{ LECTURE_TIME : syllabus_id
SYLLABUS_MASTER ||--o{ LECTURE_SESSION : syllabus_id
SYLLABUS_MASTER ||--o{ LECTURE_SESSION_IRREGULAR : syllabus_id
SYLLABUS_MASTER ||--o{ SYLLABUS_INSTRUCTOR : syllabus_id
SYLLABUS_MASTER ||--o{ SYLLABUS_BOOK : syllabus_id
SYLLABUS_MASTER ||--o{ GRADING_CRITERION : syllabus_id
SYLLABUS_MASTER ||--o{ SYLLABUS_STUDY_SYSTEM : source_syllabus_id
SYLLABUS_MASTER ||--o{ SUBJECT_SYLLABUS : syllabus_id
LECTURE_SESSION ||--o{ LECTURE_SESSION_INSTRUCTOR : lecture_session_id
```

[目次へ戻る](#目次) 