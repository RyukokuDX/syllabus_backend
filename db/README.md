# データベース関連ファイル

## ファイル構成
- `.env`: データベース接続情報（git管理対象外）
  ```
  DATABASE_URL="postgresql://postgres:syllabus@localhost:5432/syllabus"
  ```

## 開発環境でのデータベース情報
- データベース: PostgreSQL 17.5
- 接続情報:
  - ホスト: localhost
  - ポート: 5432
  - データベース名: syllabus
  - ユーザー名: postgres
  - パスワード: syllabus（開発環境用）

## データベース管理
- バックアップ方法:
  ```bash
  # データベースのバックアップ
  pg_dump -U postgres -d syllabus > backup.sql

  # データベースのリストア
  psql -U postgres -d syllabus < backup.sql
  ```

## 注意事項
- `.env`ファイルはgit管理対象外です
- 本番環境では適切なパスワードに変更してください
- 定期的なバックアップを推奨します 