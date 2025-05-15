# syllabus_backend
龍大のシラバス情報を集約して提供するバックエンド

## ディレクトリ構成

- `docs/`: プロジェクトのドキュメント
  - `database_structure.md`: データベース構造の定義
  - `database_policy.md`: データベース設計ポリシー
  - `database_er.md`: データベースER図
  - `server.md`: サーバー構成の説明
  - `docker_structure.md`: 本番環境のDocker構成
  - `docker_structure_develop.md`: 開発環境のDocker構成

- `src/`: ソースコード
  - `syllabus/`: シラバス
    - `2025/`: 年
        - `serarch_page/`: シラバスの解析済み検索画面を入れる
        - `syllabus_html/`: シラバスの生ページ
  - `course_guide/`: 要項
    - `2025/`: 年

- `docker/`: Docker関連ファイル
  - `api/`: APIサーバー用
    - `Dockerfile`: 本番用Dockerfile
    - `Dockerfile.dev`: 開発用Dockerfile
    - `requirements.txt`: Pythonパッケージ依存関係
  - `db/`: データベース用
    - `init.sql`: 初期化SQL

- `db/`: データベースファイル

## DB 構成
- [DB構成ポリシー](docs/database_policy.md)
- [DB構成仕様](docs/database_structure.md)
- [DB ER図](docs/database_er.md)

## サーバー構成
- [API仕様](docs/server.md)
- [Docker共通仕様](docs/docker.md)
- [本番環境Docker構成](docs/docker_structure.md)
- [開発環境Docker構成](docs/docker_structure_develop.md)

## 開発環境セットアップ
```bash
# 開発環境の起動
docker-compose -f docker-compose.dev.yml up -d

# 開発環境の停止
docker-compose -f docker-compose.dev.yml down
```

## 本番環境デプロイ
```bash
# 本番環境の起動
docker-compose up -d

# 本番環境の停止
docker-compose down
```