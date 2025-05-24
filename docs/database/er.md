# データベースER図

[readmeへ](../../README.md) | [設計ポリシーへ](policy.md) | [構造定義へ](structure.md)

## 更新履歴

| 日付 | バージョン | 更新者 | 内容 |
|------|------------|--------|------|
| 2025-05-19 | 1.0.0 | 藤原 | 初版作成 |
| 2025-05-20 | 1.1.0 | 藤原 | テーブル名・カラム名の統一（subject_code → syllabus_code） |
| 2025-05-20 | 1.1.1 | 藤原 | requirementテーブルの主キーをrequirement_codeに修正 |
| 2025-05-20 | 1.1.2 | 藤原 | インデックス名の統一、外部キー制約の整理 |
| 2025-05-21 | 1.1.3 | 藤原 | 正規化を強化。facultyテーブルをsubjectテーブルの直後に移動、目次・本文順序修正 |
| 2025-05-21 | 1.1.4 | 藤原 | requirementテーブルの主キーをrequirement_idに変更、関連テーブルの外部キー制約を修正 |
| 2025-05-21 | 1.1.5 | 藤原 | subject_requirementテーブルを削除、requirementテーブルにsyllabus_codeを追加 |
| 2025-05-21 | 1.1.6 | 藤原 | 外部キー制約の整合性を修正、インデックスを最適化 |
| 2025-05-21 | 1.1.7 | 藤原 | 不要な関連を削除、テーブル間の参照整合性を強化 |
| 2025-05-21 | 1.1.8 | 藤原 | programテーブルを追加、subject_programテーブルの外部キー制約を修正 |
| 2025-05-21 | 1.1.9 | 藤原 | subjectテーブルにサロゲートキーを追加、syllabusテーブルとの関連を整理 |
| 2025-05-21 | 1.1.10 | 藤原 | subjectテーブルの主キー名をsubject_idに変更、syllabusテーブルからyearカラムを移動 |
| 2025-05-21 | 1.1.11 | 藤原 | テーブル構成をデータソースの依存度に基づいて再構成 |

## ER図

```mermaid
erDiagram
    %% 凡例
    legend {
        TEXT symbol
        TEXT description
    }
    legend ||--o{ legend_item : "contains"
    legend_item {
        TEXT symbol
        TEXT description
    }

    %% 独立テーブル
    subject_name {
        INTEGER subject_name_id PK
        TEXT name
    }
    faculty {
        INTEGER faculty_id PK
        TEXT faculty_name
    }
    class {
        INTEGER class_id PK
        TEXT class_name
    }
    subclass {
        INTEGER subclass_id PK
        TEXT subclass_name
    }
    class_note {
        INTEGER class_note_id PK
        TEXT class_note
    }
    instructor {
        TEXT instructor_code PK
        TEXT last_name
        TEXT first_name
        TEXT last_name_kana
        TEXT first_name_kana
    }
    book {
        INTEGER book_id PK
        TEXT title
        TEXT isbn
    }
    book_author {
        INTEGER book_author_id PK
        INTEGER book_id FK
        TEXT author_name
    }
    program {
        INTEGER program_id PK
        TEXT program_name
    }

    %% 基本テーブル
    syllabus {
        TEXT syllabus_code PK
        INTEGER subject_name_id FK
        TEXT subtitle
        TEXT term
        TEXT campus
        INTEGER credits
        TEXT summary
        TEXT goals
        TEXT methods
        TEXT outside_study
        TEXT notes
        TEXT remarks
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }
    subject {
        INTEGER subject_id PK
        TEXT syllabus_code FK
        INTEGER syllabus_year
        INTEGER faculty_id FK
        INTEGER class_id FK
        INTEGER subclass_id FK
        INTEGER class_note_id FK
        TEXT lecture_code
    }

    %% 関連テーブル
    syllabus_grade {
        INTEGER id PK
        TEXT syllabus_code FK
        INTEGER syllabus_year
        TEXT grade
    }
    lecture_session {
        INTEGER id PK
        TEXT syllabus_code FK
        INTEGER syllabus_year
        TEXT day_of_week
        TINYINT period
    }
    syllabus_faculty {
        INTEGER id PK
        TEXT syllabus_code FK
        INTEGER faculty_id FK
    }
    syllabus_instructor {
        INTEGER id PK
        TEXT syllabus_code FK
        TEXT instructor_code FK
    }
    syllabus_book {
        INTEGER id PK
        TEXT syllabus_code FK
        INTEGER book_id FK
        TINYINT role
    }
    grading_criterion {
        INTEGER id PK
        TEXT syllabus_code FK
        TEXT criteria_type
        INTEGER ratio
    }
    requirement {
        INTEGER requirement_id PK
        INTEGER requirement_year
        INTEGER faculty_id FK
        INTEGER subject_name_id FK
        TEXT requirement_type
    }
    subject_program {
        INTEGER id PK
        INTEGER requirement_id FK
        INTEGER program_id FK
    }

    %% 関連の定義
    %% 独立テーブル → 基本テーブル
    subject_name ||--o{ syllabus : "subject_name_id"
    faculty }o--|| subject : "faculty_id"
    class }o--|| subject : "class_id"
    subclass }o--o| subject : "subclass_id"
    class_note }o--o| subject : "class_note_id"

    %% 基本テーブル → 関連テーブル
    syllabus ||--o{ syllabus_grade : "syllabus_code"
    syllabus ||--o{ lecture_session : "syllabus_code"
    syllabus ||--o{ syllabus_faculty : "syllabus_code"
    syllabus ||--o{ syllabus_instructor : "syllabus_code"
    syllabus ||--o{ syllabus_book : "syllabus_code"
    syllabus ||--o{ grading_criterion : "syllabus_code"
    subject ||--|| syllabus : "syllabus_code"

    %% 関連テーブルの外部キー
    syllabus_faculty }o--|| faculty : "faculty_id"
    syllabus_instructor }o--|| instructor : "instructor_code"
    syllabus_book }o--|| book : "book_id"
    program ||--o{ subject_program : "program_id"
    requirement ||--o{ subject_program : "requirement_id"
    requirement }o--|| faculty : "faculty_id"
    requirement }o--|| subject_name : "subject_name_id"
    book ||--o{ book_author : "book_id"
```

[目次へ戻る](#目次) 