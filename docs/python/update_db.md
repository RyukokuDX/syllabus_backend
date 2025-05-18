# データベース更新スクリプト (`update_db.py`)

[readmeへ](../../README.md) | [データベース構造へ](../database/structure.md) | [ライブラリ仕様へ](../database/python.md)

## 概要
`src/db/update_db.py`は、JSONファイルからデータベースを更新するためのスクリプトです。
データの整合性チェックと更新処理を一元的に管理します。

## 処理フロー
1. `db/updates/*/*/*.json`内のJSONファイルを検索（`add`と`modify`ディレクトリのみ）
2. 各JSONファイルに対して:
   - データの整合性をチェック（データクラスによる厳格な型チェック）
   - 整合性に問題がある場合は処理を中止し、エラー内容を表示
   - 整合性が確認できた場合はデータベースを更新
   - 処理成功時は`registered`ディレクトリに移動

## ディレクトリ構造
```
db/updates/
  ├── subject/                # データ型ごとのディレクトリ
  │   ├── add/               # 新規追加用
  │   │   └── *.json
  │   ├── modify/           # 更新用
  │   │   └── *.json
  │   └── registered/       # 処理済み
  │       └── YYYY-MM/      # 年月ごとのアーカイブ
  │           └── *.json
  └── ...
```

## JSONファイル形式
### 単一データの場合
```json
{
    "content": {
        "field1": "value1",
        "field2": "value2",
        ...
    }
}
```

### 複数データの場合
```json
{
    "content": [
        {
            "field1": "value1",
            "field2": "value2",
            ...
        },
        {
            "field1": "value3",
            "field2": "value4",
            ...
        }
    ]
}
```

## 対応データ型
| データ型 | モデルクラス | テーブル名 |
|---------|-------------|------------|
| subject | Subject | subject |
| syllabus | Syllabus | syllabus |
| syllabus_time | SyllabusTime | syllabus_time |
| instructor | Instructor | instructor |
| book | Book | book |
| grading_criterion | GradingCriterion | grading_criterion |
| syllabus_instructor | SyllabusInstructor | syllabus_instructor |
| lecture_session | LectureSession | lecture_session |
| syllabus_textbook | SyllabusTextbook | syllabus_textbook |
| syllabus_reference | SyllabusReference | syllabus_reference |
| syllabus_faculty | SyllabusFaculty | syllabus_faculty |
| subject_requirement | SubjectRequirement | subject_requirement |
| subject_program | SubjectProgram | subject_program |

## エラーハンドリング
1. JSONファイルの形式エラー
   - ファイルが存在しない
   - JSONとして不正
   - 必須フィールドの欠落

2. データ型エラー
   - 未知のデータ型
   - フィールドの型が不正
   - 必須フィールドの値が不正

3. データベースエラー
   - 接続エラー
   - SQLエラー
   - トランザクションエラー

## 処理済みファイルの管理
- 移動先: `db/updates/[データ型]/registered/YYYY-MM/[ファイル名]`
- 同名ファイルが存在する場合は連番を付加: `[元のファイル名]_[連番].[拡張子]`
- エラー発生時はファイルを移動せず、元の場所に保持

## 実行方法
```bash
python src/db/update_db.py
```

### オプション
現在のバージョンでは、コマンドラインオプションは実装されていません。
すべての設定は以下のデフォルト値で動作します：

- 更新対象ディレクトリ: `db/updates/*/add` および `db/updates/*/modify`
- ログレベル: INFO
- ログファイル: `db/updates/update.log`

### 処理の詳細

1. データの検証
   - データクラスによる厳格な型チェック
   - 必須フィールドの存在確認
   - 値の範囲チェック
   - 関連テーブルとの整合性チェック

2. データベース操作
   - `add`操作の場合:
     ```sql
     INSERT OR REPLACE INTO [テーブル名] ([カラム名], ...)
     VALUES (?, ...)
     ```
   - `modify`操作の場合:
     ```sql
     UPDATE [テーブル名]
     SET [カラム名] = ?, ...
     WHERE [主キー] = ?
     ```

3. トランザクション管理
   - 各ファイルの処理は独立したトランザクションで実行
   - エラー発生時はロールバック
   - 正常終了時はコミット

4. エラー処理
   - ファイル単位でのエラーハンドリング
   - レコード単位でのエラーハンドリング
   - エラー発生時のログ出力
   - エラー発生時の処理継続可否の判断

5. ログ出力
   - 処理開始時の情報
     - 処理開始時刻
     - 対象ファイル数
   - ファイル処理時の情報
     - ファイル名
     - データ型
     - レコード数
   - エラー情報
     - エラーの種類
     - エラーの詳細
     - スタックトレース
   - 処理終了時の情報
     - 処理終了時刻
     - 成功件数
     - エラー件数

### 戻り値
- 0: 正常終了
- 1: エラー終了
  - データの整合性エラー
  - データベースエラー
  - ファイルシステムエラー
  - その他の予期せぬエラー

### 注意事項
1. データベースのバックアップ
   - 更新前にデータベースのバックアップを取得することを推奨
   - 大量のデータを更新する場合は特に注意

2. ディスク容量
   - ログファイルは自動的に作成され、継続的に成長
   - 定期的なログローテーションを推奨

3. パフォーマンス
   - 大量のファイルを一度に処理する場合は時間がかかる可能性
   - メモリ使用量に注意

## 終了コード
- 0: 正常終了
- 1: エラー終了（エラーメッセージを表示）

## 更新履歴

| 日付 | バージョン | 更新者 | 内容 |
|------|------------|--------|------|
| 2024-03-20 | 1.0.0 | 藤原 | 初版作成 |
| 2024-05-18 | 1.1.0 | 藤原 | ログ機能の追加と処理の改善 |

### バージョン1.1.0の主な変更点

1. ログ機能の追加
   - ログレベル: INFO
   - ログファイル: `db/updates/update.log`
   - ログフォーマット: タイムスタンプ、ログレベル、メッセージ
   - コンソール出力とファイル出力の両方をサポート

2. 処理の改善
   - 各処理段階でのログ出力
     - 処理開始・終了
     - ファイル検出状況
     - JSONファイルの読み込み
     - データの検証結果
     - データベース操作（INSERT/UPDATE）
     - エラー発生時の詳細情報
   - エラーハンドリングの強化
     - 各処理段階でのエラーを詳細に記録
     - レコード単位でのエラー情報を記録

3. データベース操作の改善
   - `add`操作: `INSERT OR REPLACE`を使用
   - `modify`操作: `UPDATE`を使用
   - 主キー（`subject_code`または`syllabus_id`）に基づく更新

## 関連ドキュメント
- [データベース構造定義](../database/structure.md)
- [データベース操作クラス](database.md)
- [モデル定義](models.md)
- [シラバスページパーサー](raw_page_parser.md)
- [DB更新手順](../database_update_workflow.md)

[🔝 ページトップへ](#データベース更新スクリプト-update_dbpy)