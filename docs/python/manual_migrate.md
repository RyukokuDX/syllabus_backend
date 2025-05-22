# マイグレーション実行スクリプト

[readmeへ](../../README.md)

## 概要
`manual_migrate.py`は、PostgreSQLデータベースに対してSQLマイグレーションを実行するためのPythonスクリプトです。

## 機能
- マイグレーションファイルの自動検出と順序付け実行
- トランザクション管理によるロールバック機能
- 複数データベース対応
- エラーハンドリングとログ出力

## インターフェース

### コマンドライン
```bash
python manual_migrate.py [database_name]
```

### 引数
| 引数 | 説明 | デフォルト値 | 必須 |
|------|------|--------------|------|
| database_name | 対象データベース名 | master_db | × |

### 環境変数
| 変数名 | 説明 | デフォルト値 |
|--------|------|--------------|
| POSTGRES_HOST | データベースホスト | localhost |
| POSTGRES_PORT | ポート番号 | 5432 |
| POSTGRES_USER | ユーザー名 | postgres |
| POSTGRES_PASSWORD | パスワード | postgres |

## 内部実装

### クラス・関数

#### `get_connection(database: str = "master_db") -> psycopg2.extensions.connection`
データベースへの接続を取得します。

**引数**
- database: 接続先データベース名

**戻り値**
- psycopg2データベース接続オブジェクト

**例外**
- psycopg2.Error: データベース接続エラー時

#### `get_migration_files(migrations_dir: Path) -> List[Path]`
マイグレーションファイルを取得します。

**引数**
- migrations_dir: マイグレーションファイルのディレクトリパス

**戻り値**
- マイグレーションファイルパスのリスト（バージョン順）

#### `execute_migration(conn: psycopg2.extensions.connection, migration_file: Path) -> None`
マイグレーションファイルを実行します。

**引数**
- conn: データベース接続
- migration_file: 実行するマイグレーションファイルのパス

**例外**
- psycopg2.Error: SQL実行エラー時

#### `main(database: Optional[str] = None) -> None`
メイン処理を実行します。

**引数**
- database: 対象データベース名（オプション）

## エラーハンドリング

### データベース接続エラー
1. エラーメッセージを表示
2. 終了コード1で終了

### マイグレーション実行エラー
1. エラーの詳細を表示
2. トランザクションをロールバック
3. 終了コード1で終了

## 使用例

### デフォルトデータベースへのマイグレーション
```bash
python manual_migrate.py
```

### 特定のデータベースへのマイグレーション
```bash
python manual_migrate.py test_db
```

## 注意事項
1. マイグレーションファイルの命名規則
   - 形式: `V{バージョン番号}_{説明}.sql`
   - 例: `V1_create_users_table.sql`

2. 運用上の注意
   - 本番環境での実行前にテスト環境での動作確認を推奨
   - バージョン番号の重複を避ける
   - 大規模なデータ変更は停止時間帯に実行 

[トップへ](#)