# update_db.md

[readmeへ](../../README.md) | [データベース構造へ](../database_structure.md) | [ライブラリ仕様へ](../database_python.md)

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

## 終了コード
- 0: 正常終了
- 1: エラー終了（エラーメッセージを表示）

## 更新履歴

| 日付 | バージョン | 更新者 | 内容 |
|------|------------|--------|------|
| 2024-03-20 | 1.0.0 | 藤原 | 初版作成 | 

[🔝 ページトップへ](#update_dbmd)