---
title: データベースER図
file_version: v1.3.1
project_version: v1.3.20
last_updated: 2025-06-21
---

# データベースER図

- File Version: v1.3.1
- Project Version: v1.3.20
- Last Updated: 2025-06-21

[readmeへ](../../README.md) | [設計ポリシーへ](policy.md) | [構造定義へ](structure.md)

## ER図

### 凡例
- `||--o{` : 1対多の関連（1つのエンティティが複数のエンティティを持つ）
- `}o--||` : 多対1の関連（複数のエンティティが1つのエンティティに属する）
- `}o--o|` : 多対0または1の関連（複数のエンティティが0または1つのエンティティに属する）
- `||--||` : 1対1の関連（1つのエンティティが1つのエンティティに属する）
- `}o--o{` : 多対多の関連（複数のエンティティが複数のエンティティに属する）

```mermaid
erDiagram

    %% マスターテーブル
    class {
        INTEGER class_id PK
        TEXT class_name UNIQUE
        TIMESTAMP created_at
    }
    subclass {
        INTEGER subclass_id PK
        TEXT subclass_name UNIQUE
        TIMESTAMP created_at
    }
    faculty {
        INTEGER faculty_id PK
        TEXT faculty_name UNIQUE
        TIMESTAMP created_at
    }
    subject_name {
        INTEGER subject_name_id PK
        TEXT name
        TIMESTAMP created_at
    }
    instructor {
        INTEGER instructor_id PK
        TEXT name
        TEXT name_kana
        TIMESTAMP created_at
    }
    book {
        INTEGER book_id PK
        TEXT title
        TEXT author
        TEXT publisher
        INTEGER price
        TEXT isbn UNIQUE
        TIMESTAMP created_at
    }
    book_uncategorized {
        INTEGER id PK
        INTEGER syllabus_id FK
        TEXT title
        TEXT author
        TEXT publisher
        INTEGER price
        TEXT role
        TEXT isbn
        TEXT categorization_status
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }
    book_author {
        INTEGER book_author_id PK
        INTEGER book_id FK
        TEXT author_name
        TIMESTAMP created_at
    }
    subject_attribute {
        INTEGER attribute_id PK
        TEXT attribute_name
        TEXT description
        TIMESTAMP created_at
    }

    %% トランザクションテーブル
    syllabus_master {
        INTEGER syllabus_id PK
        TEXT syllabus_code
        INTEGER syllabus_year
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }
    syllabus {
        INTEGER syllabus_id PK,FK
        INTEGER subject_name_id FK
        TEXT subtitle
        TEXT term
        TEXT campus
        INTEGER credits
        TEXT goals
        TEXT summary
        TEXT attainment
        TEXT methods
        TEXT outside_study
        TEXT textbook_comment
        TEXT reference_comment
        TEXT advice
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }
    subject_grade {
        INTEGER id PK
        INTEGER syllabus_id FK
        TEXT grade
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }
    lecture_time {
        INTEGER id PK
        INTEGER syllabus_id FK
        TEXT day_of_week
        SMALLINT period
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }
    lecture_session {
        INTEGER lecture_session_id PK
        INTEGER syllabus_id FK
        INTEGER session_number
        TEXT contents
        TEXT other_info
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }
    syllabus_instructor {
        INTEGER id PK
        INTEGER syllabus_id FK
        INTEGER instructor_id FK
        TEXT role
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }
    lecture_session_instructor {
        INTEGER id PK
        INTEGER lecture_session_id FK
        INTEGER instructor_id FK
        TEXT role
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }
    syllabus_book {
        INTEGER id PK
        INTEGER syllabus_id FK
        INTEGER book_id FK
        TEXT role
        TEXT note
        TIMESTAMP created_at
    }
    grading_criterion {
        INTEGER id PK
        INTEGER syllabus_id FK
        TEXT criteria_type
        INTEGER ratio
        TEXT note
        TIMESTAMP created_at
    }

    %% 基本テーブル
    subject {
        INTEGER subject_id PK
        INTEGER subject_name_id FK
        INTEGER faculty_id FK
        INTEGER curriculum_year
        INTEGER class_id FK
        INTEGER subclass_id FK
        TEXT requirement_type
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }

    %% 関連テーブル
    subject_syllabus {
        INTEGER id PK
        INTEGER subject_id FK
        INTEGER syllabus_id FK
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }
    subject_attribute_value {
        INTEGER id PK
        INTEGER subject_id FK
        INTEGER attribute_id FK
        TEXT value
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }
    syllabus_study_system {
        INTEGER id PK
        INTEGER source_syllabus_id FK
        TEXT target
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }

    %% 関連の定義
    %% マスターテーブル → 基本テーブル
    subject_name ||--o{ subject : "subject_name_id"
    faculty ||--o{ subject : "faculty_id"
    class ||--o{ subject : "class_id"
    subclass }o--o| subject : "subclass_id"

    %% マスターテーブル → トランザクションテーブル
    subject_name ||--o{ syllabus : "subject_name_id"
    instructor ||--o{ syllabus_instructor : "instructor_id"
    instructor ||--o{ lecture_session_instructor : "instructor_id"
    instructor ||--o{ lecture_session_irregular_instructor : "instructor_id"
    book ||--o{ syllabus_book : "book_id"
    book ||--o{ book_author : "book_id"
    subject_attribute ||--o{ subject_attribute_value : "attribute_id"
    syllabus_master ||--o{ book_uncategorized : "syllabus_id"

    %% 基本テーブル → 関連テーブル
    subject ||--o{ subject_syllabus : "subject_id"
    subject ||--o{ subject_attribute_value : "subject_id"

    %% トランザクションテーブル → 関連テーブル
    syllabus_master ||--|| syllabus : "syllabus_id"
    syllabus_master ||--o{ subject_grade : "syllabus_id"
    syllabus_master ||--o{ lecture_time : "syllabus_id"
    syllabus_master ||--o{ lecture_session : "syllabus_id"
    syllabus_master ||--o{ lecture_session_irregular : "syllabus_id"
    syllabus_master ||--o{ syllabus_instructor : "syllabus_id"
    syllabus_master ||--o{ syllabus_book : "syllabus_id"
    syllabus_master ||--o{ grading_criterion : "syllabus_id"
    syllabus_master ||--o{ syllabus_study_system : "source_syllabus_id"
    syllabus_master ||--o{ subject_syllabus : "syllabus_id"

    lecture_session ||--o{ lecture_session_instructor : "lecture_session_id"
    lecture_session_irregular ||--o{ lecture_session_irregular_instructor : "lecture_session_irregular_id"
```

[目次へ戻る](#目次) 