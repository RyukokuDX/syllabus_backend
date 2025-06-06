<!--
更新時の注意事項:
- 準拠とは、類推せずに内容に従うこと
- 更新は docs/doc.md に準拠すること
-->

# マイグレーションファイル生成スクリプト

[readmeへ](../../README.md) | [doc.mdへ](../doc.md)

## 目次
1. [概要](#概要)
2. [機能仕様](#機能仕様)
3. [入力仕様](#入力仕様)
4. [出力仕様](#出力仕様)
5. [関数仕様](#関数仕様)
6. [使用例](#使用例)

## 概要
科目データのJSONファイルからSQLマイグレーションファイルを自動生成するスクリプトです。

## 機能仕様
- JSONファイルから科目データを読み込む
- SQLのINSERT文を生成する
- タイムスタンプ付きのマイグレーションファイルを生成する
- 既存データの更新（UPSERT）に対応

## 入力仕様

### 入力ディレクトリ構造
```
updates/
└── subject/
    └── add/
        └── *.json
```

### JSONファイル形式
```json
{
  "content": {
    "subject_code": "string",
    "subject_name": "string",
    "credit": "number",
    "created_at": "timestamp",
    "updated_at": "timestamp"
    // その他の科目関連フィールド
  }
}
```

## 出力仕様

### 出力ディレクトリ
```
docker/postgre/init/migrations/
```

### 出力ファイル名形式
```
V{YYYYMMDDHHMMSS}__insert_subjects.sql
```

### SQL出力形式
```sql
INSERT INTO subject (
    column1, column2, ...
) VALUES
    (value1, value2, ...),
    (value1, value2, ...)
ON CONFLICT (subject_code) DO UPDATE SET
    column1 = EXCLUDED.column1,
    column2 = EXCLUDED.column2,
    updated_at = CURRENT_TIMESTAMP;
```

## 関数仕様

### read_json_files(directory)
指定されたディレクトリ内のすべてのJSONファイルを読み込む関数

#### 引数
- directory (Path): JSONファイルが格納されているディレクトリパス

#### 戻り値
- list: 読み込んだJSONデータのリスト

### generate_sql_insert(table_name, records)
SQLのINSERT文を生成する関数

#### 引数
- table_name (str): 対象テーブル名
- records (list): レコードのリスト

#### 戻り値
- str: 生成されたSQL文

### main()
メイン処理を実行する関数

#### 処理内容
1. プロジェクトルートパスの取得
2. 入力/出力ディレクトリの設定
3. JSONファイルの読み込み
4. SQL文の生成
5. マイグレーションファイルの出力

## 使用例

```python
# スクリプトの実行
python src/db/migrations/generate_migration.py
```

## 更新履歴

| 日付 | バージョン | 更新者 | 内容 |
|------|------------|--------|------|
| 2024-03-20 | 1.0.0 | システム開発チーム | 初版作成 |

[🔝 ページトップへ](#マイグレーションファイル生成スクリプト) 