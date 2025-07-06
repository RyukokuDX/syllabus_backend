---
title: Syllabus Backend
file_version: v2.7.0
project_version: v2.7.0
last_updated: 2025-07-06
---

# Syllabus Backend

- File Version: v2.7.0
- Project Version: v2.7.0
- Last Updated: 2025-07-06

## 概要
シラバス情報を管理するバックエンドシステム。Web Syllabusから取得したシラバス情報をデータベースに格納し、APIを通じて提供します。

### 主な機能
- Web Syllabusからのシラバス情報の取得と保存
- シラバス情報の検索・参照APIの提供
- データベースの自動更新とバックアップ
- 複数年度のシラバス情報の管理
- JSONBキャッシュによる高速検索機能
- マルチプラットフォーム対応（Linux、macOS）

### システム構成
- バックエンド: FastAPI (Python 3.11)
  - APIサーバー
  - バッチ処理（Pythonスクリプト）
  - 監視・ログ（Docker logs）
- データベース: PostgreSQL
  - データベースサーバー
  - バックアップ
- コンテナ化: Docker
  - コンテナ管理
  - 環境分離

### 開発環境
- バックエンド開発
  - Python 3.11
  - FastAPI
  - 仮想環境（venv）
- データベース開発
  - PostgreSQL
- コンテナ開発
  - Docker
  - docker-compose
- ログ管理
  - ログディレクトリ（log/）
  - ログローテーション
- マルチプラットフォーム対応
  - Linux（Ubuntu、CentOS等）
  - macOS（Darwin）

### 運用環境
- VPN内のサーバーで運用
- 手動デプロイによる更新
- バックアップはVPN内のストレージに保存

## ディレクトリ構造
```
.
├── .github/                  # GitHub設定
├── .gitignore               # Git除外設定
├── .dockerignore           # Docker除外設定
├── docs/                    # ドキュメント
│   ├── database/           # データベース関連
│   ├── python/             # Python関連
│   ├── docker/             # Docker関連
│   └── sh/                 # シェルスクリプト関連
├── docker/                  # Docker関連
│   ├── postgresql/         # PostgreSQL設定
│   │   ├── init/          # 初期化スクリプト
│   │   ├── Dockerfile     # PostgreSQL用Dockerfile
│   │   ├── postgresql.conf # PostgreSQL設定ファイル
│   │   ├── docker-compose.yml # PostgreSQL用docker-compose
│   │   ├── generate-init.sh   # 初期化スクリプト生成
│   │   ├── start-postgres.ps1 # 起動スクリプト
│   │   ├── stop-postgres.ps1  # 停止スクリプト
│   │   ├── check-postgres.ps1 # 状態確認スクリプト
│   │   └── check-with-dev-db.ps1 # 開発DB確認スクリプト
│   └── fastapi/            # FastAPI設定
│       ├── app/            # アプリケーションコード
│       ├── Dockerfile      # FastAPI用Dockerfile
│       ├── docker-compose.yml # FastAPI用docker-compose
│       └── pyproject.toml  # Pythonプロジェクト設定
├── src/                     # ソースコード
│   ├── db/                 # データベース関連
│   ├── course_guide/       # 要項関連
│   ├── syllabus/           # シラバス関連
│   └── __init__.py         # パッケージ定義
├── python/                  # Pythonスクリプト
├── log/                     # ログファイル
├── updates/                 # 更新用ファイル
├── init.sql.template       # データベース初期化テンプレート
├── syllabus.sh             # メインシェルスクリプト
└── README.md               # 本ドキュメント
```

## セットアップ
### 前提
#### Windows
wslの利用を前提

### 手順
1. リポジトリのクローン
```bash
git clone https://github.com/your-username/syllabus_backend.git
cd syllabus_backend
```

2. 環境設定ファイルの準備
```bash
# .envファイルをコピーして編集
cp .env.example .env
# 必要に応じて.envファイルの設定を編集
```

