# データベースER図

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
        TEXT class_name
        TIMESTAMP created_at
    }
    subclass {
        INTEGER subclass_id PK
        TEXT subclass_name
        TIMESTAMP created_at
    }
    faculty {
        INTEGER faculty_id PK
        TEXT faculty_name
        TIMESTAMP created_at
    }
    subject_name {
        INTEGER subject_name_id PK
        TEXT name
        TIMESTAMP created_at
    }
    instructor {
        INTEGER instructor_id PK
        TEXT instructor_code
        TEXT last_name
        TEXT first_name
        TEXT last_name_kana
        TEXT first_name_kana
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }
    book {
        INTEGER book_id PK
        TEXT title
        TEXT publisher
        INTEGER price
        TEXT isbn
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
    subject_grade {
        INTEGER id PK
        INTEGER subject_id FK
        TEXT grade
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }
    lecture_session {
        INTEGER id PK
        TEXT syllabus_code FK
        INTEGER syllabus_year
        TEXT day_of_week
        TINYINT period
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }
    syllabus_instructor {
        INTEGER id PK
        TEXT syllabus_code FK
        INTEGER instructor_id FK
        TIMESTAMP created_at
    }
    syllabus_book {
        INTEGER id PK
        TEXT syllabus_code FK
        INTEGER book_id FK
        TEXT role
        TEXT note
        TIMESTAMP created_at
    }
    grading_criterion {
        INTEGER id PK
        TEXT syllabus_code FK
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
        INTEGER class_id FK
        INTEGER subclass_id FK
        INTEGER curriculum_year
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }

    %% 関連テーブル
    subject_syllabus {
        INTEGER id PK
        INTEGER subject_id FK
        TEXT syllabus_code FK
        INTEGER syllabus_year
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

    %% 関連の定義
    %% マスターテーブル → 基本テーブル
    subject_name ||--o{ subject : "subject_name_id"
    faculty ||--o{ subject : "faculty_id"
    class ||--o{ subject : "class_id"
    subclass }o--o| subject : "subclass_id"

    %% マスターテーブル → トランザクションテーブル
    subject_name ||--o{ syllabus : "subject_name_id"
    instructor ||--o{ syllabus_instructor : "instructor_id"
    book ||--o{ syllabus_book : "book_id"
    book ||--o{ book_author : "book_id"
    subject_attribute ||--o{ subject_attribute_value : "attribute_id"

    %% 基本テーブル → 関連テーブル
    subject ||--o{ subject_grade : "subject_id"
    subject ||--o{ subject_syllabus : "subject_id"
    subject ||--o{ subject_attribute_value : "subject_id"

    %% トランザクションテーブル → 関連テーブル
    syllabus ||--o{ lecture_session : "syllabus_code"
    syllabus ||--o{ syllabus_instructor : "syllabus_code"
    syllabus ||--o{ syllabus_book : "syllabus_code"
    syllabus ||--o{ grading_criterion : "syllabus_code"
    syllabus ||--o{ subject_syllabus : "syllabus_code"
    syllabus ||--o{ syllabus_study_system : "source_syllabus_id"
    syllabus ||--o{ syllabus_study_system : "target_syllabus_id"
```

## 更新履歴

| 日付 | バージョン | 更新者 | 内容 |
|------|------------|--------|------|
| 2024-05-19 | 1.0.0 | 藤原 | 初版作成 |
| 2024-05-20 | 1.1.0 | 藤原 | テーブル名・カラム名の統一（subject_code → syllabus_code） |
| 2024-05-20 | 1.1.1 | 藤原 | requirementテーブルの主キーをrequirement_codeに修正 |
| 2024-05-20 | 1.1.2 | 藤原 | インデックス名の統一、外部キー制約の整理 |
| 2024-05-21 | 1.1.3 | 藤原 | 正規化を強化。facultyテーブルをsubjectテーブルの直後に移動、目次・本文順序修正 |
| 2024-05-21 | 1.1.4 | 藤原 | requirementテーブルの主キーをrequirement_idに変更、関連テーブルの外部キー制約を修正 |
| 2024-05-21 | 1.1.5 | 藤原 | subject_requirementテーブルを削除、requirementテーブルにsyllabus_codeを追加 |
| 2024-05-21 | 1.1.6 | 藤原 | 外部キー制約の整合性を修正、インデックスを最適化 |
| 2024-05-21 | 1.1.7 | 藤原 | 不要な関連を削除、テーブル間の参照整合性を強化 |
| 2024-05-21 | 1.1.8 | 藤原 | programテーブルを追加、subject_programテーブルの外部キー制約を修正 |
| 2024-05-21 | 1.1.9 | 藤原 | subjectテーブルにサロゲートキーを追加、syllabusテーブルとの関連を整理 |
| 2024-05-21 | 1.1.10 | 藤原 | subjectテーブルの主キー名をidに変更、syllabusテーブルからyearカラムを移動 |
| 2024-05-21 | 1.1.11 | 藤原 | テーブル構成をデータソースの依存度に基づいて再構成 |
| 2024-05-21 | 1.1.12 | 藤原 | syllabusテーブルの履修可能学年フィールドをビットマスク方式に変更、パフォーマンスと拡張性を改善 |
| 2024-05-21 | 1.1.13 | 藤原 | requirementテーブルをEAVパターンに変更、programテーブルとsubject_programテーブルを削除 |
| 2024-05-29 | 1.1.14 | 藤原 | マスターテーブルのタイムスタンプカラムを整理、instructorテーブルの主キーをinstructor_idに変更 |
| 2024-05-29 | 1.1.15 | 藤原 | syllabus_bookテーブルのroleカラムをTEXT型に変更、subject_syllabusテーブルからlecture_codeを削除 |

[目次へ戻る](#目次) 