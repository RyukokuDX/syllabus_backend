# FastAPI × PostgreSQL 環境構築・データ管理設計書

[readmeへ](../README.md)

## 目次
1. [概要](#概要)
2. [ディレクトリ構成](#ディレクトリ構成)
3. [環境設定](#環境設定)
4. [運用方針](#運用方針)
5. [FastAPI実装方針](#fastapi実装方針)
6. [マイグレーションと拡張](#マイグレーションと拡張)
7. [Git管理ポリシー](#git管理ポリシー)

## 概要

このプロジェクトは、FastAPI と PostgreSQL を Docker コンテナで分離して運用し、初期データや構造管理を SQL によって行う設計を採用しています。CI/CD は用いず、VPN 内サーバー上で手動・半自動運用されます。

### 目的
- SQLiteからPostgreSQLへの移行
- 複数開発者での安全なデータ管理
- VPN内での安全な運用

### 特徴
- Dockerによる環境分離
- SQLによるデータ管理
- 手動・半自動運用による確実性の確保

## ディレクトリ構成

```
syllabus_backend/
├── docker/
│   ├── api/                        # FastAPI アプリケーション
│   │   └── docker-compose.yml
│   └── postgre/                    # PostgreSQL 用 Docker 構成
│       ├── docker-compose.yml
│       ├── .env                    # DB接続情報（Git 管理対象外）
│       └── init/                   # 初期化SQL
│           ├── init.sql            # 生成されたSQL（Git管理対象外）
│           └── init.sql.template   # テンプレート（Git管理対象）
├── docs/
│   ├── database/
│   │   ├── structure.md           # DB仕様書（設計資料）
│   │   ├── policy.md              # DB設計ポリシー
│   │   └── er.md                  # ER図
│   └── docker/
│       └── postgresql.md          # PostgreSQL設定書（本ファイル）
```

## 環境設定

### データベース構成

#### データベース
- master_db: 本番用データベース
- dev_db: 開発用データベース

#### ユーザーと権限
1. master_user
   - 全データベースへの全権限
   - スキーマ作成、テーブル作成、データ操作など全ての操作が可能

2. dev_user
   - dev_dbへの全権限
   - master_dbへの読み取り専用権限
   - 開発環境での作業用

3. app_user
   - master_dbへの読み取り専用権限
   - アプリケーション実行時の接続用

### 環境変数設定
`.env`ファイル（`docker/postgre/.env`）の例：
```env
MASTER_DB=master_db
DEV_DB=dev_db

MASTER_USER=master_user
MASTER_PASSWORD=masterpass

DEV_USER=dev_user
DEV_PASSWORD=devpass

APP_USER=app_user
APP_PASSWORD=apppass
```

### 初期化プロセス

1. テンプレートからSQLの生成
   - `init.sql.template`を元に`init.sql`を生成
   - 環境変数の値を置換

2. データベースとユーザーの作成
   - master_dbとdev_dbの作成
   - 3種類のユーザー作成と権限設定

3. テーブル作成
   - master_dbとdev_dbに同一のテーブル構造を作成
   - インデックスと外部キー制約の設定

### データベース接続設定

```yaml
version: "3.9"

services:
  db:
    image: postgres:15
    container_name: postgres-db
    restart: always
    env_file:
      - .env
    environment:
      - LANG=ja_JP.UTF-8
      - LC_ALL=ja_JP.UTF-8
      - POSTGRES_INITDB_ARGS="--encoding=UTF8 --locale=ja_JP.UTF-8"
    ports:
      - "5432:5432"
    volumes:
      - ./init/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
      - postgres_data:/var/lib/postgresql/data
```

## データベース管理

### データベースへの接続

```bash
# master_userとして接続（全権限）
psql -h localhost -p 5432 -U master_user -d master_db

# dev_userとして接続（開発用）
psql -h localhost -p 5432 -U dev_user -d dev_db

# app_userとして接続（読み取り専用）
psql -h localhost -p 5432 -U app_user -d master_db
```

### 初期化とリセット

1. 既存のコンテナとボリュームの削除
```bash
docker-compose down -v
```

2. 新規コンテナの起動（自動的に初期化実行）
```bash
docker-compose up -d
```

### バックアップとリストア

```bash
# master_dbのバックアップ
docker exec postgres-db pg_dump -U master_user master_db > backup_master.sql

# dev_dbのバックアップ
docker exec postgres-db pg_dump -U master_user dev_db > backup_dev.sql

# リストア（master_db）
cat backup_master.sql | docker exec -i postgres-db psql -U master_user -d master_db

# リストア（dev_db）
cat backup_dev.sql | docker exec -i postgres-db psql -U master_user -d dev_db
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
docker-compose logs db
```

[🔝 ページトップへ](#fastapi--postgresql-環境構築データ管理設計書) 