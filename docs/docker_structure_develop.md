# 開発環境のDocker構成
[readmeへ](../README.md)

## 概要
開発環境用のDocker構成について説明します。

## コンテナ構成

### APIサーバー（FastAPI）
- イメージ: `python:3.11-slim`
- ポート: 8000
- 環境変数:
  - `DATABASE_URL`: PostgreSQL接続情報
  - `DEBUG_MODE`: true
  - `LOG_LEVEL`: debug

### データベース（PostgreSQL）
- イメージ: `postgres:15`
- ポート: 5432
- 環境変数:
  - `POSTGRES_USER`
  - `POSTGRES_PASSWORD`
  - `POSTGRES_DB`

## ディレクトリ構造
```
.
├── docker-compose.dev.yml
└── docker/
    ├── api/
    │   ├── Dockerfile.dev
    │   └── requirements.txt
    └── db/
        └── init.sql
```

## Dockerfile.dev
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 開発用パッケージのインストール
RUN pip install --no-cache-dir pytest pytest-cov black flake8

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

## docker-compose.dev.yml
```yaml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: docker/api/Dockerfile.dev
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/syllabus
      - DEBUG_MODE=true
      - LOG_LEVEL=debug
    volumes:
      - ./src:/app/src
    depends_on:
      - db
    restart: unless-stopped

  db:
    image: postgres:15
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=syllabus
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./docker/db/init.sql:/docker-entrypoint-initdb.d/init.sql

volumes:
  postgres_data:
```

## 開発環境での実行方法

1. 環境構築
```bash
docker-compose -f docker-compose.dev.yml build
```

2. コンテナ起動
```bash
docker-compose -f docker-compose.dev.yml up -d
```

3. ログの確認
```bash
docker-compose -f docker-compose.dev.yml logs -f
```

4. コンテナの停止
```bash
docker-compose -f docker-compose.dev.yml down
```

## 開発時の注意事項
- ホットリロードが有効
- デバッグモードが有効
- テスト用ツールが利用可能
- データベースポートがローカルホストに公開 

[トップへ](#)