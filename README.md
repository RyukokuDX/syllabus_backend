# syllabus_backend
龍大のシラバス情報を集約して提供するバックエンド

## 環境要件
- PostgreSQL 17.5
  - 詳細な仕様は[PostgreSQL仕様書](docs/postgresql.md)を参照

## セットアップ手順
1. PostgreSQLのインストール
   - [PostgreSQL 17.5](https://www.postgresql.org/download/windows/)をダウンロードしてインストール
   - インストール時の設定：
     - ポート: 5432
     - パスワード: syllabus（開発環境用）
     - ロケール: Japanese, Japan

2. データベースの作成
   ```bash
   # PostgreSQLにログイン
   psql -U postgres
   
   # データベースを作成
   CREATE DATABASE syllabus;
   ```

3. テーブルの作成
   ```bash
   # 必要なパッケージのインストール
   pip install sqlalchemy psycopg2-binary

   # データベーステーブルの作成
   cd src/db
   python create_database.py
   ```

## ディレクトリ構成

- `docs/`: プロジェクトのドキュメント
  - `database_structure.md`: データベース構造の定義
  - `database_policy.md`: データベース設計ポリシー
  - `database_er.md`: データベースER図
  - `database_python.md`: データベースライブラリ仕様
  - `postgresql.md`: PostgreSQL仕様書
  - `server.md`: サーバー構成の説明
  - `docker.md`: Docker構成

- `src/`: ソースコード
  - `__init__.py`: パッケージ定義
  - `db/`: データベース関連
    - `__init__.py`: データベースパッケージ定義
    - `models.py`: データベースモデル定義
    - `database.py`: データベース操作クラス
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
- [PostgreSQL仕様書](docs/postgresql.md)
- [DB構成ポリシー](docs/database_policy.md)
- [DB構成仕様](docs/database_structure.md)
- [DB ER図](docs/database_er.md)
- [DBライブラリ仕様](docs/database_python.md)

## データベース接続情報（開発環境）
```
Host: localhost
Port: 5432
Database: syllabus
Username: postgres
Password: syllabus
```

## サーバー構成
- [API仕様](docs/server.md)
- [Docker構成](docs/docker.md)

## デプロイ方法
※ データベース設定は現在検討中です。詳細は[PostgreSQL仕様書](docs/postgresql.md)を参照してください。

## 注意事項
- データベースは外部のマネージドサービスまたは専用サーバーを使用
- 環境変数は適切に管理
- セキュリティ設定を確認
- 定期的なバックアップを実施