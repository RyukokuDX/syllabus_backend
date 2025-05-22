# PostgreSQL環境構築・データ管理設計書

[readmeへ](../../README.md) | [doc.mdへ](../doc.md)

## 目次
1. [概要](#概要)
2. [ディレクトリ構成](#ディレクトリ構成)
3. [環境設定](#環境設定)
4. [運用方針](#運用方針)
5. [マイグレーション管理](#マイグレーション管理)
6. [Git管理ポリシー](#git管理ポリシー)

## 概要

このプロジェクトは、PostgreSQL を Docker コンテナで運用し、マイグレーションによるデータ管理を行う設計を採用しています。VPN 内サーバー上で手動・半自動運用されます。

### 目的
- SQLiteからPostgreSQLへの移行
- マイグレーションによる安全なデータ管理
- VPN内での安全な運用

### 特徴
- Dockerによる環境分離
- マイグレーションによるデータ管理
- 手動・半自動運用による確実性の確保

## ディレクトリ構成

```
syllabus_backend/
├── docker/
│   ├── fastapi/                        # FastAPI アプリケーション
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── postgresql/                 # PostgreSQL 用 Docker 構成
│       ├── Dockerfile
│       ├── .env                    # DB接続情報（Git 管理対象外）
│       └── init/                   # 初期化スクリプト
│           └── migrations/         # マイグレーションファイル
├── docs/
│   ├── database/
│   │   ├── structure.md           # DB仕様書（設計資料）
│   │   ├── policy.md              # DB設計ポリシー
│   │   └── er.md                  # ER図
│   └── docker/
│       └── postgresql.md          # PostgreSQL設定書（本ファイル）
├── src/
│   └── db/
│       └── migrations/            # マイグレーション生成スクリプト
└── updates/                       # 更新用JSONファイル
    └── subject/
        ├── add/                   # 追加データ
        ├── update/               # 更新データ
        └── delete/               # 削除データ
```

## 環境設定

### データベース構成

#### データベース
- syllabus_db: シラバス情報データベース

#### ユーザーと権限
1. admin_user
   - データベースへの全権限
   - スキーマ作成、テーブル作成、データ操作など全ての操作が可能

2. app_user
   - データベースへの読み取り専用権限
   - アプリケーション実行時の接続用

### 環境変数設定
`.env`ファイル（`docker/postgresql/.env`）は,
開発環境では特に秘匿性はありあません。
開発段階やDB更新だけでしたら、`.env.sample`を流用してください。
ただし、公開時はパスを秘匿してください。

### 初期化プロセス

0. docker/postgresql/init/init.sqlを作成
   - `.env.sample`を流用しない場合は、`docker/psotgresql/generate-init.sh`で
   `.env`の内容を反映したpostgresqlサーバーの設定が必要です

1. データベースとユーザーの作成
   - syllabus_dbの作成
   - admin_userとapp_userの作成と権限設定

2. マイグレーションの適用
   - `init/migrations/`内のSQLファイルを順次実行
   - バージョン管理されたマイグレーションによるテーブル作成とデータ投入

## マイグレーション管理

### マイグレーションファイルの命名規則
```
V{YYYYMMDDHHMMSS}__{description}.sql
```
例：`V20240320123456__create_subject_table.sql`

### マイグレーションの生成
1. JSONファイルを`updates/subject/add/`に配置
2. マイグレーション生成スクリプトを実行
```bash
python src/db/migrations/generate_migration.py
```

### マイグレーションの適用
Dockerコンテナ起動時に自動的に適用されます。

### マイグレーションの確認
```sql
-- 適用済みマイグレーションの確認
SELECT * FROM migration_history ORDER BY applied_at;
```

## データベース管理

### データベースへの接続

```bash
# admin_userとして接続（全権限）
psql -h localhost -p 5432 -U admin_user -d syllabus_db

# app_userとして接続（読み取り専用）
psql -h localhost -p 5432 -U app_user -d syllabus_db
```

### バックアップとリストア

```bash
# バックアップ
docker exec postgresql-db pg_dump -U admin_user syllabus_db > backup.sql

# リストア
cat backup.sql | docker exec -i postgresql-db psql -U admin_user -d syllabus_db
```

## トラブルシューティング

### 文字化け対策
- 日本語対応のためのロケール設定
- データベース作成時のエンコーディング指定
- クライアント接続時の文字コード設定

### アクセス権限の確認
```sql
-- ユーザー権限の確認
\du

-- テーブル権限の確認
\dp

-- スキーマ権限の確認
\dn+
```

### ログの確認
```bash
# データベースのログを表示
docker logs postgresql-db
```

[🔝 ページトップへ](#postgresql環境構築データ管理設計書) 