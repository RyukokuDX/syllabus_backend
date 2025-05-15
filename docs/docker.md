# Docker構成
[readmeへ](../README.md)

## 概要
本プロジェクトではDockerを使用して、開発環境と本番環境の一貫性を保ちます。

## 開発環境
- APIサーバー: Dockerコンテナ
- データベース: ローカルホスト（推奨）またはDockerコンテナ

## コンテナ構成

### APIサーバー（FastAPI）
- イメージ: `python:3.11-slim`
- ポート: 8000
- 環境変数:
  - `DATABASE_URL`: 環境に応じたDB接続情報
  - `DEBUG_MODE`
  - `LOG_LEVEL`

## データベース運用方針
- prostagesql
- DB接続情報は環境変数で管理
- SSL/TLS暗号化の強制

## 監視と運用
- コンテナのヘルスチェック
- DBコネクションプールの適切な設定
- クエリパフォーマンスの監視
- リソース使用率の監視
- ログ集中管理

## バックアップ方針
- 本番DBの定期バックアップ
- バックアップの自動化
- リストア手順の文書化

## ディレクトリ構造
```
.
├── docker-compose.yml
└── docker/
    ├── api/
    │   ├── Dockerfile
    │   └── requirements.txt
    └── db/
        └── init.sql
```

## Docker共通仕様

### 初期化SQL（init.sql）の用途

#### 概要
`init.sql`は、PostgreSQLコンテナが初めて起動する際に自動的に実行されるSQLスクリプトです。
データベースの初期セットアップを自動化する目的で使用されます。

#### 主な用途
1. テーブルの作成
```sql
CREATE TABLE IF NOT EXISTS syllabus (
    id SERIAL PRIMARY KEY,
    year VARCHAR(4) NOT NULL,
    title VARCHAR(255) NOT NULL,
    -- その他のカラム
);
```

2. 初期データの投入
```sql
INSERT INTO faculty (name, code) VALUES
    ('文学部', 'LIT'),
    ('経済学部', 'ECO');
```

3. インデックスの作成
```sql
CREATE INDEX idx_syllabus_year ON syllabus(year);
CREATE INDEX idx_syllabus_title ON syllabus(title);
```

4. 権限の設定
```sql
GRANT SELECT ON ALL TABLES IN SCHEMA public TO api_user;
```

#### 実行タイミング
- PostgreSQLコンテナの初回起動時のみ実行
- データベースが既に初期化されている場合は実行されない
- コンテナの再起動時は実行されない

#### 配置場所
```
docker/
└── db/
    └── init.sql  # PostgreSQLコンテナの/docker-entrypoint-initdb.d/にマウント
```

#### 注意事項
- 開発環境でのみ使用することを推奨
- 本番環境ではマイグレーションツールの使用を推奨
- 大量のデータ投入は別のプロセスで実行
- エラーハンドリングを適切に実装

#### 開発環境での利用例
- テストデータの自動投入
- 開発用アカウントの作成
- テスト用のビューやファンクションの作成

#### 本番環境での代替案
- データベースマイグレーションツール（Alembic等）の使用
- 手動でのデータベース初期化
- バックアップからのリストア

[トップへ](#)