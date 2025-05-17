# データベース初期化スクリプト (`create_database.py`)

[readmeへ](../../README.md) | [DB構成仕様へ](../database/structure.md)

## 概要
`src/db/create_database.py`は、SQLiteデータベースを初期化し、必要なテーブルを作成するスクリプトです。
データベースのスキーマ定義を一元的に管理し、一貫性のある構造を保証します。

## 機能
- SQLiteデータベースファイルの作成
- 各テーブルの作成（存在しない場合のみ）
- 外部キー制約の設定
- タイムスタンプの自動管理

## 作成されるテーブル

### 基本情報テーブル
#### subject（科目基本情報）
```sql
CREATE TABLE IF NOT EXISTS subject (
    subject_code TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    class_name TEXT NOT NULL,
    subclass_name TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
)
```

#### syllabus（シラバス情報）
```sql
CREATE TABLE IF NOT EXISTS syllabus (
    subject_code TEXT PRIMARY KEY,
    year INTEGER NOT NULL,
    subtitle TEXT,
    term TEXT NOT NULL,
    grade_b1 BOOLEAN NOT NULL,
    grade_b2 BOOLEAN NOT NULL,
    grade_b3 BOOLEAN NOT NULL,
    grade_b4 BOOLEAN NOT NULL,
    grade_m1 BOOLEAN NOT NULL,
    grade_m2 BOOLEAN NOT NULL,
    grade_d1 BOOLEAN NOT NULL,
    grade_d2 BOOLEAN NOT NULL,
    grade_d3 BOOLEAN NOT NULL,
    campus TEXT NOT NULL,
    credits INTEGER NOT NULL,
    lecture_code TEXT NOT NULL,
    summary TEXT,
    goals TEXT,
    methods TEXT,
    outside_study TEXT,
    notes TEXT,
    remarks TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (subject_code) REFERENCES subject(subject_code) ON DELETE CASCADE
)
```

### 関連情報テーブル
- `syllabus_time`：講義時間情報
- `instructor`：教員情報
- `lecture_session`：講義計画
- `book`：書籍情報
- `grading_criterion`：成績評価基準

### 中間テーブル
- `syllabus_instructor`：シラバスと教員の関連
- `syllabus_textbook`：シラバスと教科書の関連
- `syllabus_reference`：シラバスと参考文献の関連
- `syllabus_faculty`：シラバスと学部/課程の関連
- `subject_requirement`：科目要件・属性
- `subject_program`：科目と学習プログラムの関連

## 使用方法

### Pythonスクリプトから
```python
from src.db.create_database import init_database

# データベースの初期化
init_database()
```

### コマンドラインから
```bash
python -c "from src.db.create_database import init_database; init_database()"
```

## データベースファイル
- 保存場所: `db/syllabus.db`
- 形式: SQLite3データベースファイル
- 自動作成: 存在しない場合は自動的に作成

## エラーハンドリング
- データベースディレクトリが存在しない場合は自動作成
- テーブルが既に存在する場合はスキップ
- SQLite接続エラーの適切な処理
- 外部キー制約違反の検出

## 関連ドキュメント
- [データベース構造定義](../database/structure.md)
- [データベース操作クラス](database.md)
- [モデル定義](models.md)

## 更新履歴

| 日付 | バージョン | 更新者 | 内容 |
|------|------------|--------|------|
| 2024-03-20 | 1.0.0 | 藤原 | 初版作成 |
| 2024-03-21 | 1.1.0 | 藤原 | src/dbに移動 |

[🔝 ページトップへ](#データベース初期化スクリプト-create_databasepy) 