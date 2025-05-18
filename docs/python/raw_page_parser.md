# シラバスページパーサー (`raw_page_parser.py`)

[readmeへ](../../README.md) | [データベース構造へ](../database/structure.md) | [ライブラリ仕様へ](../database/python.md)

## 概要
`src/db/raw_page_parser.py`は、HTMLファイルからシラバス情報を抽出し、JSONファイルとして保存するスクリプトです。
科目情報とシラバス詳細情報の両方を処理できます。

## 処理フロー
1. 指定されたディレクトリ内のHTMLファイルを検索
2. 各HTMLファイルに対して:
   - BeautifulSoupを使用してHTMLを解析
   - データ型に応じて適切なパーサーを実行
   - 抽出したデータをJSONファイルとして保存

## 対応データ型
| データ型 | 処理内容 |
|---------|----------|
| subject | 科目一覧テーブルから科目情報を抽出 |
| syllabus | シラバス詳細ページから情報を抽出 |

## コマンドラインオプション
```bash
python src/db/raw_page_parser.py -y [年度] -t [データ型]
```

### オプション
| オプション | 説明 | 必須 |
|-----------|------|------|
| -y, --year | 処理対象の年度（例：2025） | はい |
| -t, --type | 処理対象のデータ型（subject または syllabus） | はい |

## 出力形式

### 科目情報（subject）
```json
{
    "content": {
        "subject_code": "G250110001",
        "name": "科目名",
        "class_name": "教養科目",
        "subclass_name": "社会系化学",
        "class_note": "2015年度以降",
        "created_at": "2024-05-18T12:34:56.789Z",
        "updated_at": null
    }
}
```

- 科目区分の分解は、
`{class_note}：{class_name}・{subclass_name}`
としている.
   - 例１: `必修外国語・英語`なら
      - "class_name": "必修外国語",
      - "subclass_name": "英語",
      - "class_note": "",
   - 例2: `2015年度以降入学：教養科目・社会系科学`なら
      - "class_name": "教養科目",
      - "subclass_name": "社会系化学",
      - "class_note": "2015年度以降",


### シラバス情報（syllabus）
```json
{
    "content": {
        "syllabus_id": "G250110001",
        "subject_code": "G250110001",
        "year": 2025,
        "subtitle": "サブタイトル",
        "term": "前期",
        "lecture_code": "G111",
        "grade_b1": true,
        "grade_b2": false,
        "grade_b3": false,
        "grade_b4": false,
        "grade_m1": false,
        "grade_m2": false,
        "grade_d1": false,
        "grade_d2": false,
        "grade_d3": false,
        "campus": "キャンパス名",
        "credits": 2,
        "summary": "講義概要",
        "goals": "到達目標",
        "methods": "講義方法"
    }
}
```

## 処理の詳細

### 科目情報の抽出（parse_subject_table）
1. 科目一覧テーブルの特定
   - 属性と科目名を含むテーブルを検索
2. 各行の処理
   - 科目コードの抽出（リンクのhref属性から）
   - 科目名の抽出（@記号以前の部分）
   - 属性の分解（クラス名、サブクラス名、備考）

### シラバス情報の抽出（parse_syllabus_detail）
1. 基本情報の抽出
   - シラバス管理番号
   - 科目コード
   - 開講年度
   - サブタイトル
2. 開講情報の抽出
   - 開講期（前期/後期/通年）
   - 講義コード
   - 配当年次
   - キャンパス
   - 単位数
3. 講義内容の抽出
   - 講義概要
   - 到達目標
   - 講義方法

## 出力ディレクトリ
- 科目情報: `db/updates/subject/add/`
- シラバス情報: `db/updates/syllabus/add/`

## エラーハンドリング
1. ファイル処理エラー
   - ファイルが存在しない
   - ファイルの読み込みエラー
   - HTMLの解析エラー

2. データ抽出エラー
   - 必要な要素が見つからない
   - データ形式が不正
   - 値の変換エラー

## 注意事項
1. HTMLファイルの形式
   - 整形されたHTMLファイル（.pretty.html）を自動生成
   - 既存の整形ファイルは上書きしない

2. データの整合性
   - 科目コードとシラバス管理番号の対応
   - 年度情報の整合性
   - 必須フィールドの存在確認

## 更新履歴

| 日付 | バージョン | 更新者 | 内容 |
|------|------------|--------|------|
| 2024-03-20 | 1.0.0 | 藤原 | 初版作成 |
| 2024-05-18 | 1.1.0 | 藤原 | サブタイトル抽出の修正 |

### バージョン1.1.0の主な変更点
1. サブタイトル抽出の改善
   - `th`要素の検索方法を修正
   - より正確なサブタイトル抽出を実現

## 関連ドキュメント
- [データベース構造定義](../database/structure.md)
- [データベース操作クラス](database.md)
- [モデル定義](models.md)
- [DB更新スクリプト](update_db.md)
- [DB更新手順](../database_update_workflow.md)

[🔝 ページトップへ](#シラバスページパーサー-raw_page_parserpy) 