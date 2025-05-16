# データベースライブラリ仕様

[readmeへ](../README.md) | [DB構成仕様へ](database_structure.md)

## 概要
シラバス情報データベースを操作するためのPythonライブラリです。SQLAlchemyを使用してORMを提供し、データベースの初期化やレコードの操作を行うことができます。

## ディレクトリ構成
```
src/db/
├── models.py      # データベースモデルの定義
└── database.py    # データベース操作用ユーティリティ
```

## モデル定義 (`models.py`)

### テーブル一覧
1. `Subject`: 科目基本情報
2. `Syllabus`: シラバス情報
3. `SyllabusTime`: 講義時間
4. `Instructor`: 教員
5. `SyllabusInstructor`: シラバス-教員関連
6. `LectureSession`: 講義計画
7. `Book`: 書籍
8. `SyllabusTextbook`: シラバス-教科書関連
9. `SyllabusReference`: シラバス-参考文献関連
10. `GradingCriterion`: 成績評価基準
11. `SyllabusFaculty`: シラバス-学部/課程関連
12. `SubjectRequirement`: 科目要件・属性
13. `SubjectProgram`: 科目-学習プログラム関連

各テーブルの詳細な定義は[DB構成仕様](database_structure.md)を参照してください。

## データベース操作 (`database.py`)

### クラス: `Database`

#### コンストラクタ
```python
def __init__(self, db_url: str)
```
- `db_url`: データベース接続URL（例: "postgresql://user:password@localhost:5432/syllabus_db"）

#### メソッド一覧

##### データベース初期化
```python
def init_db(self)
```
- 全てのテーブルを作成します
- 既存のテーブルがある場合はスキップされます

##### セッション取得
```python
def get_session(self)
```
- 新しいデータベースセッションを返します

##### レコード追加
```python
def add_record(self, model: T) -> Optional[T]
```
- 単一のレコードを追加します
- 成功時は追加されたモデルインスタンス、失敗時は`None`を返します

##### 複数レコード一括追加
```python
def add_records(self, models: list[T]) -> bool
```
- 複数のレコードを一括で追加します
- 成功時は`True`、失敗時は`False`を返します

##### ID指定でのレコード取得
```python
def get_by_id(self, model_class: Type[T], id_value: any) -> Optional[T]
```
- 指定されたIDのレコードを取得します
- 存在しない場合は`None`を返します

##### レコード更新
```python
def update_record(self, model: T) -> bool
```
- レコードを更新します
- 成功時は`True`、失敗時は`False`を返します

##### レコード削除
```python
def delete_record(self, model: T) -> bool
```
- レコードを削除します
- 成功時は`True`、失敗時は`False`を返します

## 使用例

### データベース接続
```python
from src.db.database import Database
from src.db.models import Subject, Syllabus

# データベースインスタンスの作成
db = Database("postgresql://user:password@localhost:5432/syllabus_db")

# データベースの初期化
db.init_db()
```

### レコードの追加
```python
# 科目の追加
subject = Subject(
    subject_code="SUBJ001",
    name="プログラミング基礎",
    class_name="専門科目"
)
db.add_record(subject)

# シラバスの追加
syllabus = Syllabus(
    subject_code="SUBJ001",
    year=2024,
    term="前期",
    grade_b1=True,
    grade_b2=True,
    grade_b3=False,
    grade_b4=False,
    grade_m1=False,
    grade_m2=False,
    grade_d1=False,
    grade_d2=False,
    grade_d3=False,
    campus="深草",
    credits=2,
    lecture_code="ABC123"
)
db.add_record(syllabus)
```

### レコードの取得と更新
```python
# IDによるレコードの取得
subject = db.get_by_id(Subject, "SUBJ001")
if subject:
    # レコードの更新
    subject.name = "プログラミング基礎A"
    db.update_record(subject)
```

### レコードの削除
```python
subject = db.get_by_id(Subject, "SUBJ001")
if subject:
    db.delete_record(subject)
```

## エラーハンドリング
- 全てのデータベース操作は`SQLAlchemyError`をキャッチし、適切にログ出力します
- エラー発生時は操作がロールバックされます
- エラーの詳細はログに記録されます 