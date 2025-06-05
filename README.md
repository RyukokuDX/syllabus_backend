# Syllabus Backend

## 概要
シラバス情報を管理するバックエンドシステム。Web Syllabusから取得したシラバス情報をデータベースに格納し、APIを通じて提供します。

### 主な機能
- Web Syllabusからのシラバス情報の取得と保存
- シラバス情報の検索・参照APIの提供
- データベースの自動更新とバックアップ
- 複数年度のシラバス情報の管理

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
  - SQLite（開発用）
- コンテナ開発
  - Docker
  - docker-compose
- ログ管理
  - ログディレクトリ（log/）
  - ログローテーション

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
1. リポジトリのクローン
```bash
git clone https://github.com/your-username/syllabus_backend.git
cd syllabus_backend
```

2. 仮想環境の作成と有効化
```bash
python -m venv venv
source venv/bin/activate  # Linuxの場合
venv\Scripts\activate     # Windowsの場合
```

3. 依存パッケージのインストール
```bash
pip install -r requirements.txt
```

4. データベースの初期化
```bash
# init.sql.templateをコピーしてinit.sqlを作成
cp init.sql.template init.sql
# データベースの初期化
python src/db/init_db.py
```

## 開発ガイドライン
- [データベース設計ポリシー](docs/database/policy.md)
- [API仕様](docs/api/openapi.yaml)
- [データベース構造定義](docs/database/structure.md)

## ライセンス
MIT License

## ドキュメント

### シェルスクリプト関連
- [syllabus.sh](docs/sh/syllabus.md) - メインシェルスクリプトの使用方法

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
