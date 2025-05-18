FROM postgres:15-alpine

# タイムゾーンを設定
ENV TZ=Asia/Tokyo

# 初期化スクリプトをコピー
COPY ./docker-entrypoint-initdb.d/ /docker-entrypoint-initdb.d/

# PostgreSQLの設定をカスタマイズ
COPY postgresql.conf /etc/postgresql/postgresql.conf

CMD ["postgres", "-c", "config_file=/etc/postgresql/postgresql.conf"] 