3. 実行権限の復元（macOSの場合）
```bash
# macOSでクローンした場合、実行権限が失われている可能性があります
chmod +x bin/*.sh
chmod +x syllabus.sh
# または専用スクリプトを使用
./bin/restore-permissions.sh
```

4. 仮想環境の作成と初期化
```bash
./syllabus.sh venv init
```

5. データベースの起動
```bash
./syllabus.sh -p start
```

6. データベースの起動確認
```bash
./syllabus.sh -p records
```
7. キャッシュの生成（推奨）
```bash
# シラバスキャッシュを生成（検索性能向上のため）
./syllabus.sh -p cache generate subject_syllabus_cache
./syllabus.sh -p cache generate catalogue

# キャッシュの状態を確認
./syllabus.sh -p cache status

# 利用可能なキャッシュ一覧を表示
./syllabus.sh -p cache list
```

8. OS互換性の確認（オプション）
```bash
# OS互換性テストを実行
./syllabus.sh test-os
```

## 開発ガイドライン
- [データベース設計ポリシー](docs/database/policy.md)
- [API仕様](docs/api/openapi.yaml)
- [データベース構造定義](docs/database/structure.md)
- [キャッシュ構造定義](docs/database/jsonb_cache.md)

### Cursor関連
- `.cursor/querry.mdc` - PostgreSQL+jsonbクエリ作成ルール
  - jsonbキャッシュの仕様は docs/database/jsonb_cache.md を参照
  - 属性値カタログ（AV catalogue）は `./syllabus.sh -p cache get catalogue` で取得
  - クエリ作成時は上記カタログ・仕様を必ず参照すること
- `.cursor/rules/` - Cursor IDEの追加ルール設定ディレクトリ
  - `git.mdc` - Git操作に関するルール設定
  - `general-rule.mdc` - 一般的な開発ルール設定
  - これらのファイルは、Cursor IDEでの開発効率を向上させるための設定を含みます
  - チーム開発時の一貫性を保つために使用されます
  - 開発者はこれらのルールに従って作業を行う必要があります

## ライセンス
MIT License

## ドキュメント

### シェルスクリプト関連
- [syllabus.sh](docs/sh/syllabus.md) - メインシェルスクリプトの使用方法
- [git_bump.sh](docs/sh/git_bump.md) - バージョン管理スクリプトの使用方法
- [OS互換性](docs/sh/os_compatibility.md) - マルチプラットフォーム対応について

### データベース関連
- [ER図](docs/database/er.md) - データベースのER図
- [設計ポリシー](docs/database/policy.md) - データベース設計のポリシー
- [構造定義](docs/database/structure.md) - データベースの構造定義

### Docker関連
- [Docker基本](docs/docker/docker.md) - Dockerの基本設定と使用方法
- [PostgreSQL](docs/docker/postgresql.md) - PostgreSQLの設定と使用方法
- [FastAPI](docs/docker/fastapi.md) - FastAPIの設定と使用方法

### Python関連
- [モデル定義](docs/python/models.md) - データベースモデルの定義
- [マイグレーション生成](docs/python/generate_migration.py.md) - マイグレーションファイルの生成方法
- [手動マイグレーション](docs/python/manual_migrate.md) - 手動マイグレーションの手順

### その他
- [ドキュメント作成ガイド](docs/doc.md) - ドキュメント作成のガイドライン
- [トラブルシューティングガイド](docs/trouble_shoot.md) - よくある問題と解決方法

### Git更新手順
1. バージョン更新
   ```bash
   git bump
   ```

2. Cursorへの commit_msg 変更依頼
   - Cursor IDEで commit_msg を開き、変更内容を確認・編集

3. 変更のコミット
   ```bash
   git fcom
   ```

### コミットメッセージのプレフィックス
- `feat:` - 新機能
- `fix:` - バグ修正
- `docs:` - ドキュメントの変更
- `style:` - コードの意味に影響を与えない変更
- `refactor:` - バグ修正や機能追加を含まないコードの変更
- `test:` - テストの追加・修正
- `chore:` - ビルドプロセスやツールの変更
