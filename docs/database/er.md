# データベースER図

[readmeへ](../../README.md) | [設計ポリシーへ](policy.md) | [構造定義へ](structure.md)

## 目次

### テーブル構成
1. [class（科目区分）](#class科目区分)
2. [subclass（科目小区分）](#subclass科目小区分)
3. [class_note（科目区分の備考）](#class_note科目区分の備考)
4. [faculty（開講学部・課程）](#faculty開講学部課程)
5. [subject_name（科目名マスタ）](#subject_name科目名マスタ)
6. [syllabus（シラバス情報）](#syllabusシラバス情報)
7. [subject（科目基本情報）](#subject科目基本情報)
8. [instructor（教員）](#instructor教員)
9. [book（書籍）](#book書籍)
10. [book_author（書籍著者情報）](#book_author書籍著者情報)
11. [lecture_session（講義時間）](#lecture_session講義時間)
12. [syllabus_faculty（シラバス学部課程関連）](#syllabus_facultyシラバス学部課程関連)
13. [syllabus_instructor（シラバス教員関連）](#syllabus_instructorシラバス教員関連)
14. [syllabus_book（シラバス教科書関連）](#syllabus_bookシラバス教科書関連)
15. [grading_criterion（成績評価基準）](#grading_criterion成績評価基準)
16. [program（学修プログラム）](#program学修プログラム)
17. [requirement（科目要件属性）](#requirement科目要件属性)
18. [subject_program（科目学習プログラム関連）](#subject_program科目学習プログラム関連)

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
        INTEGER credits
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

## テーブル間の関連

### 1対多の関連
- subject_name → syllabus
- syllabus → lecture_session
- syllabus → syllabus_faculty
- syllabus → syllabus_instructor
- syllabus → syllabus_book
- syllabus → grading_criterion
- subject → syllabus
- faculty → subject
- class → subject
- subclass → subject
- class_note → subject
- faculty → syllabus_faculty
- instructor → syllabus_instructor
- book → syllabus_book
- program → subject_program
- requirement → subject_program
- faculty → requirement
- subject_name → requirement

### 多対多の関連
- syllabus ⟷ faculty (syllabus_faculty)
- syllabus ⟷ instructor (syllabus_instructor)
- syllabus ⟷ book (syllabus_book)
- requirement ⟷ program (subject_program)

## 主キーと外部キー

### 主キー
- class: class_id
- subclass: subclass_id
- class_note: class_note_id
- faculty: faculty_id
- subject_name: subject_name_id
- syllabus: syllabus_code
- subject: subject_id
- instructor: instructor_code
- book: book_id
- lecture_session: id
- syllabus_faculty: id
- syllabus_instructor: id
- syllabus_book: id
- grading_criterion: id
- program: program_id
- requirement: requirement_id
- subject_program: id
- book_author: book_author_id

### 外部キー
- syllabus.subject_name_id → subject_name.subject_name_id
- subject.syllabus_code → syllabus.syllabus_code
- subject.faculty_id → faculty.faculty_id
- subject.class_id → class.class_id
- subject.subclass_id → subclass.subclass_id
- subject.class_note_id → class_note.class_note_id
- lecture_session.syllabus_code → syllabus.syllabus_code
- syllabus_faculty.syllabus_code → syllabus.syllabus_code
- syllabus_faculty.faculty_id → faculty.faculty_id
- syllabus_instructor.syllabus_code → syllabus.syllabus_code
- syllabus_instructor.instructor_code → instructor.instructor_code
- syllabus_book.syllabus_code → syllabus.syllabus_code
- syllabus_book.book_id → book.book_id
- grading_criterion.syllabus_code → syllabus.syllabus_code
- subject_program.requirement_id → requirement.requirement_id
- subject_program.program_id → program.program_id
- requirement.faculty_id → faculty.faculty_id
- requirement.subject_name_id → subject_name.subject_name_id
- book_author.book_id → book.book_id

[目次へ戻る](#目次) 