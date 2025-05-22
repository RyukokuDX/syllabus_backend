# データモデル定義 (`models.py`)

[readmeへ](../../README.md) | [DB構成仕様へ](../database/structure.md)

## 概要
SQLAlchemyを使用したデータベースモデルの定義を提供します。
各モデルはデータベースのテーブルと1対1で対応し、型安全性とバリデーションを確保します。

## モデル一覧

### マスタ・基本情報
#### Faculty（開講学部・課程）
```python
class Faculty:
    faculty_id: int         # 学部ID（主キー）
    faculty_name: str       # 学部・課程名
```

#### SubjectName（科目名マスタ）
```python
class SubjectName:
    subject_name_id: int    # 科目名ID（主キー）
    name: str               # 科目名
```

#### Book（書籍）
```python
class Book:
    id: int                 # 書籍ID（主キー）
    author: Optional[str]   # 著者名
    title: str              # 書籍タイトル
    publisher: Optional[str]# 出版社名
    price: Optional[int]    # 価格
    isbn: Optional[str]     # ISBN番号
    created_at: datetime
    updated_at: Optional[datetime]
```

#### Instructor（教員）
```python
class Instructor:
    instructor_code: str    # 教職員番号（主キー）
    last_name: str
    first_name: str
    last_name_kana: Optional[str]
    first_name_kana: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
```

### 科目・シラバス
#### Subject（科目基本情報）
```python
class Subject:
    syllabus_code: str      # シラバス管理番号（主キー）
    name: str               # 科目名
    class_name: str         # 科目区分
    subclass_name: Optional[str]  # 小区分
    class_note: Optional[str]     # 区分備考
    created_at: datetime
    updated_at: Optional[datetime]
```

#### Syllabus（シラバス情報）
```python
class Syllabus:
    syllabus_code: str      # シラバス管理番号（主キー）
    year: int              # 開講年度
    subtitle: Optional[str]
    term: str
    grade_b1: bool
    grade_b2: bool
    grade_b3: bool
    grade_b4: bool
    grade_m1: bool
    grade_m2: bool
    grade_d1: bool
    grade_d2: bool
    grade_d3: bool
    campus: str
    credits: int
    lecture_code: str
    summary: Optional[str]
    goals: Optional[str]
    methods: Optional[str]
    outside_study: Optional[str]
    notes: Optional[str]
    remarks: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
```

### 中間・関連テーブル
#### SyllabusFaculty（シラバス-学部/課程関連）
```python
class SyllabusFaculty:
    id: int
    syllabus_code: str
    faculty_id: int
    created_at: datetime
```

#### SyllabusInstructor（シラバス-教員関連）
```python
class SyllabusInstructor:
    id: int
    syllabus_code: str
    instructor_code: str
    created_at: datetime
```

#### SyllabusBook（シラバス-書籍関連）
```python
class SyllabusBook:
    id: int
    syllabus_code: str
    book_id: int
    role: int  # 1:教科書, 2:参考書
    note: Optional[str]
    created_at: datetime
```

#### GradingCriterion（成績評価基準）
```python
class GradingCriterion:
    id: int
    syllabus_code: str
    criteria_type: str
    ratio: Optional[int]
    note: Optional[str]
    created_at: datetime
```

#### SubjectRequirement（科目-要綱関連）
```python
class SubjectRequirement:
    id: int
    syllabus_code: str
    requirement_code: str
    created_at: datetime
```

#### SubjectProgram（科目-学習プログラム関連）
```python
class SubjectProgram:
    id: int
    syllabus_code: str
    program_code: str
    created_at: datetime
```

#### LectureSession（講義時間）
```python
class LectureSession:
    id: int
    syllabus_code: str
    day_of_week: int
    period: int
    created_at: datetime
```

### 要件・属性
#### Requirement（科目要件属性）
```python
class Requirement:
    requirement_code: str
    subject_name: str
    requirement_type: str
    applied_science_available: bool
    graduation_credit_limit: bool
    year_restriction: bool
    first_year_only: bool
    up_to_second_year: bool
    guidance_required: bool
    created_at: datetime
    updated_at: Optional[datetime]
```

---

## 使用例
```python
faculty = Faculty(faculty_id=1, faculty_name="情報理工学部")
subject_name = SubjectName(subject_name_id=1, name="プログラミング基礎")
subject = Subject(syllabus_code="K250622250", name="プログラミング基礎", class_name="専門科目", subclass_name="情報系科目", class_note="初学者向け", created_at=datetime.now(), updated_at=None)
syllabus = Syllabus(syllabus_code="K250622250", year=2025, subtitle="Pythonによるプログラミング入門", term="前期", grade_b1=True, grade_b2=True, grade_b3=False, grade_b4=False, grade_m1=False, grade_m2=False, grade_d1=False, grade_d2=False, grade_d3=False, campus="瀬田", credits=2, lecture_code="2025-K250622250-01", summary="プログラミングの基礎概念とPython言語の基本を学びます。", goals="1. プログラミングの基本概念を理解する", methods="講義と実習を組み合わせて行います。", outside_study="毎週の課題プログラミングに取り組んでください。", notes="ノートPCを持参してください。", remarks="初回授業でPython開発環境のセットアップを行います。", created_at=datetime.now(), updated_at=None)
```

## 関連ドキュメント
- [データベース構造定義](../database/structure.md)
- [データベース操作クラス](database.md)
- [DB更新スクリプト](update_db.md)

## 更新履歴

| 日付 | バージョン | 更新者 | 内容 |
|------|------------|--------|------|
| 2024-03-20 | 1.0.0 | 藤原 | 初版作成 |
| 2024-03-21 | 1.1.0 | 藤原 | モデル定義と使用例を追加 |
| 2025-05-21 | 2.0.0 | 藤原 | DB構造・サンプルJSON・models.pyに完全準拠し全面改訂 |

[🔝 ページトップへ](#データモデル定義-modelspy)