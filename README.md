# syllabus_backend
龍大のシラバス情報を集約して提供するバックエンド

## ディレクトリ構成

- `docs/`: プロジェクトのドキュメント
  - `database_structure.md`: データベース構造の定義
  - `database_policy.md`: データベース設計ポリシー
  - `database_er.md`: データベースER図
  - `database_python.md`: データベースライブラリ仕様
  - `server.md`: サーバー構成の説明
  - `docker.md`: Docker構成

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
    - `requirements.txt`: Pythonパッケージ依存関係

- `db/`: データベースファイル

## DB 構成
- [DB構成ポリシー](docs/database_policy.md)
- [DB構成仕様](docs/database_structure.md)
- [DB ER図](docs/database_er.md)
- [DBライブラリ仕様](docs/database_python.md)

## サーバー構成
- [API仕様](docs/server.md)
- [Docker構成](docs/docker.md)

## デプロイ方法
```bash
# 環境変数の設定
export DATABASE_URL="postgresql://user:password@your-db-host:5432/syllabus"

# コンテナのビルドと起動
docker-compose up -d --build

# コンテナの停止
docker-compose down
```

## 注意事項
- データベースは外部のマネージドサービスまたは専用サーバーを使用
- 環境変数は適切に管理
- セキュリティ設定を確認
- 定期的なバックアップを実施