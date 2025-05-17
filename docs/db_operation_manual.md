# データベース運用手順書

[🔝 ページトップへ](#データベース運用手順書)

## 関連ドキュメント
- [README](../README.md)
- [データベース構造](./database_structure.md)
- [PythonでのDB操作](./database_python.md)
- [PostgreSQL設定](./postgresql.md)

## はじめに
このドキュメントは、PostgreSQLデータベースの具体的な運用手順を説明します。
特に、JSONファイルを使用したデータの更新方法に重点を置いています。

## 1. 開発環境のセットアップ

### 1.1 必要なツールのインストール
```bash
# 必要なPythonパッケージのインストール
pip install sqlalchemy alembic psycopg2-binary python-dotenv

# PostgreSQLのインストール確認
psql --version
```

### 1.2 データベースの初期設定
```bash
# PostgreSQLへの接続
psql -U postgres

# データベースとユーザーの作成
CREATE DATABASE syllabus_dev;
CREATE USER dev_user WITH PASSWORD 'syllabus';
GRANT ALL PRIVILEGES ON DATABASE syllabus_dev TO dev_user;
```

## 2. データの更新手順

### 2.1 JSONファイルの配置
データ更新用のJSONファイルは以下の場所に配置します：

```
db/
└── updates/
    ├── subjects/              # 科目情報の更新
    │   ├── add/              # 追加
    │   ├── modify/           # 変更
    │   └── delete/           # 削除
    └── syllabus/             # シラバス情報の更新
        ├── add/
        ├── modify/
        └── delete/
```

### 2.2 JSONファイルの形式

#### 単一エントリの形式（推奨）
```json
{
    "subject_code": "AB123",
    "name": "プログラミング基礎",
    "class_name": "専門科目",
    "subclass_name": "情報系"
}
```

#### 複数エントリの形式（一括処理用）
```json
[
    {
        "subject_code": "AB123",
        "name": "プログラミング基礎",
        "class_name": "専門科目",
        "subclass_name": "情報系"
    },
    {
        "subject_code": "CD456",
        "name": "データベース基礎",
        "class_name": "専門科目",
        "subclass_name": "情報系"
    }
]
```

**注意事項：**
- 一括処理の場合、トランザクション制御により全件成功または全件失敗となります
- 一度に処理可能な最大件数は1000件です
- エラーが発生した場合は、どのエントリでエラーが発生したかをログに記録します

#### シラバス情報の追加（syllabus/add/）

##### 単一エントリの形式（推奨）
```json
{
    "subject_code": "AB123",
    "year": 2025,
    "term": "前期",
    "subtitle": "Pythonプログラミング",
    "summary": "プログラミングの基礎を学習します",
    "goals": ["基本的なプログラムが書ける", "デバッグができる"],
    "instructors": ["山田太郎", "鈴木花子"]
}
```

##### 複数エントリの形式（一括処理用）
```json
[
    {
        "subject_code": "AB123",
        "year": 2025,
        "term": "前期",
        "subtitle": "Pythonプログラミング",
        "summary": "プログラミングの基礎を学習します",
        "goals": ["基本的なプログラムが書ける", "デバッグができる"],
        "instructors": ["山田太郎", "鈴木花子"]
    },
    {
        "subject_code": "CD456",
        "year": 2025,
        "term": "後期",
        "subtitle": "データベース設計",
        "summary": "データベースの基礎を学習します",
        "goals": ["ER図が書ける", "SQLが書ける"],
        "instructors": ["佐藤一郎"]
    }
]
```

### 2.3 更新コマンドの実行

```bash
# データ更新スクリプトの実行
python src/db/tools/update_db.py --type subjects --action add --file db/updates/subjects/add/new_subjects.json

# シラバス情報の更新
python src/db/tools/update_db.py --type syllabus --action modify --file db/updates/syllabus/modify/update_syllabus.json
```

### 2.4 更新の確認
```bash
# 更新されたデータの確認
python src/db/tools/verify_updates.py --type subjects --id AB123
```

## 3. よくある操作手順

### 3.1 新規科目の追加
1. `db/updates/subjects/add/`に新規科目のJSONファイルを作成
   ```json
   {
       "subject_code": "CD456",
       "name": "データベース基礎",
       "class_name": "専門科目"
   }
   ```

2. 更新スクリプトを実行
   ```bash
   python src/db/tools/update_db.py --type subjects --action add --file db/updates/subjects/add/new_subject.json
   ```

3. 確認
   ```bash
   python src/db/tools/verify_updates.py --type subjects --id CD456
   ```

### 3.2 シラバス情報の一括更新
1. CSVからJSONへの変換（必要な場合）
   ```bash
   python src/db/tools/csv_to_json.py --input data.csv --output db/updates/syllabus/add/bulk_update.json
   ```

2. 一括更新の実行
   ```bash
   python src/db/tools/bulk_update.py --file db/updates/syllabus/add/bulk_update.json
   ```

### 3.3 データの修正
1. 修正用JSONファイルの作成
   ```json
   {
       "subject_code": "AB123",
       "changes": {
           "name": "プログラミング基礎演習",
           "subclass_name": "実習系"
       }
   }
   ```

2. 修正の適用
   ```bash
   python src/db/tools/update_db.py --type subjects --action modify --file db/updates/subjects/modify/fix.json
   ```

## 4. エラー対応

### 4.1 よくあるエラーと対処法
- `subject_code already exists`
  → 既存のコードを確認し、重複を避ける
- `invalid JSON format`
  → JSONファイルの構文を確認
- `missing required field`
  → 必須フィールドが抜けていないか確認

### 4.2 ロールバック手順
```bash
# 最後の更新をロールバック
python src/db/tools/rollback.py --last

# 特定の更新をロールバック
python src/db/tools/rollback.py --id UPDATE_ID
```

## 5. 定期メンテナンス

### 5.1 バックアップの作成
```bash
# JSONバックアップの作成
python src/db/tools/export_to_json.py --output backup/

# データベースダンプの作成
pg_dump -U dev_user syllabus_dev > backup/syllabus_dev_$(date +%Y%m%d).sql
```

### 5.2 データの整合性チェック
```bash
# 全テーブルの整合性チェック
python src/db/tools/check_integrity.py

# 特定のテーブルのチェック
python src/db/tools/check_integrity.py --table subjects
```

## 6. トラブルシューティング

### 6.1 接続エラー
```bash
# 接続テスト
python src/db/tools/test_connection.py

# 接続情報の確認
python src/db/tools/show_config.py
```

### 6.2 ログの確認
```bash
# 更新ログの確認
python src/db/tools/show_logs.py --last 10

# エラーログの確認
python src/db/tools/show_logs.py --type error
```

## 付録

### A. 設定ファイル例
```json
{
    "database": {
        "host": "localhost",
        "port": 5432,
        "name": "syllabus_dev",
        "user": "dev_user"
    },
    "backup": {
        "interval": "daily",
        "keep_days": 7
    }
}
```

### B. 必要なツール
- Python 3.8以上
- PostgreSQL 17.5
- psql（PostgreSQLクライアント）

### C. JSONファイル管理方針

#### C.1 バージョン管理
- すべてのJSONファイルはGitでバージョン管理されます
- ファイル名には更新日時を含めることを推奨（例：`20240320_add_new_subjects.json`）
- コミットメッセージには更新の目的と影響範囲を明記

#### C.2 ファイルの保持とアーカイブ
- 処理済みファイルは`db/updates/archive/YYYY-MM/`に移動
- アーカイブは四半期ごとにまとめてzip化
- アーカイブファイルは3年間保持

#### C.3 ファイル命名規則
```
[日付]_[操作種別]_[対象テーブル]_[概要].json
例：20240320_add_subjects_spring_semester.json
```

#### C.4 処理状態の管理
- 各JSONファイルの処理状態は`db/updates/status.log`で管理
- ログには以下の情報を記録：
  - 処理日時
  - 処理結果（成功/失敗）
  - 影響レコード数
  - エラー内容（該当する場合） 