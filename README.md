# シラバス管理システム バックエンド

## プロジェクト構成
```
.
├── docker/
│   ├── fastapi/      # FastAPIアプリケーションコンテナ
│   └── postgresql/   # PostgreSQLコンテナ
└── src/
    └── db/          # データベース関連スクリプト
```

## 環境構築

### 1. ホスト環境のセットアップ
データベースマイグレーション用の環境をセットアップします：

```bash
# 必要なパッケージのインストール
cd src/db
pip install -r requirements.txt
```

### 2. Dockerコンテナの起動
```bash
docker-compose up -d
```

## データベースマイグレーション

### マイグレーションの実行
```bash
# デフォルトデータベース（master_db）に対してマイグレーションを実行
python src/db/migrations/manual_migrate.py

# 特定のデータベースに対してマイグレーションを実行
python src/db/migrations/manual_migrate.py [database_name]
```

### 環境変数
マイグレーションスクリプトは以下の環境変数を使用します：
- `POSTGRES_HOST`: データベースホスト（デフォルト: localhost）
- `POSTGRES_PORT`: データベースポート（デフォルト: 5432）
- `POSTGRES_USER`: データベースユーザー（デフォルト: postgres）
- `POSTGRES_PASSWORD`: データベースパスワード（デフォルト: postgres）

## Cursorへの指示
- [Cursorへの指示書](docs/cursor.md)

## 更新作業
- 更新作業はjsonファイルを特定のディレクトリに格納し、
pythonで更新をかけるかCurosrへ指示する事で処理します
詳細は[更新手順書](docs/database/updateflow.md)

## ディレクトリ構成

- `docs/`: プロジェクトのドキュメント
  - `database/`: データベース関連ドキュメント
    - `structure.md`: データベース構造の定義
    - `policy.md`: データベース設計ポリシー
    - `er.md`: データベースER図
    - `python.md`: データベースライブラリ仕様
  - `docker/`: Docker関連ドキュメント
    - `postgresql.md`: PostgreSQL仕様書
    - `fastapi.md`: FastAPI構成仕様書
  - `python/`: Pythonライブラリの仕様書
    - `database.md`: データベース操作クラスの仕様
    - `models.md`: データモデルの定義と使用方法
    - `generate_migration.py.md`: マイグレーションファイル生成スクリプトの仕様
    - `raw_page_parser.md`: シラバス検索ページパーサーの仕様

- `src/`: ソースコード
  - `__init__.py`: パッケージ定義
  - `db/`: データベース関連
    - `__init__.py`: データベースパッケージ定義
    - `models.py`: データベースモデル定義
    - `database.py`: データベース操作クラス
    - `migrations/`: マイグレーション関連
      - `generate_migration.py`: マイグレーションファイル生成スクリプト
    - `raw_page_parser.py`: シラバス検索ページパーサー
    - `py.typed`: 型チェック用マーカー
  - `syllabus/`: シラバス
    - `2025/`: 年
      - `search_page/`: シラバスの解析済み検索画面を入れる
      - `syllabus_html/`: シラバスの生ページ
  - `course_guide/`: 要項
    - `2025/`: 年

- `docker/`: Docker関連ファイル
  - `api/`: APIサーバー用
    - `Dockerfile`: 本番用Dockerfile
    - `requirements.txt`: Pythonパッケージ依存関係
  - `postgresql/`: PostgreSQL用
    - `init/`: 初期化スクリプト
      - `migrations/`: マイグレーションファイル
    - `Dockerfile`: PostgreSQL用Dockerfile

- `updates/`: 更新用JSONファイル
  - `subject/`: 科目情報
    - `add/`: 追加データ
    - `update/`: 更新データ
    - `delete/`: 削除データ

## DB 構成
- [DB構成ポリシー](docs/database/policy.md)
- [DB構成仕様](docs/database/structure.md)
- [DB ER図](docs/database/er.md)

## Pythonライブラリ

### データベース操作 [`database.py`](docs/python/database.md)
シングルトンパターンを使用したPostgreSQLデータベース操作クラス
- 接続管理
- トランザクション制御
- エラーハンドリング

### データモデル [`models.py`](docs/python/models.md)
SQLAlchemyを使用したデータモデル定義
- 科目情報（Subject）
- シラバス情報（Syllabus）
- 講義時間（SyllabusTime）
- 教員情報（Instructor）
- 書籍情報（Book）
- 成績評価基準（GradingCriterion）
- その他関連テーブル

### マイグレーション実行 [`manual_migrate.py`](docs/python/manual_migrate.md)
SQLマイグレーションファイルを実行する処理
- マイグレーションファイルの自動検出
- トランザクション管理
- 複数データベース対応

### マイグレーション [`generate_migration.py`](docs/python/generate_migration.py.md)
JSONファイルからSQLマイグレーションファイルを生成する処理
- JSONファイルの読み込み
- SQLマイグレーションファイルの生成
- UPSERTに対応

### パーサー [`raw_page_parser.py`](docs/python/raw_page_parser.md)
シラバス検索ページのパース処理
- HTMLパース
- データ抽出
- 正規化処理

## Docker構成
- [FastAPI構成](docs/docker/fastapi.md)
- [PostgreSQL構成](docs/docker/postgresql.md)
