# syllabus_backend
龍大のシラバス情報を集約して提供するバックエンド

## 環境要件
- SQLite
  - DB構成は[DB構成](docs/database_structure.md)

## Cursorへの指示
- [Cursorへの指示書](docs/cursor.md)

## 更新作業
- 更新作業はjsonファイルを特定のディレクトリに格納し、
Curosrへ指示する事で処理します
詳細は[更新手順書](docs/database_update_workflow.md)

## ディレクトリ構成

- `docs/`: プロジェクトのドキュメント
  - `database_structure.md`: データベース構造の定義
  - `database_policy.md`: データベース設計ポリシー
  - `database_er.md`: データベースER図
  - `database_python.md`: データベースライブラリ仕様
  - `postgresql.md`: PostgreSQL仕様書
  - `server.md`: サーバー構成の説明
  - `docker.md`: Docker構成
  - `python/`: Pythonライブラリの仕様書
    - `database.md`: データベース操作クラスの仕様
    - `models.md`: データモデルの定義と使用方法
    - `update_db.md`: DB更新処理の仕様
    - `raw_page_parser.md`: シラバス検索ページパーサーの仕様

- `src/`: ソースコード
  - `__init__.py`: パッケージ定義
  - `db/`: データベース関連
    - `__init__.py`: データベースパッケージ定義
    - `models.py`: データベースモデル定義
    - `database.py`: データベース操作クラス
    - `raw_page_parser.py`: シラバス検索ページパーサー
    - `py.typed`: 型チェック用マーカー
  - `syllabus/`: シラバス
    - `2025/`: 年
      - `serarch_page/`: シラバスの解析済み検索画面を入れる
      - `syllabus_html/`: シラバスの生ページ
  - `course_guide/`: 要項
    - `2025/`: 年

- `docker/`: Docker関連ファイル
  - `api/`: APIサーバー用
    - `Dockerfile`: 本番用Dockerfile
    - `requirements.txt`: Pythonパッケージ依存関係

- `db/`: データベース関連ファイル
  - 設定ファイル（現在検討中）

## DB 構成
- [DB構成ポリシー](docs/database_policy.md)
- [DB構成仕様](docs/database_structure.md)
- [DB ER図](docs/database_er.md)
- [DBライブラリ仕様](docs/database_python.md)

## Pythonライブラリ
### データベース操作 [`database.py`](docs/python/database.md)
シングルトンパターンを使用したSQLiteデータベース操作クラス
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

### データ更新 [`update_db.py`](docs/python/update_db.md)
JSONファイルからデータベースを更新する処理
- データの整合性チェック
- バリデーション
- エラーハンドリング
- 処理済みファイルの自動アーカイブ

### パーサー [`raw_page_parser.py`](docs/python/raw_page_parser.md)
シラバス検索ページのパース処理
- HTMLパース
- データ抽出
- 正規化処理

## サーバー構成
- [API仕様](docs/server.md)
- [Docker構成](docs/docker.md)
