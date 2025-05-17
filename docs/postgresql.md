# PostgreSQL 開発用データベース運用仕様書

[readmeへ](../README.md) | [DB構造へ](database_structure.md) | [DB運用マニュアルへ](db_operation_manual.md) | [ライブラリ仕様へ](database_python.md)

## 目次
1. [概要](#概要)
2. [データベース情報](#データベース情報)
3. [ディレクトリ構成](#ディレクトリ構成)
4. [データベース構築方法](#データベース構築方法)
5. [データ入力方法](#データ入力方法)
6. [本番環境への移行](#本番環境への移行)
7. [アカウント管理](#アカウント管理)
8. [パフォーマンス設定](#パフォーマンス設定開発環境)
9. [安全な運用のために](#安全な運用のために)
10. [管理担当](#管理担当)
11. [変更履歴](#変更履歴)

## 概要

このドキュメントは、講義情報管理システムの開発を安全かつ効率的に行うための **開発専用データベースの運用仕様 (PostgreSQL)** です。
本番環境と切り離されたDBを用意することで、機密情報の保護と自由な開発・テストを両立します。

## データベース情報

* データベース名：`syllabus_dev`
* DBMS：PostgreSQL 17.5
* 主な用途：ローカル環境／テスト自動化／画面開発用データの準備
* 文字エンコーディング：UTF-8（日本語シラバス情報対応）

## ディレクトリ構成

```
db/
├── updates/
│   ├── subjects/              # 科目情報の更新
│   │   ├── add/              # 追加
│   │   ├── modify/           # 変更
│   │   └── delete/           # 削除
│   └── syllabus/             # シラバス情報の更新
│       ├── add/
│       ├── modify/
│       └── delete/
├── archive/                   # 処理済みJSONファイルのアーカイブ
│   └── YYYY-MM/              # 年月ごとのアーカイブ
├── migrations/               # マイグレーションファイル
├── sample_data/             # サンプルデータ
├── .env                     # 接続情報（Git非管理）
└── .env.sample             # 公開用サンプル
```

## データベース構築方法

1. データベースの作成
```bash
# データベースの作成
psql -U dev_admin -d syllabus_dev -f src/db/schema.sql
```

2. テーブルの作成
```bash
# テーブルの作成
psql -U dev_admin -d syllabus_dev -f src/db/tables.sql
```

## データ入力方法

1. サンプルデータの作成
```bash
# サンプルデータの作成
psql -U dev_admin -d syllabus_dev -f src/db/sample_data.sql
```

2. シラバス情報の作成
```bash
# シラバス情報の作成
psql -U dev_admin -d syllabus_dev -f src/db/syllabus_data.sql
```

## 本番環境への移行

### 1. データの検証
```bash
# 開発環境のデータ検証
python src/db/validators/validate_data.py

# 整合性チェック
python src/db/validators/check_integrity.py
```

### 2. マイグレーションファイルの準備
```bash
# マイグレーションファイルの生成
alembic revision --autogenerate -m "production_migration"

# マイグレーションの適用
alembic upgrade head
```

### 3. 本番環境への適用
```bash
# 本番環境用のダンプファイル作成
pg_dump -U dev_admin -Fc syllabus_dev > prod_migration.dump

# 本番環境への適用
pg_restore -U prod_admin -d syllabus_prod prod_migration.dump
```

## アカウント管理

| ロール名 | 用途 | 権限 |
|---------|------|------|
| `dev_admin` | 開発DBの管理者 | 作成・削除・全権限 |
| `dev_user` | 開発者用 | SELECT / INSERT / UPDATE |

### ロール作成SQL
```sql
-- 管理者ロールの作成
CREATE ROLE dev_admin WITH LOGIN PASSWORD 'secure_admin_pw';
CREATE ROLE dev_user WITH LOGIN PASSWORD 'secure_user_pw';

-- データベース作成
CREATE DATABASE syllabus_dev OWNER dev_admin;

-- 開発者権限の設定
GRANT CONNECT ON DATABASE syllabus_dev TO dev_user;
GRANT USAGE ON SCHEMA public TO dev_user;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO dev_user;
```

## パフォーマンス設定（開発環境）

* `max_connections`: 100（デフォルト）
* `shared_buffers`: 128MB（デフォルト）
* `work_mem`: 4MB（デフォルト）
* ログ設定:
  * `log_min_duration_statement`: 1000（1秒以上のクエリ）
  * `log_statement`: 'all'（開発用）

## 安全な運用のために

* 本番環境の接続情報を開発に流用しないこと
* `dev_user`には最小限の操作権限のみ与える
* マイグレーションファイルは慎重にレビュー
* `.env`で接続元を明確に分離
* 定期的なバックアップの実施

## 管理担当

* 藤原

## 変更履歴

| 日付 | バージョン | 更新者 | 内容 |
|------|------------|--------|------|
| 2024-03-20 | 1.0.0 | 藤原 | 初版作成 |
| 2024-03-21 | 1.0.1 | 藤原 | ディレクトリ構造を統一 |

[🔝 ページトップへ](#postgresql-開発用データベース運用仕様書) 