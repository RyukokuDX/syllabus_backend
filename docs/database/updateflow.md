# データベース更新手順書

[readmeへ](../../README.md) | [doc.mdへ](../doc.md)

## 目次
0. [即席更新手順](#即席更新手順)
1. [概要](#概要)
2. [前提条件](#前提条件)
3. [更新の流れ](#更新の流れ)
4. [詳細手順](#詳細手順)
5. [トラブルシューティング](#トラブルシューティング)

## 即席更新手順
- `update/sample/`内の更新したいテーブル名のサンプルjsonを`update/{table}/add/`に移動
- 設置したjsonに追加したい内容を追記
- developにpushしてpull requestを出す
- 管理者がＤＢを更新！

## 概要

このドキュメントでは、シラバスデータベースの更新手順について説明します。
データの更新は、JSONファイルを特定のディレクトリに配置し、Dockerコンテナを再起動することで行います。
上記よりも複雑な為、移行の文章は更新後のDBまで確認したい人向けです。

### 目的
- シラバスデータの安全な更新
- 更新履歴の管理
- エラー発生時の対応

### 特徴
- JSONファイルによるデータ管理
- Dockerによる環境分離
- 手動確認によるデータ整合性の確保

## 前提条件

### 必要なソフトウェア
- Docker Desktop
- Python 3.8以上
- Visual Studio Code（推奨）

### 必要なファイル
- `.env.sample`ファイル（または`.env`ファイル）
- 更新用のJSONファイル

## 更新の流れ

1. 環境の準備
2. JSONファイルの配置
3. Dockerコンテナの再起動
4. 更新の確認

## 詳細手順

### 1. 環境の準備

#### 1-1. プロジェクトのクローン（初回のみ）
```bash
git clone https://github.com/yourusername/syllabus_backend.git
cd syllabus_backend
```

#### 1-2. 環境設定ファイルの準備
1. `.env.sample`を`docker/postgresql/.env`にコピー
```bash
cd docker/postgresql
copy .env.sample .env
```

### 2. JSONファイルの配置

#### 2-1. ディレクトリ構造の確認
更新用JSONファイルは以下のディレクトリに配置します：
```
updates/
└── subject/
    ├── add/      # 新規追加データ
    ├── update/   # 更新データ
    └── delete/   # 削除データ
```

#### 2-2. JSONファイルの形式
```json
{
  "content": {
    "subject_code": "AB1234",
    "subject_name": "プログラミング基礎",
    "credit": 2,
    "created_at": "2024-03-20T10:00:00",
    "updated_at": "2024-03-20T10:00:00"
  }
}
```

#### 2-3. ファイルの配置
1. 更新内容に応じて適切なディレクトリを選択
   - 新規追加 → `updates/subject/add/`
   - 更新 → `updates/subject/update/`
   - 削除 → `updates/subject/delete/`

2. JSONファイルを配置
   - ファイル名は任意（例：`subject_001.json`）
   - 複数ファイルの配置も可能

### 3. Dockerコンテナの再起動

#### 3-1. 現在のコンテナの停止
```bash
cd docker/postgresql
docker compose down
```

#### 3-2. コンテナの再起動
```bash
docker compose up -d
```

### 4. 更新の確認

#### 4-1. データベースへの接続
```bash
# admin_userとして接続
psql -h localhost -p 5432 -U admin_user -d syllabus_db
```

#### 4-2. データの確認
```sql
-- 更新されたデータの確認
SELECT * FROM subject WHERE updated_at > CURRENT_DATE - INTERVAL '1 day';

-- 特定の科目コードの確認
SELECT * FROM subject WHERE subject_code = 'AB1234';
```

## トラブルシューティング

### コンテナ起動エラー
1. ログの確認
```bash
docker logs postgresql-db
```

2. よくある問題と解決方法
- ポート競合
  ```bash
  # 使用中のポートの確認
  netstat -ano | findstr :5432
  ```
- 権限エラー
  - `.env`ファイルの設定を確認
  - Dockerの再起動を試す

### データ更新エラー
1. JSONファイルの形式確認
   - 必須フィールドの存在確認
   - 日付形式の確認
   - 文字コードの確認（UTF-8）

2. データベースの状態確認
```sql
-- テーブル構造の確認
\d subject

-- エラーログの確認
SELECT * FROM error_log ORDER BY created_at DESC LIMIT 10;
```

### バックアップとリストア
```bash
# 更新前のバックアップ
docker exec postgresql-db pg_dump -U admin_user syllabus_db > backup_before_update.sql

# 問題発生時のリストア
cat backup_before_update.sql | docker exec -i postgresql-db psql -U admin_user -d syllabus_db
```

## 補足：マイグレーション（オプション）

マイグレーションを使用する場合は、以下の手順を実行します：

1. マイグレーションファイルの生成
```bash
python src/db/migrations/generate_migration.py
```

2. 生成されたファイルの確認
```bash
ls -l docker/postgresql/init/migrations/
```

マイグレーションファイルは、コンテナ再起動時に自動的に適用されます。

## 1. データベース構造の更新手順

### 1.1 スキーマ変更の基本フロー

1. **変更内容の確認**
   - `docs/database/structure.md`の更新履歴に変更内容を記録
   - `docs/database/er.md`のER図を更新
   - 変更内容の影響範囲を確認

2. **マイグレーションファイルの生成**
   ```bash
   # src/db/migrationsディレクトリで実行
   python generate_migration.py
   ```
   - タイムスタンプ付きのSQLファイルが生成される
   - 生成されたファイルは`src/db/migrations/`に保存

3. **初期化SQLの更新**
   - `docker/postgresql/init/init.sql.template`を更新
   - `docker/postgresql/generate_init.sh`を実行して
   `docker/postgresql/init/init.sql`を作成
   - テーブル定義、インデックス、制約を最新の状態に反映

4. **モデルの更新**
   - `src/db/models.py`のSQLAlchemyモデルを更新
   - データクラスの定義も必要に応じて更新

5. **データベース操作関数の更新**
   - `src/db/database.py`の関数を更新
   - 新しいカラムやテーブルに対応する処理を追加

### 1.2 具体的な変更パターン

#### テーブル名の変更
1. 新しいテーブルを作成
2. 既存データを移行
3. 古いテーブルを削除
4. 関連するインデックスと制約を更新

#### カラム名の変更
1. 新しいカラムを追加
2. 既存データを移行
3. 古いカラムを削除
4. 関連するインデックスと制約を更新

#### カラム型の変更
1. 一時的なカラムを追加
2. データを変換して移行
3. 古いカラムを削除
4. 一時的なカラムの名前を変更

#### 制約の追加/変更
1. 既存の制約を削除（必要な場合）
2. 新しい制約を追加
3. データの整合性を確認

### 1.3 注意事項

- 本番環境での変更は必ずバックアップを取得
- 変更は段階的に行い、各段階でテストを実施
- ロールバック手順を事前に準備
- 変更内容をチーム内で共有
- 変更履歴を詳細に記録

## 2. データ更新の手順

### 2.1 新規データの追加

1. **JSONファイルの準備**
   - `updates/{テーブル名}/add/`ディレクトリにJSONファイルを配置
   - ファイル名は`{タイムスタンプ}_{テーブル名}.json`の形式

2. **マイグレーションファイルの生成**
   ```bash
   # src/db/migrationsディレクトリで実行
   python generate_migration.py
   ```

3. **生成されたSQLの確認**
   - `src/db/migrations/`に生成されたSQLファイルを確認
   - データの整合性をチェック

4. **データベースへの適用**
   - 生成されたSQLを実行
   - 実行結果を確認

### 2.2 既存データの更新

1. **更新用JSONファイルの準備**
   - `updates/{テーブル名}/update/`ディレクトリにJSONファイルを配置
   - 更新対象のレコードを特定するキーを含める

2. **更新用SQLの生成**
   - `generate_migration.py`を実行して更新用SQLを生成
   - 生成されたSQLの内容を確認

3. **データベースへの適用**
   - 更新用SQLを実行
   - 更新結果を確認

### 2.3 データの削除

1. **削除対象の特定**
   - 削除するレコードの条件を明確化
   - 関連するレコードの影響を確認

2. **削除用SQLの生成**
   - 削除条件に基づいてSQLを生成
   - 外部キー制約を考慮

3. **データベースからの削除**
   - 削除用SQLを実行
   - 削除結果を確認

## 3. バックアップとリストア

### 3.1 バックアップの取得

```bash
# データベースのバックアップ
pg_dump -U postgres syllabus > backup_$(date +%Y%m%d).sql

# スキーマのみのバックアップ
pg_dump -U postgres --schema-only syllabus > schema_$(date +%Y%m%d).sql
```

### 3.2 リストア手順

```bash
# データベースのリストア
psql -U postgres syllabus < backup_YYYYMMDD.sql

# スキーマのみのリストア
psql -U postgres syllabus < schema_YYYYMMDD.sql
```

## 4. トラブルシューティング

### 4.1 一般的な問題

1. **外部キー制約違反**
   - 参照先のレコードが存在することを確認
   - 必要に応じて参照先のデータを先に追加

2. **一意制約違反**
   - 重複するデータがないことを確認
   - 必要に応じて既存データを更新

3. **型変換エラー**
   - データ型の互換性を確認
   - 必要に応じてデータを変換

### 4.2 ロールバック手順

1. **最新のバックアップを確認**
2. **データベースをリストア**
3. **変更を元に戻す**
4. **システムの動作を確認**

## 5. 監視とメンテナンス

### 5.1 定期的な確認項目

- テーブルのサイズと成長率
- インデックスの使用状況
- パフォーマンスの傾向
- エラーログの確認

### 5.2 最適化のタイミング

- テーブルサイズが大きくなった場合
- クエリのパフォーマンスが低下した場合
- 新しいインデックスが必要な場合
- データの整合性に問題が発生した場合

[🔝 ページトップへ](#データベース更新手順書)