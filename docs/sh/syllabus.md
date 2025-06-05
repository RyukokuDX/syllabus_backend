# syllabus.sh

[readmeへ](../README.md) | [ドキュメント作成ガイドラインへ](../doc.md)

メインのシェルスクリプト。PostgreSQLとFastAPIサービスの管理を統一的に行うためのインターフェースを提供します。

## 目次
1. [使用方法](#使用方法)
2. [オプション](#オプション)
3. [コマンド](#コマンド)
4. [使用例](#使用例)
5. [注意事項](#注意事項)
6. [関連スクリプト](#関連スクリプト)
7. [更新履歴](#更新履歴)

## 使用方法

```bash
./syllabus.sh [OPTIONS] COMMAND [ARGS]
```

### オプション

- `-p, --postgres`: PostgreSQLサービスを操作
- `-h, --help`: ヘルプメッセージを表示

### コマンド

#### 基本コマンド

- `help`: ヘルプメッセージを表示
- `venv-init`: Python仮想環境の初期化
- `start`: 指定されたサービスを開始
- `stop`: 指定されたサービスを停止
- `ps`: サービスの状態を表示
- `logs`: サービスのログを表示

#### PostgreSQL関連

- `shell`: PostgreSQLサービスのシェルを開く（-pオプション必須）
- `records`: すべてのテーブルのレコード数を表示、または指定テーブルの全件表示（-pオプション必須）
  - 引数なし: 全テーブルのレコード数を表示
  - `records {テーブル名}`: 指定テーブルの全レコードを表示

#### パーサー関連

- `parser`: 指定されたテーブルのパーサースクリプトを実行（引数必須）

#### CSV関連

- `csv normalize`: 指定年度のCSVファイルを整形
  - 引数: `{year}` - 処理対象の年度
  - 処理内容:
    - 元ファイルを`.org`拡張子でバックアップ（既存の場合はスキップ）
    - 区切り文字をタブに統一
    - 全フィールドの前後の空白を削除
    - 空値、`null`、`NULL`、`None`を`NULL`に統一
    - "科目名"フィールドを正規化（全角→半角、記号の統一など）

#### データ管理関連

- `generate`: 指定されたテーブルのデータを生成（-pオプション必須、引数必須）
- `check`: 指定されたテーブルのデータをチェック（-pオプション必須）
- `deploy`: 指定されたテーブルのデータをデプロイ（-pオプション必須）

### 使用例

```bash
# Python仮想環境の初期化
./syllabus.sh venv-init

# サービスの起動
./syllabus.sh -p start

# サービスの停止
./syllabus.sh -p stop

# サービスの状態表示
./syllabus.sh ps

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
./syllabus.sh -p generate init
./syllabus.sh -p generate migration

# データチェック
./syllabus.sh -p check

# データデプロイ
./syllabus.sh -p deploy
```

## 注意事項

- PostgreSQLの操作（shell/records）を行う場合は、必ず`-p`オプションを指定してください
- パーサーを実行する前に、`venv-init`コマンドでPython仮想環境を初期化してください
- 各コマンドは`bin/`ディレクトリ内の対応するスクリプトを実行します
- エラーが発生した場合は、適切なエラーメッセージとヘルプが表示されます

## 関連スクリプト

### パーサー関連
- [parser.sh](../python/parser.md) - パーサースクリプトの実行

## 更新履歴

| 日付 | バージョン | 更新者 | 内容 |
|------|------------|--------|------|
| 2024-06-05 | 1.0 | 藤原和将 | 初版作成 |
| 2024-06-05 | 1.1 | 藤原和将  | Python仮想環境のサポートを追加、コマンド構造を整理 |
| 2024-06-05 | 1.2 | 藤原和将  | parser関連の処理を追加 |
| 2024-06-05 | 1.3 | 藤原和将  | CSVファイルの整形機能を追加 |

[🔝 ページトップへ](#syllabussh) 