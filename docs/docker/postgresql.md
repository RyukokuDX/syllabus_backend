# PostgreSQL環境構築・データ管理設計書

[readmeへ](../../README.md) | [doc.mdへ](../doc.md)

## 目次
1. [概要](#概要)
2. [ディレクトリ構成](#ディレクトリ構成)
3. [環境設定](#環境設定)
4. [運用方針](#運用方針)
5. [初期化プロセス](#初期化プロセス)
6. [初期化スクリプトの実行メカニズム](#初期化スクリプトの実行メカニズム)
7. [PowerShellスクリプト](#powershellスクリプト)
   - [start-postgres.ps1](#powershellスクリプトstart-postgresps1)
   - [stop-postgres.ps1](#powershellスクリプトstop-postgresps1)
   - [check-postgres.ps1](#powershellスクリプトcheck-postgresps1)
8. [マイグレーション管理](#マイグレーション管理)
9. [Git管理ポリシー](#git管理ポリシー)
10. [トラブルシューティング](#トラブルシューティング)
11. [更新履歴](#更新履歴)

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

0. 環境変数の設定
   - `.env`ファイルを`docker/postgresql/.env`に配置
   - 開発環境では`.env.sample`を流用可能

1. 初期化スクリプトの生成
   - `generate-init.sh`を実行して初期化SQLファイルを生成
   - テンプレートファイル（`init/init.sql.template`、`init/init-dev.sql.template`）から
   - 環境変数を反映した`init/01-init.sql`と`init/02-init-dev.sql`を生成
   - マイグレーションファイルの自動挿入

2. PostgreSQLコンテナの起動
   - `docker-compose up -d`でコンテナを起動
   - コンテナ起動時に自動的に初期化スクリプトが実行される
   - 初期化スクリプトの実行順序：
     1. `01-init.sql`: データベースとユーザーの作成、権限設定
     2. マイグレーションファイル: テーブル作成と初期データ投入
     3. `02-init-dev.sql`: 開発用データベースの作成と設定

3. 初期化の確認
   - コンテナ起動後、各テーブルのレコード数を表示
   - 正常に初期化されたことを確認

### 初期化スクリプトの実行メカニズム

PostgreSQLコンテナの初期化スクリプト（`01-init.sql`など）は、以下のメカニズムで自動実行されます：

1. `docker-compose.yml`で初期化スクリプトをマウント
   ```yaml
   volumes:
     - ./init/01-init.sql:/docker-entrypoint-initdb.d/01-init.sql
     - ./init/02-init-dev.sql:/docker-entrypoint-initdb.d/02-init-dev.sql
     - ./init/migrations:/docker-entrypoint-initdb.d/migrations
   ```

2. PostgreSQL公式イメージの仕様
   - `/docker-entrypoint-initdb.d/`ディレクトリ内のSQLファイルは
   - コンテナ初回起動時に自動的に実行される
   - ファイル名の昇順で実行される（01-、02-などのプレフィックスで制御）

3. 実行タイミング
   - コンテナの初回起動時のみ実行
   - 既存のデータベースが存在する場合は実行されない
   - 強制的に再実行する場合は、ボリュームを削除してコンテナを再作成する必要がある

### PowerShellスクリプト（start-postgres.ps1）

Windows環境でのPostgreSQLコンテナの起動と初期化を自動化するPowerShellスクリプトです。

#### 機能

1. 文字エンコーディング設定
   ```powershell
   [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
   $OutputEncoding = [System.Text.Encoding]::UTF8
   ```
   - 日本語対応のためのUTF-8エンコーディング設定

2. 初期化スクリプト生成
   - WSL環境で`generate-init.sh`を実行
   - 環境変数を反映した初期化SQLファイルを生成

3. コンテナ起動
   - `docker-compose up -d`でコンテナを起動
   - コンテナの起動完了を待機（10秒）

4. 初期化確認
   - 各テーブルのレコード数を表示
   - 正常に初期化されたことを確認

#### 使用方法

```powershell
# スクリプトの実行
.\start-postgres.ps1
```

#### 注意事項

- WSL環境が必要（`generate-init.sh`の実行のため）
- 実行前に`.env`ファイルが正しく設定されていることを確認
- コンテナが既に起動している場合は、一度停止してから実行することを推奨

### PowerShellスクリプト（stop-postgres.ps1）

PostgreSQLコンテナの停止とクリーンアップを行うPowerShellスクリプトです。

#### 機能

1. 文字エンコーディング設定
   - 日本語対応のためのUTF-8エンコーディング設定

2. コンテナ停止
   - `docker-compose down`でコンテナを停止
   - 関連するネットワークとボリュームを削除

3. クリーンアップ
   - 生成された初期化SQLファイルを削除
   - 一時ファイルのクリーンアップ

#### 使用方法

```powershell
# スクリプトの実行
.\stop-postgres.ps1
```

#### 注意事項

- 実行前にデータのバックアップを推奨
- コンテナの完全な停止とクリーンアップが行われる
- 次回起動時は初期化からやり直しとなる

### PowerShellスクリプト（check-postgres.ps1）

PostgreSQLコンテナの状態確認とデータベースの健全性チェックを行うPowerShellスクリプトです。

#### 機能

1. 文字エンコーディング設定
   - 日本語対応のためのUTF-8エンコーディング設定

2. コンテナ状態確認
   - コンテナの稼働状態確認
   - ヘルスチェックの実行

3. データベース確認
   - 接続テスト
   - テーブル一覧の表示
   - 各テーブルのレコード数表示
   - インデックスの状態確認

#### 使用方法

```powershell
# スクリプトの実行
.\check-postgres.ps1
```

#### 注意事項

- コンテナが起動している必要がある
- データベースへの接続権限が必要
- 定期的な実行による監視が推奨

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

## 更新履歴

| 日付 | バージョン | 更新内容 | 更新者 |
|------|------------|----------|--------|
| 2024-03-22 | 1.0.0 | 初版作成 | - |
| 2024-03-22 | 1.1.0 | 初期化プロセスの詳細化 | - |
| 2024-03-22 | 1.2.0 | PowerShellスクリプトの仕様追加 | - |
| 2024-03-22 | 1.3.0 | 目次更新と更新履歴追加 | - |

[🔝 ページトップへ](#postgresql環境構築データ管理設計書) 