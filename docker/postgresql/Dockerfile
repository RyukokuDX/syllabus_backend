FROM postgres:15-bullseye

# 日本語ロケールを生成する
RUN apt-get update && \
    apt-get install -y locales && \
    rm -rf /var/lib/apt/lists/* && \
    localedef -i ja_JP -c -f UTF-8 -A /usr/share/locale/locale.alias ja_JP.UTF-8

# LANG 等は build 時には指定せず、環境変数としてデフォルトにするだけ
ENV LANG=ja_JP.UTF-8
ENV LC_ALL=ja_JP.UTF-8

# タイムゾーンを設定
ENV TZ=Asia/Tokyo

# PostgreSQLの設定をカスタマイズ
COPY postgresql.conf /etc/postgresql/postgresql.conf

# マイグレーションスクリプトをコピー
COPY ./init/init.sh /docker-entrypoint-initdb.d/03-run-migrations.sh
RUN chmod +x /docker-entrypoint-initdb.d/03-run-migrations.sh

CMD ["postgres", "-c", "config_file=/etc/postgresql/postgresql.conf"] 