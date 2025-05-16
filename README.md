# syllabus_backend
龍大のシラバス情報を集約して提供するバックエンド

## ディレクトリ構成

- `docs/`: プロジェクトのドキュメント
  - `database_structure.md`: データベース構造の定義
  - `database_policy.md`: データベース設計ポリシー
  - `database_er.md`: データベースER図
  - `Server.md`: サーバー構成の説明

- `src/`: ソースコード
  - `syllabus/`: シラバス
    - `2025/`: 年
        - `serarch_page/`: シラバスの解析済み検索画面を入れる
        - `syllabus_html/`: シラバスの生ページ
  - `course_guide/`: 要項
    - `2025/`: 年

- `db/` : dbいれ

## DB 構成
- [DB構成ポリシー](docs/database_policy.md)
- [DB構成仕様](docs/database_structure.md)
- [DB ER図](docs/database_er.md)

## サーバー構成
[Server.md](Server.md)