FROM postgres:15-bullseye

# 日本語ロケールを生成する
RUN apt-get update && \
    apt-get install -y locales && \
    echo "ja_JP.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen ja_JP.UTF-8

# LANG 等は build 時には指定せず、環境変数としてデフォルトにするだけ
ENV LANG=ja_JP.UTF-8
ENV LC_ALL=ja_JP.UTF-8

# タイムゾーンを設定
ENV TZ=Asia/Tokyo

# PostgreSQLの設定をカスタマイズ
COPY postgresql.conf /etc/postgresql/postgresql.conf

CMD ["postgres", "-c", "config_file=/etc/postgresql/postgresql.conf"] 