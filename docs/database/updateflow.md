# データベース更新手順書

[readmeへ](../../README.md) | [doc.mdへ](../doc.md)

## 目次
1. [概要](#概要)
2. [前提条件](#前提条件)
3. [更新の流れ](#更新の流れ)
4. [詳細手順](#詳細手順)
5. [トラブルシューティング](#トラブルシューティング)

## 概要

このドキュメントでは、シラバスデータベースの更新手順について説明します。
データの更新は、JSONファイルを特定のディレクトリに配置し、Dockerコンテナを再起動することで行います。

### 目的
- シラバスデータの安全な更新
- 更新履歴の管理
- エラー発生時の対応

### 特徴
- JSONファイルによるデータ管理
- Dockerによる環境分離
- 手動確認によるデータ整合性の確保

## 前提条件

### 必要なソフトウェア
- Docker Desktop
- Python 3.8以上
- Visual Studio Code（推奨）

### 必要なファイル
- `.env.sample`ファイル（または`.env`ファイル）
- 更新用のJSONファイル

## 更新の流れ

1. 環境の準備
2. JSONファイルの配置
3. Dockerコンテナの再起動
4. 更新の確認

## 詳細手順

### 1. 環境の準備

#### 1-1. プロジェクトのクローン（初回のみ）
```bash
git clone https://github.com/yourusername/syllabus_backend.git
cd syllabus_backend
```

#### 1-2. 環境設定ファイルの準備
1. `.env.sample`を`docker/postgresql/.env`にコピー
```bash
cd docker/postgresql
copy .env.sample .env
```

### 2. JSONファイルの配置

#### 2-1. ディレクトリ構造の確認
更新用JSONファイルは以下のディレクトリに配置します：
```
updates/
└── subject/
    ├── add/      # 新規追加データ
    ├── update/   # 更新データ
    └── delete/   # 削除データ
```

#### 2-2. JSONファイルの形式
```json
{
  "content": {
    "subject_code": "AB1234",
    "subject_name": "プログラミング基礎",
    "credit": 2,
    "created_at": "2024-03-20T10:00:00",
    "updated_at": "2024-03-20T10:00:00"
  }
}
```

#### 2-3. ファイルの配置
1. 更新内容に応じて適切なディレクトリを選択
   - 新規追加 → `updates/subject/add/`
   - 更新 → `updates/subject/update/`
   - 削除 → `updates/subject/delete/`

2. JSONファイルを配置
   - ファイル名は任意（例：`subject_001.json`）
   - 複数ファイルの配置も可能

### 3. Dockerコンテナの再起動

#### 3-1. 現在のコンテナの停止
```bash
cd docker/postgresql
docker compose down
```

#### 3-2. コンテナの再起動
```bash
docker compose up -d
```

### 4. 更新の確認

#### 4-1. データベースへの接続
```bash
# admin_userとして接続
psql -h localhost -p 5432 -U admin_user -d syllabus_db
```

#### 4-2. データの確認
```sql
-- 更新されたデータの確認
SELECT * FROM subject WHERE updated_at > CURRENT_DATE - INTERVAL '1 day';

-- 特定の科目コードの確認
SELECT * FROM subject WHERE subject_code = 'AB1234';
```

## トラブルシューティング

### コンテナ起動エラー
1. ログの確認
```bash
docker logs postgresql-db
```

2. よくある問題と解決方法
- ポート競合
  ```bash
  # 使用中のポートの確認
  netstat -ano | findstr :5432
  ```
- 権限エラー
  - `.env`ファイルの設定を確認
  - Dockerの再起動を試す

### データ更新エラー
1. JSONファイルの形式確認
   - 必須フィールドの存在確認
   - 日付形式の確認
   - 文字コードの確認（UTF-8）

2. データベースの状態確認
```sql
-- テーブル構造の確認
\d subject

-- エラーログの確認
SELECT * FROM error_log ORDER BY created_at DESC LIMIT 10;
```

### バックアップとリストア
```bash
# 更新前のバックアップ
docker exec postgresql-db pg_dump -U admin_user syllabus_db > backup_before_update.sql

# 問題発生時のリストア
cat backup_before_update.sql | docker exec -i postgresql-db psql -U admin_user -d syllabus_db
```

## 補足：マイグレーション（オプション）

マイグレーションを使用する場合は、以下の手順を実行します：

1. マイグレーションファイルの生成
```bash
python src/db/migrations/generate_migration.py
```

2. 生成されたファイルの確認
```bash
ls -l docker/postgresql/init/migrations/
```

マイグレーションファイルは、コンテナ再起動時に自動的に適用されます。

[🔝 ページトップへ](#データベース更新手順書)