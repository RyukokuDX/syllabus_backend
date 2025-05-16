# APIサーバー仕様書
[readmeへ](../README.md)

## 概要
シラバス情報を提供するRESTful APIサーバー。FastAPIを使用して実装されています。

## 基本情報
- APIバージョン: v1
- エンドポイントプレフィックス: `/api`

## エンドポイント

### SQLクエリ実行

#### エンドポイント 
```
POST /api/query
```

#### リクエストボディ
```json
{
  "query": "SELECT * FROM syllabus WHERE year = ? AND semester = ?",
  "params": ["2025", "前期"]
}
```

#### レスポンス
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "year": "2025",
      "title": "プログラミング基礎",
      "semester": "前期"
    }
  ],
  "metadata": {
    "row_count": 1,
    "execution_time": "0.123s"
  }
}
```

#### エラーレスポンス
```json
{
  "status": "error",
  "error": {
    "code": "ERROR_CODE",
    "message": "エラーメッセージ",
    "details": "詳細なエラー情報"
  }
}
```

### 制限事項
- Content-Type: application/json
- 最大リクエストサイズ: 1MB
- 1リクエストにつき1つのSQLクエリのみ実行可能
- セミコロン（;）による複数命令は禁止
- 1回のクエリで返却される最大行数：1000行
- クエリ実行の最大時間：30秒

### 使用可能な操作
1. SELECT文
```sql
-- 基本的な検索
SELECT * FROM syllabus WHERE year = ?

-- 列の指定
SELECT title, teacher, year FROM syllabus WHERE year = ?

-- 集計関数
SELECT COUNT(*) FROM syllabus WHERE year = ?
```

2. 検索条件
```sql
-- 完全一致
WHERE column = ?

-- あいまい検索
WHERE title LIKE ? ESCAPE '\'
-- パラメータ例: ["プログラミング%"]  -- 前方一致
-- パラメータ例: ["%プログラミング%"]  -- 中間一致

-- 範囲検索
WHERE credit BETWEEN ? AND ?
-- パラメータ例: [1, 4]
```

3. 使用可能な関数
- 集計関数：COUNT, SUM, AVG, MAX, MIN
- 文字列関数：UPPER, LOWER, TRIM
- 日付関数：DATE, STRFTIME

### 禁止されている操作
- セミコロンを含むクエリ
- サブクエリ
- テーブル結合（JOIN）
- データ更新操作（INSERT, UPDATE, DELETE等）
- スキーマ操作（CREATE, ALTER, DROP等）
- トランザクション操作（BEGIN, COMMIT, ROLLBACK）

### エラーコード
- 400: リクエストパラメータが不正
- 403: 許可されていないSQLクエリ
- 404: リソースが見つからない
- 408: クエリ実行がタイムアウト
- 500: サーバー内部エラー

### セキュリティ対策
1. パラメータ化されたクエリの使用
- すべてのユーザー入力は必ずパラメータとして渡す
- クエリ文字列への直接的な値の埋め込みは禁止

2. クエリの検証
- 構文解析による有効性確認
- 禁止操作のチェック
- 実行計画の検証

3. カラム指定の制限
- 動的なカラム指定時はホワイトリストで検証
```json
{
  "allowed_columns": {
    "syllabus": ["id", "year", "title", "teacher", "semester", "credit"],
    "departments": ["id", "name", "faculty"],
    "teachers": ["id", "name", "title"]
  }
}
```
- `SELECT *` の使用は監査ログに記録

4. LIKE句の保護
- ワイルドカード使用パターンの監視
```json
{
  "suspicious_patterns": [
    "%--",
    "%';",
    "%;",
    "%/*",
    "%*/",
    "%@@"
  ]
}
```
- 異常パターン検出時は警告ログを出力
- 同一IPからの連続した異常パターンでブロック

5. レスポンスフィールドの制限
- デフォルトビューの定義
```json
{
  "default_views": {
    "syllabus_public": ["title", "teacher", "semester", "credit"],
    "syllabus_admin": ["*"],
    "teachers_public": ["name", "title"]
  }
}
```
- アクセス権限に応じたフィールド制限
- 機密情報を含むフィールドの除外

6. 監査ログ
```json
{
  "timestamp": "2024-03-20T10:30:00Z",
  "level": "INFO",
  "event": "QUERY_EXECUTION",
  "details": {
    "query": "SELECT * FROM syllabus WHERE year = ?",
    "params": ["2025"],
    "execution_time": "0.123s",
    "query_analysis": {
      "used_wildcards": false,
      "used_functions": ["STRFTIME"],
      "selected_columns": ["*"],
      "table_access": ["syllabus"]
    },
    "client_info": {
      "ip": "192.168.1.100",
      "user_id": "user123",
      "access_level": "public"
    }
  }
}
```

7. 異常検知ルール
- 関数使用頻度の監視
```json
{
  "function_limits": {
    "interval": "1hour",
    "thresholds": {
      "STRFTIME": 100,
      "UPPER": 50,
      "LOWER": 50,
      "COUNT": 200
    }
  }
}
```
- パターンベースの検知
  - 同一IPからの特定関数の連続使用
  - 通常とは異なる時間帯での関数使用
  - 特定のテーブル・カラムへの集中的なアクセス

8. ブロックポリシー
- 段階的な制限
  1. 警告ログの出力
  2. レート制限の強化
  3. 一時的なIPブロック
  4. アカウントの停止
- 管理者への通知
  - Slack通知
  - メール通知
  - ダッシュボードでのアラート表示

### レート制限
- 1分あたりの最大リクエスト数: 60
- 超過した場合は429エラー（Too Many Requests）を返却

[トップへ](#)