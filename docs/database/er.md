# データベースER図

[readmeへ](../../README.md) | [設計ポリシーへ](policy.md) | [構造定義へ](structure.md)

## 目次

### テーブル構成
1. [subject（科目基本情報）](#subject科目基本情報)
2. [syllabus（シラバス情報）](#syllabusシラバス情報)
3. [lecture_session（講義時間）](#lecture_session講義時間)
4. [instructor（教員）](#instructor教員)
5. [syllabus_instructor（シラバス-教員関連）](#syllabus_instructorシラバス-教員関連)
6. [book（書籍）](#book書籍)
7. [syllabus_book（シラバス-教科書関連）](#syllabus_bookシラバス-教科書関連)
8. [grading_criterion（成績評価基準）](#grading_criterion成績評価基準)
9. [syllabus_faculty（シラバス-学部/課程関連）](#syllabus_facultyシラバス-学部課程関連)
10. [requirement（科目要件・属性）](#requirement科目要件属性)
11. [subject_requirement（科目-要綱関連）](#subject_requirement科目-要綱関連)
12. [subject_program（科目-学習プログラム関連）](#subject_program科目-学習プログラム関連)

## 更新履歴

| 日付 | バージョン | 更新者 | 内容 |
|------|------------|--------|------|
| 2025-05-19 | 1.0.0 | 藤原 | 初版作成 |
| 2025-05-20 | 1.1.0 | 藤原 | テーブル名・カラム名の統一（subject_code → syllabus_code） |
| 2025-05-20 | 1.1.1 | 藤原 | requirementテーブルの主キーをrequirement_codeに修正 |
| 2025-05-20 | 1.1.2 | 藤原 | インデックス名の統一、外部キー制約の整理 |

## ER図

```mermaid
erDiagram
    class ||--o{ subject : "has"
    subclass ||--o{ subject : "has"
    class_note ||--o{ subject : "has"
    subject_name ||--o{ subject : "has"
    subject ||--o{ syllabus : "has"
    subject ||--o{ lecture_session : "has"
    subject ||--o{ syllabus_instructor : "has"
    subject ||--o{ syllabus_book : "has"
    subject ||--o{ grading_criterion : "has"
    subject ||--o{ syllabus_faculty : "has"
    subject ||--o{ subject_requirement : "has"
    subject ||--o{ subject_program : "has"

    instructor ||--o{ syllabus_instructor : "teaches"
    book ||--o{ syllabus_book : "used_in"
    requirement ||--o{ subject_requirement : "applies_to"
    faculty ||--o{ syllabus_faculty : "has"
    criteria ||--o{ grading_criterion : "has"

    class {
        INTEGER class_id PK
        TEXT class_name
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }

    subclass {
        INTEGER subclass_id PK
        TEXT subclass_name
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }

    class_note {
        INTEGER class_note_id PK
        TEXT class_note
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }

    subject_name {
        INTEGER subject_name_id PK
        TEXT name
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }

    subject {
        TEXT syllabus_code PK
        INTEGER subject_name_id FK
        INTEGER class_id FK
        INTEGER subclass_id FK
        INTEGER class_note_id FK
        TEXT lecture_code
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }

    syllabus {
        TEXT syllabus_code PK,FK
        INTEGER year
        TEXT subtitle
        TEXT term
        BOOLEAN grade_b1
        BOOLEAN grade_b2
        BOOLEAN grade_b3
        BOOLEAN grade_b4
        BOOLEAN grade_m1
        BOOLEAN grade_m2
        BOOLEAN grade_d1
        BOOLEAN grade_d2
        BOOLEAN grade_d3
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

    lecture_session {
        INTEGER id PK
        TEXT syllabus_code FK
        TEXT day_of_week
        INTEGER period
        TIMESTAMP created_at
    }

    instructor {
        TEXT instructor_code PK
        TEXT last_name
        TEXT first_name
        TEXT last_name_kana
        TEXT first_name_kana
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }

    syllabus_instructor {
        INTEGER id PK
        TEXT syllabus_code FK
        TEXT instructor_code FK
        TIMESTAMP created_at
    }

    book {
        INTEGER id PK
        TEXT author
        TEXT title
        TEXT publisher
        INTEGER price
        TEXT isbn
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }

    syllabus_book {
        INTEGER id PK
        TEXT syllabus_code FK
        INTEGER book_id FK
        TINYINT role
        TEXT note
        TIMESTAMP created_at
    }

    criteria {
        INTEGER criteria_id PK
        TEXT criteria_type
        TEXT description
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }

    grading_criterion {
        INTEGER id PK
        TEXT syllabus_code FK
        INTEGER criteria_id FK
        INTEGER ratio
        TEXT note
        TIMESTAMP created_at
    }

    faculty {
        INTEGER faculty_id PK
        TEXT faculty_name
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }

    syllabus_faculty {
        INTEGER id PK
        TEXT syllabus_code FK
        INTEGER faculty_id FK
        TIMESTAMP created_at
    }

    requirement {
        TEXT requirement_code PK
        TEXT subject_name
        TEXT requirement_type
        BOOLEAN applied_science_available
        BOOLEAN graduation_credit_limit
        BOOLEAN year_restriction
        BOOLEAN first_year_only
        BOOLEAN up_to_second_year
        BOOLEAN guidance_required
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }

    subject_requirement {
        INTEGER id PK
        TEXT syllabus_code FK
        TEXT requirement_code FK
        TIMESTAMP created_at
    }

    subject_program {
        INTEGER id PK
        TEXT syllabus_code FK
        TEXT program_code
        TIMESTAMP created_at
    }
```

## テーブル間の関連

### 1対多の関連
- class → subject
- subclass → subject
- class_note → subject
- subject_name → subject
- subject → syllabus
- subject → lecture_session
- subject → syllabus_instructor
- subject → syllabus_book
- subject → grading_criterion
- subject → syllabus_faculty
- subject → subject_requirement
- subject → subject_program
- instructor → syllabus_instructor
- book → syllabus_book
- requirement → subject_requirement
- faculty → syllabus_faculty
- criteria → grading_criterion

### 多対多の関連
- subject ⟷ instructor (syllabus_instructor)
- subject ⟷ book (syllabus_book)
- subject ⟷ requirement (subject_requirement)
- subject ⟷ faculty (syllabus_faculty)

## 主キーと外部キー

### 主キー
- class: class_id
- subclass: subclass_id
- class_note: class_note_id
- subject_name: subject_name_id
- subject: syllabus_code
- syllabus: syllabus_code
- lecture_session: id
- instructor: instructor_code
- syllabus_instructor: id
- book: id
- syllabus_book: id
- criteria: criteria_id
- grading_criterion: id
- faculty: faculty_id
- syllabus_faculty: id
- requirement: requirement_code
- subject_requirement: id
- subject_program: id

### 外部キー
- subject.subject_name_id → subject_name.subject_name_id
- subject.class_id → class.class_id
- subject.subclass_id → subclass.subclass_id
- subject.class_note_id → class_note.class_note_id
- syllabus.syllabus_code → subject.syllabus_code
- lecture_session.syllabus_code → syllabus.syllabus_code
- syllabus_instructor.syllabus_code → subject.syllabus_code
- syllabus_instructor.instructor_code → instructor.instructor_code
- syllabus_book.syllabus_code → subject.syllabus_code
- syllabus_book.book_id → book.id
- grading_criterion.syllabus_code → syllabus.syllabus_code
- grading_criterion.criteria_id → criteria.criteria_id
- syllabus_faculty.syllabus_code → subject.syllabus_code
- syllabus_faculty.faculty_id → faculty.faculty_id
- subject_requirement.syllabus_code → subject.syllabus_code
- subject_requirement.requirement_code → requirement.requirement_code
- subject_program.syllabus_code → subject.syllabus_code

[目次へ戻る](#目次) 