# データモデル定義 (`models.py`)

[readmeへ](../../README.md) | [DB構成仕様へ](../database_structure.md)

## 概要
SQLAlchemyを使用したデータベースモデルの定義を提供します。
各モデルはデータベースのテーブルと1対1で対応し、型安全性とバリデーションを確保します。

## モデル一覧

### 基本情報
#### Subject（科目基本情報）
```python
class Subject:
    subject_code: str  # シラバス管理番号（主キー）
    name: str         # 科目名
    class_name: str   # 科目区分
    subclass_name: Optional[str]  # 科目小区分
    class_note: Optional[str]     # 科目区分の備考
```

#### Syllabus（シラバス情報）
```python
class Syllabus:
    subject_code: str  # シラバス管理番号（主キー）
    year: int         # 開講年度
    term: str         # 開講学期
    credits: int      # 単位数
    campus: str       # 開講キャンパス
    # 学年ごとの履修可否
    grade_b1: bool    # 学部1年
    grade_b2: bool    # 学部2年
    grade_b3: bool    # 学部3年
    grade_b4: bool    # 学部4年
    grade_m1: bool    # 修士1年
    grade_m2: bool    # 修士2年
    grade_d1: bool    # 博士1年
    grade_d2: bool    # 博士2年
    grade_d3: bool    # 博士3年
```

### 関連情報
#### SyllabusTime（講義時間）
```python
class SyllabusTime:
    id: int           # ID（主キー）
    subject_code: str # シラバス管理番号（外部キー）
    day_of_week: str  # 曜日
    period: str       # 時限
```

#### Instructor（教員）
```python
class Instructor:
    instructor_code: str  # 教職員番号（主キー）
    name: str            # 氏名
    name_kana: Optional[str]  # 氏名（カナ）
    name_en: Optional[str]    # 氏名（英語）
```

### 中間テーブル
- `SyllabusInstructor`: シラバスと教員の関連
- `SyllabusTextbook`: シラバスと教科書の関連
- `SyllabusReference`: シラバスと参考文献の関連
- `SyllabusFaculty`: シラバスと学部/課程の関連
- `SubjectProgram`: 科目と学習プログラムの関連

## 使用例

### モデルのインスタンス化
```python
# 科目情報の作成
subject = Subject(
    subject_code="SUBJ001",
    name="プログラミング基礎",
    class_name="専門科目",
    subclass_name="情報系科目"
)

# シラバス情報の作成
syllabus = Syllabus(
    subject_code="SUBJ001",
    year=2024,
    term="前期",
    credits=2,
    campus="深草",
    grade_b1=True,
    grade_b2=True,
    grade_b3=False,
    grade_b4=False,
    grade_m1=False,
    grade_m2=False,
    grade_d1=False,
    grade_d2=False,
    grade_d3=False
)
```

### バリデーション
各モデルは型チェックとバリデーションを自動的に行います：
```python
# 不正な値を設定しようとするとエラー
try:
    subject = Subject(
        subject_code=123,  # 文字列であるべき
        name="プログラミング基礎"
    )
except TypeError as e:
    print(f"型エラー: {e}")
```

## 関連ドキュメント
- [データベース構造定義](../database_structure.md)
- [データベース操作クラス](database.md)
- [DB更新スクリプト](update_db.md)

## 更新履歴

| 日付 | バージョン | 更新者 | 内容 |
|------|------------|--------|------|
| 2024-03-20 | 1.0.0 | 藤原 | 初版作成 |
| 2024-03-21 | 1.1.0 | 藤原 | モデル定義と使用例を追加 |

[🔝 ページトップへ](#データモデル定義-modelspy)