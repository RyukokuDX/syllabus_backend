# Docker環境構築仕様書

[readmeへ](../README.md) | [サーバー構成へ](server.md) 

## 目次
1. [概要](#概要)
2. [前提条件](#前提条件)
3. [ディレクトリ構成](#ディレクトリ構成)
4. [コンテナ構成](#コンテナ構成)
5. [環境変数](#環境変数)
6. [ビルド手順](#ビルド手順)
7. [運用手順](#運用手順)
8. [トラブルシューティング](#トラブルシューティング)

## 概要
FastAPIアプリケーションをコンテナ化して提供するための構成です。
データベースはSQLiteを使用し、データファイルはボリュームマウントで永続化します。

## ディレクトリ構造
```
.
├── docker-compose.yml
└── docker/
    └── api/
        ├── Dockerfile
        └── requirements.txt
```

## 必要なパッケージ

### Pythonパッケージ（本番環境用）
- Web Framework
  - fastapi==0.109.0
    - 高速なAPIフレームワーク
    - OpenAPI（Swagger）ドキュメント自動生成
    - 型ヒントによる自動バリデーション
    - JSONリクエスト/レスポンスの自動処理
  - uvicorn==0.27.0
    - ASGIサーバー
    - 高パフォーマンスなサーバー実装
  - pydantic==2.5.3
    - データバリデーション
    - 設定管理
    - JSONシリアライズ/デシリアライズ
    - SQLクエリのパラメータバリデーション
  - pydantic-settings==2.1.0
    - 環境変数からの設定読み込み
    - 設定値の型チェック

- データベース
  - sqlalchemy==2.0.25
    - ORMマッパー
    - SQLクエリビルダー
    - データベース抽象化レイヤー
  - alembic==1.13.1
    - データベースマイグレーション
    - スキーマバージョン管理

- ユーティリティ
  - python-dotenv==1.0.0
    - .env ファイルの読み込み
    - 環境変数管理
  - requests==2.31.0
    - HTTP通信
    - 外部APIとの連携
  - httpx==0.26.0
    - 非同期HTTP通信
  - typing-extensions==4.9.0
    - 高度な型ヒント機能
    - Python3.7以降の型機能の下位互換性

- ロギング・モニタリング
  - loguru==0.7.2
    - 構造化ログ出力
    - ログローテーション
    - エラートレース出力
  - prometheus-client==0.19.0
    - メトリクス収集
    - パフォーマンスモニタリング
  - uvicorn-prometheus==0.5.0
    - Uvicornのメトリクス収集
    - リクエスト統計
  - python-json-logger==2.0.7
    - JSON形式でのログ出力
    - ログの構造化

- ヘルスチェック
  - fastapi-health==0.4.0
    - エンドポイントのヘルスチェック
    - 依存サービスの状態確認
    - カスタムヘルスチェックの実装
  - APScheduler==3.10.4
    - 定期的なヘルスチェック実行
    - バックグラウンドタスク管理
    - クロン形式のスケジュール設定

## コンテナ構成

### APIサーバー（FastAPI）
- イメージ: `python:3.11-slim`
- ポート: 8000
- ボリューム:
  - `./db:/app/db`: SQLiteデータベースファイル
  - `./logs:/app/logs`: ログファイル
- 環境変数:
  - `SQLITE_DB_PATH`: /app/db/syllabus.db
  - `DEBUG_MODE`: false
  - `LOG_LEVEL`: info

## Docker Compose設定例

```yaml
version: '3.8'

services:
  api:
    build:
      context: ./docker/api
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    volumes:
      - ./db:/app/db
      - ./logs:/app/logs
    environment:
      - SQLITE_DB_PATH=/app/db/syllabus.db
      - DEBUG_MODE=false
      - LOG_LEVEL=info
    restart: unless-stopped
```

## ヘルスチェック設定

### エンドポイント
```python
# health_check.py
from fastapi_health import health

async def db_health_check():
    # SQLite接続確認
    return True

async def api_health_check():
    # API全体の状態確認
    return True

app.add_api_route("/health", health([db_health_check, api_health_check]))
```

### 定期チェック
```python
# scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

scheduler = AsyncIOScheduler()

# 5分ごとのヘルスチェック
@scheduler.scheduled_job(CronTrigger(minute='*/5'))
async def periodic_health_check():
    # ヘルスチェック実行
    pass

# メモリ使用量監視
@scheduler.scheduled_job(CronTrigger(minute='*/15'))
async def monitor_memory():
    # メモリ使用量確認
    pass

scheduler.start()
```

## ログ設定

### JSON形式ログ
```python
# logging_config.py
from pythonjsonlogger import jsonlogger
import logging

def setup_logging():
    json_handler = logging.StreamHandler()
    json_handler.setFormatter(
        jsonlogger.JsonFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s'
        )
    )
    logging.getLogger().addHandler(json_handler)
```

### Prometheusメトリクス
```python
# metrics.py
from prometheus_client import Counter, Histogram

http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)
```

## 更新履歴

| 日付 | バージョン | 更新者 | 内容 |
|------|------------|--------|------|
| 2024-03-20 | 1.0.0 | 藤原 | 初版作成 |
| 2024-03-20 | 1.1.0 | 藤原 | PostgreSQLからSQLiteに変更 |

[🔝 ページトップへ](#docker環境構築仕様書)