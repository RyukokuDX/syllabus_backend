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
./syllabus.sh [OPTIONS] COMMAND
```

### オプション

- `-p, --postgresql`: PostgreSQLサービスを操作（デフォルト）
- `-a, --api`: FastAPIサービスを操作
- `-h, --help`: ヘルプメッセージを表示

### コマンド

#### PostgreSQL関連

- `start`: PostgreSQLサービスを起動
- `stop`: PostgreSQLサービスを停止
- `check`: 開発用データベースでマイグレーションを確認
- `deploy`: マイグレーションを本番環境に適用
- `generate`: マイグレーションファイルを生成
- `init-dirs`: 更新ディレクトリを初期化
- `clean`: 更新ディレクトリをクリーンアップ

#### FastAPI関連

- `start`: FastAPIサービスを起動
- `stop`: FastAPIサービスを停止

### 使用例

```bash
# PostgreSQLの起動（check/deployの前に必要）
./syllabus.sh -p start

# PostgreSQLマイグレーションの確認（PostgreSQLが起動している必要あり）
./syllabus.sh -p check

# マイグレーションの本番環境への適用（PostgreSQLが起動している必要あり）
./syllabus.sh -p deploy

# FastAPIの起動
./syllabus.sh -a start
```

## 注意事項

- PostgreSQLの操作（check/deploy）を行う前に、必ず`start`コマンドでサービスを起動してください
- 各コマンドは`bin/`ディレクトリ内の対応するスクリプトを実行します
- エラーが発生した場合は、適切なエラーメッセージとヘルプが表示されます

## 関連スクリプト

### PostgreSQL関連
- [start-postgres.sh](./start-postgres.md) - PostgreSQLサービスの起動と初期化
- [stop-postgres.sh](./stop-postgres.md) - PostgreSQLサービスの停止
- [check-with-dev-db.sh](./check-with-dev-db.md) - 開発用データベースでのマイグレーション確認
- [deploy-migration.sh](./deploy-migration.md) - 本番環境へのマイグレーション適用
- [generate-migration.sh](./generate-migration.md) - マイグレーションファイルの生成
- [init-directories.sh](./init-directories.md) - 更新ディレクトリの初期化
- [init-updates.sh](./init-updates.md) - 更新ディレクトリのクリーンアップ

### FastAPI関連
- FastAPIの起動と停止は`syllabus.sh`内で直接処理されます

## 更新履歴

| 日付 | バージョン | 更新者 | 内容 |
|------|------------|--------|------|
| 2024-03-20 | 1.0.0 | 開発者名 | 初版作成 |

[🔝 ページトップへ](#syllabussh) 