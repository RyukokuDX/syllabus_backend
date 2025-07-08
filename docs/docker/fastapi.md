---
title: FastAPI環境構築ガイド
file_version: v3.0.0
project_version: v3.0.0
last_updated: 2025-07-08
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
  "query": "SELECT s.syllabus_id, sn.name AS 科目名, s.term AS 学期 FROM syllabus s JOIN syllabus_instructor si ON s.syllabus_id = si.syllabus_id JOIN instructor i ON si.instructor_id = i.instructor_id JOIN subject_name sn ON s.subject_name_id = sn.subject_name_id WHERE i.name = %s ORDER BY s.syllabus_id;",
  "params": ["藤原 和将"]
}
```

#### レスポンス
```json
{
  "results": [
    [
      13,
      "理工学のすすめ",
      "後期"
    ],
    [
      35,
      "数理情報基礎演習B",
      "後期"
    ],
    [
      37,
      "線形代数及び演習II",
      "後期"
    ],
    [
      47,
      "プロジェクト演習",
      "前期"
    ],
    [
      57,
      "数理情報演習",
      "1Q"
    ],
    [
      90,
      "セミナ-I",
      "後期"
    ],
    [
      111,
      "セミナ-II",
      "前期"
    ],
    [
      117,
      "特別研究I",
      "前期"
    ],
    [
      130,
      "特別研究II",
      "後期"
    ],
    [
      700,
      "数理解析特別講義II",
      "前期"
    ],
    [
      703,
      "数理解析特別研究",
      "通年"
    ],
    [
      718,
      "基礎解析特論I",
      "3Q"
    ],
    [
      719,
      "基礎解析特論II",
      "4Q"
    ],
    [
      732,
      "先端理工学基礎演習I",
      "前期"
    ],
    [
      745,
      "先端理工学基礎演習II",
      "後期"
    ],
    [
      758,
      "数理·情報科学特別研究",
      "前期"
    ],
    [
      771,
      "数理·情報科学特別研究",
      "後期"
    ],
    [
      782,
      "先端理工学研究(数理·情報科学コ-ス)",
      "通年"
    ],
    [
      785,
      "数理·情報科学演習",
      "前期"
    ],
    [
      798,
      "数理·情報科学演習",
      "後期"
    ]
  ],
  "execution_time": 0.022578954696655273,
  "row_count": 20
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