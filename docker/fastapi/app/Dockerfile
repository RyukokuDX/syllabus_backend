FROM python:3.11-slim

WORKDIR /app

# システムの依存関係をインストール
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# アプリケーションディレクトリを作成
RUN mkdir -p /app/src /app/db /app/logs

# 必要なファイルをコピー
COPY ./docker/api/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY ./src /app/src/

# 実行時の設定
ENV PYTHONUNBUFFERED=1
ENV SQLITE_DB_PATH=/app/db/syllabus.db
ENV DEBUG_MODE=false
ENV LOG_LEVEL=info
ENV MAX_WORKERS=4
ENV RELOAD_MODE=false
ENV API_PREFIX=/api/v1
ENV CORS_ORIGINS=["http://localhost:3000"]
ENV CORS_ALLOW_CREDENTIALS=true

# ポートを公開
EXPOSE 5000

# ヘルスチェックの設定
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# アプリケーションを実行
CMD ["uvicorn", "src.main:app", \
     "--host", "0.0.0.0", \
     "--port", "5000", \
     "--workers", "4", \
     "--proxy-headers", \
     "--forwarded-allow-ips", "*"] 