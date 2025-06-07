# FastAPI Docker環境

[readmeへ](../README.md) | [Docker設定へ](docker.md) | [PostgreSQL設定へ](postgresql.md)

## 目次
1. [概要](#概要)
2. [ディレクトリ構成](#ディレクトリ構成)
3. [環境変数](#環境変数)
4. [ボリュームマウント](#ボリュームマウント)
5. [API開発のワークフロー](#api開発のワークフロー)
6. [APIエンドポイント](#apiエンドポイント)
7. [セキュリティ対策](#セキュリティ対策)
8. [APIドキュメント](#apiドキュメント)
9. [ログ](#ログ)

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
| DATABASE_URL | PostgreSQLへの接続URL | postgresql://app:password@db:5433/syllabus |
| PYTHONPATH | Pythonパッケージの検索パス | /app |

## ボリュームマウント

| ホストパス | コンテナパス | 説明 |
|------------|--------------|------|
| ../../src | /app/src | ソースコード |
| ./pyproject.toml | /app/pyproject.toml | 依存関係定義 |

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
POST /api/query
```

#### リクエストボディ
```json
{
  "query": "SELECT * FROM syllabus WHERE year = ? AND semester = ?",
  "params": ["2025", "前期"]
}
```

#### レスポンス
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "year": "2025",
      "title": "プログラミング基礎",
      "semester": "前期"
    }
  ],
  "metadata": {
    "row_count": 1,
    "execution_time": "0.123s"
  }
}
```

### 制限事項
- Content-Type: application/json
- 最大リクエストサイズ: 1MB
- 1リクエストにつき1つのSQLクエリのみ実行可能
- セミコロン（;）による複数命令は禁止
- 1回のクエリで返却される最大行数：1000行
- クエリ実行の最大時間：30秒

## セキュリティ対策

### 1. パラメータ化されたクエリの使用
- すべてのユーザー入力は必ずパラメータとして渡す
- クエリ文字列への直接的な値の埋め込みは禁止

### 2. クエリの検証
- 構文解析による有効性確認
- 禁止操作のチェック
- 実行計画の検証

### 3. カラム指定の制限
```json
{
  "allowed_columns": {
    "syllabus": ["id", "year", "title", "teacher", "semester", "credit"],
    "departments": ["id", "name", "faculty"],
    "teachers": ["id", "name", "title"]
  }
}
```

### 4. LIKE句の保護
```json
{
  "suspicious_patterns": [
    "%--",
    "%';",
    "%;",
    "%/*",
    "%*/",
    "%@@"
  ]
}
```

### 5. レスポンスフィールドの制限
```json
{
  "default_views": {
    "syllabus_public": ["title", "teacher", "semester", "credit"],
    "syllabus_admin": ["*"],
    "teachers_public": ["name", "title"]
  }
}
```

### 6. 監査ログ
```json
{
  "timestamp": "2024-03-20T10:30:00Z",
  "level": "INFO",
  "event": "QUERY_EXECUTION",
  "details": {
    "query": "SELECT * FROM syllabus WHERE year = ?",
    "params": ["2025"],
    "execution_time": "0.123s",
    "query_analysis": {
      "used_wildcards": false,
      "used_functions": ["STRFTIME"],
      "selected_columns": ["*"],
      "table_access": ["syllabus"]
    },
    "client_info": {
      "ip": "192.168.1.100",
      "user_id": "user123",
      "access_level": "public"
    }
  }
}
```

### 7. 異常検知ルール
```json
{
  "function_limits": {
    "interval": "1hour",
    "thresholds": {
      "STRFTIME": 100,
      "UPPER": 50,
      "LOWER": 50,
      "COUNT": 200
    }
  }
}
```

### 8. ブロックポリシー
- 段階的な制限
  1. 警告ログの出力
  2. レート制限の強化
  3. 一時的なIPブロック
  4. アカウントの停止

## APIドキュメント

- Swagger UI: http://localhost:5000/docs
- ReDoc: http://localhost:5000/redoc

## ログ

- ログは標準出力に出力され、`docker-compose logs api`で確認可能
- ログレベルは環境変数`LOG_LEVEL`で制御（デフォルト: info）

## 更新履歴

| 日付 | バージョン | 更新者 | 内容 |
|------|------------|--------|------|
| 2024-03-20 | 1.0.0 | 藤原 | 初版作成 |

[🔝 ページトップへ](#fastapi-docker環境) 