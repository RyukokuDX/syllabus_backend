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

このプロジェクトは、FastAPI と PostgreSQL を Docker コンテナで分離して運用し、初期データや構造管理を JSON + SQL によって行う設計を採用しています。CI/CD は用いず、VPN 内サーバー上で手動・半自動運用されます。

### 目的
- SQLiteからPostgreSQLへの移行
- 複数開発者での安全なデータ管理
- VPN内での安全な運用

### 特徴
- Dockerによる環境分離
- JSON + SQLによるデータ管理
- 手動・半自動運用による確実性の確保

## ディレクトリ構成

```
your-project/
├── api/                            # FastAPI アプリケーション
│   ├── Dockerfile
│   ├── main.py
│   ├── requirements.txt
│   └── ...
├── postgre/                        # PostgreSQL 用 Docker 構成
│   ├── Dockerfile（任意）
│   ├── .env                        # DB接続情報（Git 管理対象外）
│   └── docker-entrypoint-initdb.d/
│       └── 初期SQL配置場所
├── db/
│   ├── upgrade/                    # JSON による初期データ定義
│   │   └── users/add/user1.json
│   ├── migrate/                    # Git 管理対象の SQL 出力
│   │   └── 001_insert_data.sql
│   └── generate_sql.py            # JSON → SQL 変換スクリプト
├── docs/
│   └── database/
│       └── structure.md           # DB仕様書（設計資料）
├── docker/
│   └── docker-compose.yml
```

## 環境設定

### データベース接続設定
`.env`ファイル（`postgre/.env`）の例：
```env
POSTGRES_DB=mydb
POSTGRES_USER=postgre
POSTGRES_PASSWORD=masterpass

DEV_USER=dev_user
DEV_PASSWORD=devpass

APP_USER=app
APP_PASSWORD=apppass
```

### 注意点
- `.env`ファイルはGit管理対象外
- 開発環境用の`.env.example`を用意

## 運用方針

### Git運用
- JSON（`db/upgrade/`）とSQL（`db/migrate/`）をGitで管理
- `.env`はサーバーに手動設置し`.env.example`を別途Git管理

### SQL適用フロー
1. ローカルでJSONを追加
2. `generate_sql.py`を実行しSQLを生成
3. GitにコミットしVPN内Gitサーバーにpush
4. VPNサーバーでgit pull
5. SQLの適用

#### SQLの適用コマンド例
```bash
docker exec -i postgre-db psql -U postgre -d mydb < db/migrate/001_insert_data.sql
```

または

```bash
scp db/migrate/001_insert_data.sql user@vpn-server:/home/user/project/
ssh user@vpn-server 'docker exec -i postgre-db psql -U postgre -d mydb < /home/user/project/001_insert_data.sql'
```

## FastAPI実装方針

### 基本方針
- FastAPIアプリはSQLファイルを直接使用しない
- ORMまたはAPIを通じてDBを操作
- 初期データ投入・マイグレーションはPostgreSQL側で管理

### 実装のポイント
- SQLAlchemyを使用したORM操作
- トランザクション管理の徹底
- エラーハンドリングの強化

## マイグレーションと拡張

### マイグレーション管理（golang-migrate）
- マイグレーションツールとして`golang-migrate`を採用
- バージョン管理された形式でSQLファイルを管理
- ロールバック機能の活用

#### マイグレーションファイルの配置
```
db/
├── migrations/
│   ├── 000001_create_tables.up.sql
│   ├── 000001_create_tables.down.sql
│   ├── 000002_add_indexes.up.sql
│   └── 000002_add_indexes.down.sql
└── generate_sql.py
```

#### マイグレーションコマンド
```bash
# マイグレーションファイルの作成
migrate create -ext sql -dir db/migrations -seq add_new_table

# マイグレーションの実行
migrate -path db/migrations -database "postgresql://user:password@localhost:5432/dbname?sslmode=disable" up

# ロールバック
migrate -path db/migrations -database "postgresql://user:password@localhost:5432/dbname?sslmode=disable" down 1
```

### データ管理ツール（Go CLI）
- Go言語で実装したCLIツールによるデータ管理
- JSON → SQLの変換を自動化
- バリデーション機能の実装

#### CLIツールの機能
```
cmd/
└── dbtools/
    ├── main.go
    ├── cmd/
    │   ├── generate.go    # JSON → SQL生成
    │   ├── validate.go    # データ検証
    │   └── migrate.go     # マイグレーション実行
    └── internal/
        ├── converter/     # 変換ロジック
        └── validator/     # 検証ロジック
```

#### 使用例
```bash
# SQLの生成
go run cmd/dbtools/main.go generate -input db/upgrade -output db/migrations

# データの検証
go run cmd/dbtools/main.go validate -input db/upgrade

# マイグレーションの実行
go run cmd/dbtools/main.go migrate up
```

### 将来的な拡張案
- マイグレーションの自動化スクリプト
- スキーマ定義からのコード生成
- テストデータ生成機能の追加

### 移行手順
1. golang-migrateのインストール
   ```bash
   go install -tags 'postgres' github.com/golang-migrate/migrate/v4/cmd/migrate@latest
   ```

2. 既存のSQLiteスキーマからPostgreSQLスキーマへの変換
   ```bash
   # スキーマ変換用のマイグレーションファイル作成
   migrate create -ext sql -dir db/migrations -seq initial_schema
   ```

3. データ移行ツールの実装
   ```go
   // cmd/dbtools/cmd/migrate.go
   func migrateData() {
       // SQLiteからデータを読み込み
       // PostgreSQLに書き込み
   }
   ```

4. 移行テストの実施
   - テスト環境でのデータ整合性確認
   - パフォーマンステスト
   - ロールバック手順の確認

## Git管理ポリシー

### ファイル管理方針

| ファイルパス             | 管理対象 | 備考                      |
|--------------------------|----------|---------------------------|
| `db/upgrade/*.json`      | 〇       | データ定義（手入力 or 自動） |
| `db/migrate/*.sql`       | 〇       | 生成SQL（手動 or スクリプト） |
| `postgre/.env`           | ×        | 機密情報のため除外       |
| `postgre/.env.example`   | 〇       | サンプル値を残す         |

### セキュリティ注意点
- 機密情報を含むファイルは必ずGit管理から除外
- 環境変数による設定値の管理
- アクセス権限の適切な設定

[🔝 ページトップへ](#fastapi--postgresql-環境構築データ管理設計書) 