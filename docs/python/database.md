# データベース操作 (`database.py`)

## クラス: `Database`

### コンストラクタ
```python
def __init__(self, db_url: str)
```
- `db_url`: データベース接続URL
  - SQLite3の場合: `"sqlite:///db/syllabus.db"`（プロジェクトルートからの相対パス）
  - PostgreSQLの場合: `"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"`
    - 環境変数から読み込む（推奨）：
      ```python
      import os
      from urllib.parse import quote_plus

      db_url = "postgresql://{user}:{password}@{host}:{port}/{dbname}".format(
          user=quote_plus(os.getenv('DB_USER', 'postgres')),
          password=quote_plus(os.getenv('DB_PASSWORD', '')),
          host=os.getenv('DB_HOST', 'localhost'),
          port=os.getenv('DB_PORT', '5432'),
          dbname=os.getenv('DB_NAME', 'syllabus_db')
      )
      ```

#### メソッド一覧

#### データベース初期化
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

#### レコード追加
```python
def add_record(self, model: T) -> Optional[T]
```
- 単一のレコードを追加します
- 成功時は追加されたモデルインスタンス、失敗時は`None`を返します

#### 複数レコード一括追加
```python
def add_records(self, models: list[T]) -> bool
```
- 複数のレコードを一括で追加します
- 成功時は`True`、失敗時は`False`を返します

#### ID指定でのレコード取得
```python
def get_by_id(self, model_class: Type[T], id_value: any) -> Optional[T]
```
- 指定されたIDのレコードを取得します
- 存在しない場合は`None`を返します

#### レコード更新
```python
def update_record(self, model: T) -> bool
```
- レコードを更新します
- 成功時は`True`、失敗時は`False`を返します

#### レコード削除
```python
def delete_record(self, model: T) -> bool
```
- レコードを削除します
- 成功時は`True`、失敗時は`False`を返します

## 使用例

### データベース接続
```python
import os
from urllib.parse import quote_plus
from src.db.database import Database
from src.db.models import Subject, Syllabus

# SQLite3を使用する場合（開発環境向け）
db = Database("sqlite:///db/syllabus.db")

# PostgreSQLを使用する場合（本番環境向け）
# 環境変数から安全に接続情報を取得
db_url = "postgresql://{user}:{password}@{host}:{port}/{dbname}".format(
    user=quote_plus(os.getenv('DB_USER', 'postgres')),
    password=quote_plus(os.getenv('DB_PASSWORD', '')),
    host=os.getenv('DB_HOST', 'localhost'),
    port=os.getenv('DB_PORT', '5432'),
    dbname=os.getenv('DB_NAME', 'syllabus_db')
)
db = Database(db_url)

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

## 更新履歴

| 日付 | バージョン | 更新者 | 内容 |
|------|------------|--------|------|
| 2024-03-20 | 1.0.0 | 藤原 | 初版作成 |

[🔝 ページトップへ](#)