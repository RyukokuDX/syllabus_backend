# stop-postgres.sh

[readmeへ](../README.md) | [ドキュメント作成ガイドラインへ](../doc.md) | [syllabus.shへ](./syllabus.md)

PostgreSQLサービスを停止するスクリプト。

## 目次
1. [機能](#機能)
2. [使用方法](#使用方法)
3. [処理の流れ](#処理の流れ)
4. [依存関係](#依存関係)
5. [注意事項](#注意事項)
6. [更新履歴](#更新履歴)

## 機能

1. PostgreSQLサービスの停止
   - Docker Composeを使用してサービスを停止
   - コンテナの停止を確認

## 使用方法

```bash
./syllabus.sh -p stop
```

## 処理の流れ

1. PostgreSQLの停止
   - `docker-compose down`の実行
   - コンテナの停止を確認

## 依存関係

- Docker
- Docker Compose
- PostgreSQLコンテナ

## 注意事項

- 実行前にPostgreSQLサービスが起動していることを確認
- コンテナ名は`postgres-db`を使用
- データベースの接続を確認してから停止することを推奨

## 更新履歴

| 日付 | バージョン | 更新者 | 内容 |
|------|------------|--------|------|
| 2024-03-20 | 1.0.1 | 開発者名 | 初版作成 |

[🔝 ページトップへ](#stop-postgressh) 