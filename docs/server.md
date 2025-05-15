# APIサーバー仕様書
[readmeへ](../README.md)

## 概要
シラバス情報を提供するRESTful APIサーバー。FastAPIを使用して実装されています。

## 基本情報
- ベースURL: `http://localhost:8000`
- APIバージョン: v1
- エンドポイントプレフィックス: `/api`

## 認証
- 現時点では認証なし（将来的に必要に応じて実装）

## エンドポイント一覧

### SQLクエリ実行

#### エンドポイント 
```
GET /api/
```

#### クエリパラメータ
- `query` (required): 実行するSQLクエリ文
  - 例: `SELECT * FROM syllabus WHERE year = '2025'`

#### レスポンス
```json
{
  "status": "success",
  "data": [
    {
      // SQLクエリの結果に応じた動的なJSONオブジェクト
      // 例：
      "id": 1,
      "year": "2025",
      "title": "プログラミング基礎"
    }
  ],
  "row_count": 1,
  "execution_time": "0.123s"
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
- 使用許可命令
  - .tables
  - pragma
  - select
- 全テーブル使用許可
- 1回のクエリで返却される最大行数：1000行
- クエリ実行の最大時間：30秒
- 複数命令可（但し構文解析を行う)

### 主なエラーコード
- 400: リクエストパラメータが不正
- 403: 許可されていないSQLクエリ（SELECT以外）
- 404: リソースが見つからない
- 408: クエリ実行がタイムアウト
- 500: サーバー内部エラー

## レート制限
- 現時点では制限なし（将来的に必要に応じて実装）

## 注意事項
- すべてのレスポンスはJSONフォーマットで返却
- 日時フォーマットはISO 8601形式を使用
- 文字エンコーディングはUTF-8

## SQLインジェクションポリシー

### 基本方針
- すべてのSQLクエリは構文解析を経て実行される
- パラメータ化されたクエリのみ受け付ける
- 許可された命令のみ実行可能

### パラメータ化
1. クエリ形式
```sql
-- 基本形式
SELECT * FROM table WHERE column = ?

-- 複数パラメータ
SELECT * FROM table WHERE column1 = ? AND column2 = ?

-- IN句の場合
SELECT * FROM table WHERE column IN (?, ?, ?)
```

2. パラメータの受け渡し
```json
{
  "query": "SELECT * FROM syllabus WHERE year = ? AND semester = ?",
  "params": ["2025", "前期"]
}
```

### 論理演算子の使用
1. 基本形式
```sql
-- ANDの使用
SELECT * FROM table WHERE column1 = ? AND column2 = ?

-- ORの使用
SELECT * FROM table WHERE column1 = ? OR column2 = ?

-- AND/ORの組み合わせ
SELECT * FROM table WHERE (column1 = ? OR column2 = ?) AND column3 = ?
```

2. パラメータ化された論理演算の例
```json
{
  "query": "SELECT * FROM syllabus WHERE (year = ? OR year = ?) AND semester = ?",
  "params": ["2024", "2025", "前期"]
}
```

3. 複雑な条件の例
```json
{
  "query": "SELECT * FROM syllabus WHERE (faculty = ? OR faculty = ?) AND (year = ? OR semester = ?) AND teacher = ?",
  "params": ["文学部", "経済学部", "2025", "前期", "山田太郎"]
}
```

4. 注意事項
- 括弧`()`による優先順位の明示を推奨
- 条件の複雑さに応じた適切なインデックスの使用
- 過度に複雑な条件は実行計画の検証で制限される可能性あり

### 構文解析プロセス
1. クエリの分割
   - セミコロンで区切られた複数のクエリを個別に解析
   - 各クエリの構文を検証

2. 命令の検証
   - 許可された命令のみ実行可能
     - `.tables`: テーブル一覧の取得
     - `pragma`: テーブル情報の取得
     - `select`: データの取得
   - その他の命令は即時エラー

3. セキュリティチェック
   - テーブル名の検証
   - カラム名の検証
   - 条件句の検証

### 複数命令実行
```json
{
  "queries": [
    {
      "query": ".tables",
      "params": []
    },
    {
      "query": "SELECT * FROM syllabus WHERE year = ?",
      "params": ["2025"]
    },
    {
      "query": "PRAGMA table_info(syllabus)",
      "params": []
    }
  ]
}
```

### エラー処理
1. 構文エラー
```json
{
  "status": "error",
  "error": {
    "code": "SYNTAX_ERROR",
    "message": "SQLクエリの構文が不正です",
    "details": "構文解析エラーの詳細",
    "query_index": 0  // 複数クエリの場合、エラーが発生したクエリのインデックス
  }
}
```

2. 不正な命令
```json
{
  "status": "error",
  "error": {
    "code": "INVALID_COMMAND",
    "message": "許可されていない命令が含まれています",
    "details": "INSERT/UPDATE/DELETE等の命令は許可されていません",
    "query_index": 1
  }
}
```

3. パラメータエラー
```json
{
  "status": "error",
  "error": {
    "code": "PARAM_ERROR",
    "message": "パラメータの数が一致しません",
    "details": "クエリのパラメータ数: 2, 提供されたパラメータ数: 1",
    "query_index": 0
  }
}
```

### セキュリティ上の注意
- すべてのパラメータは型チェックを実施
- エスケープ処理は自動的に実施
- テーブル名やカラム名のホワイトリスト検証
- クエリの実行前に必ずEXPLAINを実行
- 実行計画の検証によるパフォーマンス保護

[トップへ](#)