# 本番環境のDocker構成
[readmeへ](../README.md)

## 概要
本番環境用のDocker構成について説明します。

## コンテナ構成

### APIサーバー（FastAPI）
- イメージ: `python:3.11-slim`
- ポート: 8000
- 環境変数:
  - `DATABASE_URL`: 本番DB接続情報
  - `DEBUG_MODE`: false
  - `LOG_LEVEL`: info

## ディレクトリ構造
```
.
├── docker-compose.yml
└── docker/
    └── api/
        ├── Dockerfile
        └── requirements.txt
```

## Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 依存関係のインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションのコピー
COPY . .

# ヘルスチェック設定
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# 実行コマンド
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## docker-compose.yml
```yaml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: docker/api/Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - DEBUG_MODE=false
      - LOG_LEVEL=info
    restart: unless-stopped
```

## 本番環境での注意事項

### セキュリティ
- 環境変数は適切に管理
- シークレット管理サービスの使用
- SSL/TLS暗号化の強制
- 定期的なセキュリティアップデート

### データベース接続
- 接続情報は環境変数で管理
- コネクションプールの適切な設定

### 監視設定
- アプリケーションログの集中管理
- メトリクスの収集
- アラートの設定
- パフォーマンスモニタリング

### バックアップ
- データベースの定期バックアップ
- バックアップの自動化
- リストア手順の整備

[トップへ](#)