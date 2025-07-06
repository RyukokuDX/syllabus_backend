---
title: トラブルシューティングガイド
file_version: v2.7.0
project_version: v2.7.0
last_updated: 2025-07-06
---

# トラブルシューティングガイド

- File Version: v2.7.0
- Project Version: v2.7.0
- Last Updated: 2025-07-06

[readmeへ](../README.md) | [ドキュメント作成ガイドへ](./doc.md)

## 目次
1. [仮想環境関連のエラー](#仮想環境関連のエラー)
2. [Docker Compose関連のエラー](#docker-compose関連のエラー)
3. [データベース関連のエラー](#データベース関連のエラー)
4. [WSL環境での一般的な問題](#wsl環境での一般的な問題)
5. [よくある質問](#よくある質問)

## 仮想環境関連のエラー

### エラー1: ensurepip is not available

#### 症状
```bash
The virtual environment was not created successfully because ensurepip is not available.
On Debian/Ubuntu systems, you need to install the python3-venv package using the following command.
    apt install python3.11-venv
```

#### 原因
WSL環境でPython仮想環境作成に必要なパッケージがインストールされていない

#### 解決方法
1. WSL環境でパッケージを更新
   ```bash
   wsl sudo apt update
   ```

2. 必要なPython仮想環境パッケージをインストール
   ```bash
   wsl sudo apt install python3.11-venv python3.11-dev python3-pip
   ```

3. 既存の仮想環境を削除
   ```bash
   wsl rm -rf venv_syllabus_backend
   ```

4. 仮想環境を再初期化
   ```bash
   wsl ./syllabus.sh venv init
   ```

### エラー2: No module named pip

#### 症状
```bash
/mnt/c/github/syllabus_backend/venv_syllabus_backend/bin/python: No module named pip
```

#### 原因
仮想環境作成時にpipが正しくインストールされていない

#### 解決方法
1. 仮想環境を手動でアクティベート
   ```bash
   wsl bash -c "source venv_syllabus_backend/bin/activate && pip install -r requirements.txt"
   ```

2. または、仮想環境を再作成
   ```bash
   wsl rm -rf venv_syllabus_backend
   wsl ./syllabus.sh venv init
   ```

## Docker Compose関連のエラー

### エラー1: unknown shorthand flag: 'f' in -f

#### 症状
```bash
unknown shorthand flag: 'f' in -f
See 'docker --help'.
```

#### 原因
WSL環境で古いバージョンのDocker Compose（1.29.2）が使用されており、新しい`docker compose`コマンド（プラグイン版）が認識されていない

#### 解決方法

**方法1: スクリプトの修正（推奨）**
1. `bin/start-postgres.sh`を編集
2. 以下の行を変更：
   ```bash
   # 変更前
   docker compose -f docker-compose.yml up -d postgres-db
   
   # 変更後
   docker-compose -f docker-compose.yml up -d postgres-db
   ```

**方法2: Docker Compose v2のインストール**
1. Docker Compose v2（プラグイン版）をインストール
2. `docker compose`コマンドが使用可能になる

#### 確認方法
```bash
# 現在のDocker Composeバージョンを確認
wsl docker-compose --version

# Docker Compose v2が利用可能か確認
wsl docker compose version
```

## データベース関連のエラー

### エラー1: PostgreSQLコンテナが起動しない

#### 症状
- `./syllabus.sh -p start`実行時にエラーが発生
- PostgreSQLコンテナが起動しない

#### 原因
- Docker Composeコマンドの問題
- ポートの競合
- ディスク容量不足

#### 解決方法
1. Docker Composeの問題を解決（上記参照）
2. ポート競合の確認
   ```bash
   wsl netstat -tulpn | grep 5432
   ```
3. ディスク容量の確認
   ```bash
   wsl df -h
   ```

### エラー2: データベース接続エラー

#### 症状
```bash
psql: error: connection to server at "localhost" (127.0.0.1), port 5432 failed
```

#### 原因
- PostgreSQLコンテナが起動していない
- ポート設定の問題
- 認証情報の問題

#### 解決方法
1. コンテナの状態確認
   ```bash
   wsl docker ps
   ```

2. コンテナのログ確認
   ```bash
   wsl docker logs postgres-db
   ```

3. 環境変数ファイル（.env）の確認

## WSL環境での一般的な問題

### 問題1: 実行権限の問題

#### 症状
```bash
Permission denied: ./syllabus.sh
```

#### 解決方法
```bash
# 実行権限を付与
wsl chmod +x bin/*.sh
wsl chmod +x syllabus.sh

# または専用スクリプトを使用
wsl ./bin/restore-permissions.sh
```

### 問題2: パッケージリポジトリのGPGエラー

#### 症状
```bash
GPG エラー: https://packages.cloud.google.com/apt cloud-sdk InRelease: 公開鍵を利用できないため、以下の署名は検証できませんでした
```

#### 解決方法
このエラーは無視して問題ありません。必要なパッケージのインストールには影響しません。

### 問題3: PowerShellでのコマンド実行エラー

#### 症状
```bash
トークン '&&' は、このバージョンでは有効なステートメント区切りではありません
```

#### 解決方法
PowerShellでは`&&`が使えないため、以下のように実行：
```bash
# 誤った例
wsl source venv_syllabus_backend/bin/activate && pip install -r requirements.txt

# 正しい例
wsl bash -c "source venv_syllabus_backend/bin/activate && pip install -r requirements.txt"
```

## よくある質問

### Q1: 仮想環境の初期化が途中で止まる
**A:** ネットワーク接続の問題や依存関係のダウンロードに時間がかかっている可能性があります。しばらく待つか、Ctrl+Cで中断して再実行してください。

### Q2: Docker Composeのバージョンが古い
**A:** WSL環境では古いバージョンが使用されることがあります。`docker-compose`コマンドを使用するか、Docker Compose v2をインストールしてください。

### Q3: パッケージのインストールに失敗する
**A:** 以下を確認してください：
- インターネット接続
- ディスク容量
- パッケージリポジトリの状態

### Q4: WSL環境でのパフォーマンスが悪い
**A:** 以下を試してください：
- WSL2の使用確認
- メモリ割り当ての調整
- ウイルス対策ソフトの除外設定

## ログの確認方法

### Dockerログの確認
```bash
# PostgreSQLコンテナのログ
wsl docker logs postgres-db

# リアルタイムログ
wsl docker logs -f postgres-db
```

### システムログの確認
```bash
# WSLのシステムログ
wsl journalctl -xe

# Dockerのログ
wsl docker system info
```

## 緊急時の対処法

### 完全リセット
問題が解決しない場合、以下の手順で完全リセットできます：

1. すべてのコンテナを停止・削除
   ```bash
   wsl docker-compose down
   wsl docker system prune -a
   ```

2. 仮想環境を削除
   ```bash
   wsl rm -rf venv_syllabus_backend
   ```

3. 初期化スクリプトを再実行
   ```bash
   wsl ./syllabus.sh venv init
   wsl ./syllabus.sh -p start
   ```

[🔝 ページトップへ](#トラブルシューティングガイド) 