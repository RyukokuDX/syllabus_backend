<!--
更新時の注意事項:
- 準拠とは、類推せずに内容に従うこと
- 更新は docs/doc.md に準拠すること
-->

# syllabus.sh

- File Version: v2.6.0
- Project Version: v2.6.0
- Last Updated: 2025-07-05

[readmeへ](../README.md) | [ドキュメント作成ガイドラインへ](../doc.md)

メインのシェルスクリプト。PostgreSQLとFastAPIサービスの管理を統一的に行うためのインターフェースを提供します。

## 目次
1. [使用方法](#使用方法)
2. [オプション](#オプション)
3. [コマンド](#コマンド)
4. [使用例](#使用例)
5. [注意事項](#注意事項)
6. [OS互換性](#os互換性)
7. [関連スクリプト](#関連スクリプト)
8. [更新履歴](#更新履歴)

## 使用方法

```bash
./syllabus.sh [OPTIONS] COMMAND [ARGS]
```

### オプション

- `-p, --postgresql`: PostgreSQLサービスを操作
- `-g, --git`: Gitサービスを操作
- `-m, --mcp`: mcpサービスを操作
- `-h, --help`: ヘルプメッセージを表示

### コマンド

#### 【共通コマンド】

- `help`: ヘルプメッセージを表示
- `version`: syllabus.shのバージョンを表示
- `version <file>`: 指定されたファイルの更新履歴を表示
- `venv init`: Python仮想環境の初期化
- `csv normalize`: 指定年度のCSVファイルを整形（区切り文字をタブに、空白を削除、科目名・課程名を正規化）
- `parser`: 指定されたテーブルのパーサースクリプトを実行（引数必須）
- `test-os`: OS互換性テストを実行

#### 【-p, --postgresql サービスコマンド】

- `start`: 指定されたサービスを開始
- `stop`: 指定されたサービスを停止
- `restart`: 指定されたサービスを再起動
- `ps`: サービスの状態を表示
- `logs`: サービスのログを表示
- `shell`: PostgreSQLサービスのシェルを開く
- `records`: 全テーブルのレコード数を表示
- `records <table>`: 指定テーブルの全件表示
- `parser`: 指定されたテーブルのパーサースクリプトを実行
- `migration`: マイグレーション関連のコマンド
- `cache generate`: 指定されたキャッシュを生成
- `cache delete`: 指定されたキャッシュを削除
- `cache refresh`: 指定されたキャッシュを削除して再生成
- `cache get full`: 全キャッシュデータを取得・整形
- `cache get catalogue`: EAVカタログキャッシュ（分類属性・学部・区分リスト等）をJSON整形で取得
- `cache list`: 利用可能なキャッシュ一覧を表示
- `cache status`: キャッシュの状態を表示
- `sql <sqlfile>`: 指定したSQLファイルをPostgreSQLサーバーで実行（psqlオプション：--tuples-only, --no-align等に対応）

#### 【-g, --git サービスコマンド】

- `update minor <squash|noff>`: minorバージョンアップをdevelopへマージ（squash/no-ff選択）

#### 【-m, --mcp サービスコマンド】

- `comment generate`: mcp用コメントSQLを生成（src/db/mcp_comments.pyを実行）
- `start -f <json>`: 指定したmcp設定jsonの内容でmcpサーバー（postgres）をバックグラウンド起動
- `stop -f <json>`: 指定したmcp設定jsonの内容でmcpサーバー（postgres）を停止
- `restart -f <json>`: 停止→起動を連続実行

### 使用例

```bash
# Python仮想環境の初期化
./syllabus.sh venv init

# サービスの起動
./syllabus.sh -p start

# サービスの停止
./syllabus.sh -p stop

# サービスの状態表示
./syllabus.sh -p ps

# サービスのログ表示
./syllabus.sh -p logs

# PostgreSQLシェルの起動
./syllabus.sh -p shell

# テーブルのレコード数表示
./syllabus.sh -p records

# facultyテーブルの全件表示
./syllabus.sh -p records faculty

# パーサーの実行（引数必須）
./syllabus.sh parser book
./syllabus.sh parser syllabus

# CSVファイルの整形
./syllabus.sh csv normalize 2024

# データ生成
./syllabus.sh -p migration generate init
./syllabus.sh -p migration generate migration

# データチェック
./syllabus.sh -p migration check

# データデプロイ
./syllabus.sh -p migration deploy

# キャッシュ生成
./syllabus.sh -p cache generate <cache名>

# キャッシュ再生成
./syllabus.sh -p cache refresh <cache名>

# キャッシュ状態確認
./syllabus.sh -p cache status

# キャッシュテスト
./syllabus.sh -p cache test

# OS互換性テスト
./syllabus.sh test-os

# コメントSQL生成
./syllabus.sh -m comment generate

# mcpサーバー起動
./syllabus.sh -m start -f .cursor/mcp.json

# mcpサーバー停止
./syllabus.sh -m stop -f .cursor/mcp.json

# mcpサーバー再起動
./syllabus.sh -m restart -f .cursor/mcp.json

# git minorバージョンアップ
./syllabus.sh -g update minor squash
./syllabus.sh -g update minor noff

# EAVカタログキャッシュの生成
./syllabus.sh -p cache generate catalogue

# EAVカタログキャッシュの再生成
./syllabus.sh -p cache refresh catalogue

# EAVカタログキャッシュの取得（JSON整形出力）
./syllabus.sh -p cache get catalogue
```

## 注意事項

- PostgreSQLの操作（shell/records/migration/cache/sql）を行う場合は、必ず`-p`オプションを指定してください
- **EAVカタログキャッシュ（catalogue）は、分類属性・学部・区分リスト等をJSONで一括取得でき、get catalogueで自動的に整形表示されます**
- パーサーを実行する前に、`venv init`コマンドでPython仮想環境を初期化してください
- 各コマンドは`bin/`ディレクトリ内の対応するスクリプトを実行します
- エラーが発生した場合は、適切なエラーメッセージとヘルプが表示されます

## OS互換性

本スクリプトは以下のOS環境で動作します：

### 対応OS
- **Linux**: Ubuntu、CentOS、Debian等
- **macOS**: Darwin（M1/M2 Mac含む）

### 自動判別機能
- OS種類を自動判別し、適切なコマンドを選択
- macOSでは`ls -v`オプションが利用できないため、`ls -1` + `sort -V`を使用
- Linuxでは`ls -v`オプションを直接使用
- 環境変数の読み込みは共通関数で統一

### 互換性テスト
```bash
./syllabus.sh test-os
```

このコマンドで以下の項目をテストできます：
- OS種類の判別
- OS別コマンド設定
- バージョンディレクトリ取得
- 環境変数取得
- 各コマンドの利用可能性

## 関連スクリプト

### パーサー関連
- [parser.sh](../python/parser.md) - パーサースクリプトの実行

### minorバージョンアップのsquash/no-ffマージ

- `-g update minor squash` : squashでdevelopにminorマージ
- `-g update minor noff`   : no-ffでdevelopにminorマージ

```bash
./syllabus.sh -g update minor squash
./syllabus.sh -g update minor noff
```

現在のブランチの内容をdevelopにsquashまたはno-ffでマージします。
内部的に `bin/minor_version_update.sh` を呼び出します。

[🔝 ページトップへ](#syllabussh) 