---
title: FastAPI環境構築ガイド
file_version: v2.7.1
project_version: v2.7.1
last_updated: 2025-07-06
---

# FastAPI Docker環境

[readmeへ](../README.md) | [Docker設定へ](docker.md) | [PostgreSQL設定へ](postgresql.md)

## 目次
1. [概要](#概要)
2. [ディレクトリ構成](#ディレクトリ構成)
3. [環境変数](#環境変数)
4. [ボリュームマウント](#ボリュームマウント)
5. [DBテーブル構成](#dbテーブル構成)
6. [API開発のワークフロー](#api開発のワークフロー)
7. [APIエンドポイント](#apiエンドポイント)
8. [セキュリティ対策](#セキュリティ対策)
9. [APIドキュメント](#apiドキュメント)
10. [ログ](#ログ)

## 概要

FastAPIを使用したAPIサーバーの環境構成について説明します。

## ディレクトリ構成

```
docker/fastapi/
├── app/               # アプリケーション設定
├── Dockerfile         # FastAPI用Dockerfile
├── docker-compose.yml # FastAPI用compose設定
└── pyproject.toml     # Poetry依存関係定義

src/                   # アプリケーションソース
├── main.py           # アプリケーションのエントリーポイント
├── models/           # データモデル定義
├── routes/           # APIルート定義
├── schemas/          # Pydanticスキーマ
└── utils/            # ユーティリティ関数
```

## 環境変数

| 変数名 | 説明 | デフォルト値 |
|--------|------|--------------|
| DATABASE_URL | PostgreSQLへの接続URL | postgresql://postgres:postgres@postgres-db:5432/syllabus_db |
| PYTHONPATH | Pythonパッケージの検索パス | /app |

## ボリュームマウント

| ホストパス | コンテナパス | 説明 |
|------------|--------------|------|
| ../../src | /app/src | ソースコード |
| ./pyproject.toml | /app/pyproject.toml | 依存関係定義 |

## DBテーブル構成

- テーブル・カラム名は[docs/database/structure.md](../database/structure.md)に厳密に準拠
- 例: class, subclass, faculty, subject_name, instructor, syllabus_master, book, book_uncategorized, syllabus, subject_grade, lecture_time, lecture_session, lecture_session_irregular, syllabus_instructor, lecture_session_instructor, syllabus_book, grading_criterion, subject_attribute, subject, subject_attribute_value, syllabus_faculty, syllabus_study_system など
- 各テーブルの詳細はstructure.mdを参照

## API開発のワークフロー

1. ソースコードの変更
   - `src`ディレクトリ内のコードを編集
   - ホットリロードにより自動で反映

2. 依存関係の追加
   ```bash
   docker-compose exec api poetry add <package-name>
   ```

3. マイグレーションの実行
   ```bash
   docker-compose exec api poetry run alembic upgrade head
   ```

4. テストの実行
   ```bash
   docker-compose exec api poetry run pytest
   ```

## APIエンドポイント

### SQLクエリ実行

#### エンドポイント
```
POST /api/v1/query
```

#### リクエストボディ
```json
{
  "query": "SELECT * FROM subject WHERE faculty_id = ? AND curriculum_year = ?",
  "params": [1, 2025]
}
```

#### レスポンス
```json
{
  "results": [
    {
      "subject_id": 1,
      "subject_name_id": 1,
      "faculty_id": 1,
      "curriculum_year": 2025,
      "class_id": 1,
      "subclass_id": 2,
      "requirement_type": "必修",
      "created_at": "2025-07-06T12:00:00Z",
      "updated_at": "2025-07-06T12:00:00Z"
    }
  ],
  "execution_time": 0.123,
  "row_count": 1
}
```

### 制限事項
- Content-Type: application/json
- 最大リクエストサイズ: 1MB
- 1リクエストにつき1つのSQLクエリのみ実行可能
- セミコロン（;）による複数命令は禁止
- 1回のクエリで返却される最大行数：1000行
- クエリ実行の最大時間：30秒
- テーブル・カラム名はstructure.mdの定義に厳密に従うこと

## セキュリティ対策

### 1. パラメータ化されたクエリの使用
- すべてのユーザー入力は必ずパラメータとして渡す
- クエリ文字列への直接的な値の埋め込みは禁止

### 2. クエリの検証
- 構文解析による有効性確認
- 禁止操作のチェック
- 実行計画の検証

### 3. カラム指定の制限
- structure.mdに記載されたカラムのみ許可

### 4. LIKE句の保護
- 危険なパターン（%--, %';, %;, %/*, %*/, %@@ など）を検出し拒否

### 5. レスポンスフィールドの制限
- structure.mdに記載されたカラムのみ返却

### 6. 監査ログ
- すべてのクエリ実行を監査ログに記録

### 7. 異常検知ルール
- クエリ頻度や関数利用回数に応じてレート制限・警告・ブロックを段階的に実施

## APIドキュメント

- Swagger UI: http://localhost:5000/docs
- ReDoc: http://localhost:5000/redoc

## ログ

- ログは標準出力およびlogs/api.logに出力
- ログレベルは環境変数`LOG_LEVEL`で制御（デフォルト: info）

## 更新履歴

| 日付 | バージョン | 更新者 | 内容 |
|------|------------|--------|------|
| 2025-07-06 | 2.7.1 | 藤原 | structure.mdに準拠したテーブル・カラム・API例・制約に更新 |

[🔝 ページトップへ](#fastapi-docker環境) 