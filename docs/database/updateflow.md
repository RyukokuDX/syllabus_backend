以下は推敲後のMarkdown文書です。文体の統一、表現の明瞭化、タイポの修正、読点・句読点の整理を中心に改善しました。リンクやコード、構成は元のままです。

---

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

* `update/sample/`内の、更新したいテーブル名のサンプルJSONを`update/{table}/add/`に移動
* 移動したJSONに追加したい内容を追記
* developブランチにpushして、Pull Requestを作成
* 管理者がDBを更新！

## 概要

このドキュメントでは、シラバスデータベースの更新手順を説明します。
更新は、JSONファイルを所定のディレクトリに配置し、Dockerコンテナを再起動することで行います。
以下の手順は、単なる更新にとどまらず、更新後のDB状態まで確認したい方向けの内容です。

### 目的

* シラバスデータの安全な更新
* 更新履歴の記録
* エラー発生時の対応策の明示

### 特徴

* JSONファイルによるデータ管理
* Dockerによる環境の分離
* 手動確認によるデータ整合性の確保

## 前提条件

### 必要なソフトウェア

* Docker Desktop
* Python 3.8以上
* Visual Studio Code（推奨）

### 必要なファイル

* `.env.sample`（または`.env`）ファイル
* 更新用JSONファイル

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

```bash
cd docker/postgresql
copy .env.sample .env
```

### 2. JSONファイルの配置

#### 2-1. ディレクトリ構造の確認

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

* 適切なディレクトリを選択（add / update / delete）
* 任意のファイル名（例：`subject_001.json`）で保存
* 複数ファイルの同時配置も可能

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
psql -h localhost -p 5432 -U admin_user -d syllabus_db
```

#### 4-2. データの確認

```sql
SELECT * FROM subject WHERE updated_at > CURRENT_DATE - INTERVAL '1 day';
SELECT * FROM subject WHERE subject_code = 'AB1234';
```

## トラブルシューティング

### コンテナ起動エラー

#### 1. ログの確認

```bash
docker logs postgresql-db
```

#### 2. よくある問題と対策

* **ポート競合**

```bash
netstat -ano | findstr :5432
```

* **権限エラー**

  * `.env`ファイルの確認
  * Dockerの再起動

### データ更新エラー

* JSONフォーマットの確認

  * 必須フィールド、日付形式、文字コード（UTF-8）

* DB状態の確認

```sql
\d subject
SELECT * FROM error_log ORDER BY created_at DESC LIMIT 10;
```

### バックアップとリストア

```bash
docker exec postgresql-db pg_dump -U admin_user syllabus_db > backup_before_update.sql
cat backup_before_update.sql | docker exec -i postgresql-db psql -U admin_user -d syllabus_db
```

## 補足：マイグレーション（オプション）

```bash
python src/db/migrations/generate_migration.py
ls -l docker/postgresql/init/migrations/
```

マイグレーションはコンテナ再起動時に自動適用されます。

---

## 1. データベース構造の更新手順

### 1.1 スキーマ変更の流れ

1. **変更内容の確認**

   * `structure.md`とER図の更新、影響範囲の特定

2. **マイグレーションファイル生成**

```bash
python generate_migration.py
```

3. **初期化SQLの更新**

```bash
./generate_init.sh
```

4. **モデルの更新**

   * `models.py`と必要に応じてデータクラスも修正

5. **DB操作関数の更新**

   * `database.py`の該当箇所を修正

6. **サンプルJSONの更新**

   * `updates/sample/{table}.json` を整備

### 1.2 変更パターンごとの処理

#### テーブル名の変更

新設 → データ移行 → 旧テーブル削除 → 制約/インデックス更新

#### カラム名の変更

追加 → データ移行 → 旧カラム削除 → 制約更新

#### カラム型の変更

一時カラム → 変換 → 削除 → 名前変更

#### 制約の追加/変更

旧制約削除 → 新制約追加 → 整合性確認

### 1.3 注意点

* 本番前に必ずバックアップ
* 各段階でテスト
* ロールバック手順の準備
* チーム共有と記録の徹底

---

## 2. データ更新の手順

### 2.1 新規データの追加

```bash
# updates/{テーブル名}/add/ に配置
# ファイル名: {タイムスタンプ}_{テーブル名}.json
python generate_migration.py
```

生成されたSQLで整合性チェック → 適用 → 結果確認

### 2.2 データの更新

* 更新対象JSONを `update/` に配置
* キーを明示 → マイグレーション生成 → SQL確認・適用

### 2.3 データの削除

* 条件特定 → SQL生成 → 削除・結果確認（外部キー注意）

---

## 3. バックアップとリストア

### 3.1 バックアップ

```bash
pg_dump -U postgres syllabus > backup_$(date +%Y%m%d).sql
pg_dump -U postgres --schema-only syllabus > schema_$(date +%Y%m%d).sql
```

### 3.2 リストア

```bash
psql -U postgres syllabus < backup_YYYYMMDD.sql
psql -U postgres syllabus < schema_YYYYMMDD.sql
```

---

## 4. トラブルシューティング

### 4.1 よくある問題

* **外部キー制約違反** → 参照元の存在確認
* **一意制約違反** → 重複確認
* **型変換エラー** → データ型の整合性確認

### 4.2 ロールバック手順

* バックアップ確認 → リストア → 修正 → 動作確認

---

## 5. 監視とメンテナンス

### 5.1 定期確認項目

* テーブルサイズ、インデックス、パフォーマンス、エラーログ

### 5.2 最適化の目安

* パフォーマンス劣化
* データ整合性問題
* インデックス不足

[🔝 ページトップへ](#データベース更新手順書)