# raw_page_parser.py

[readmeへ](../../README.md)

## 概要
シラバス検索ページのHTMLファイルから科目情報を抽出し、JSONファイルとして保存します。

## 使用方法
```bash
python src/db/raw_page_parser.py -y YEAR
```

### オプション
- `-y`, `--year`: 対象年度（必須）

## 入力
- `src/syllabus/{年}/search_page/*.html`
  - シラバス検索結果のHTMLファイル
  - テーブルクラス`dataT`から科目情報を抽出

## 出力
- `db/updates/subject/add/{subject_code}.json`
  ```json
  {
    "subject_code": "科目コード",
    "name": "科目名",
    "class_name": "科目区分",
    "subclass_name": "科目小区分",
    "note": "備考"
  }
  ```

## 処理内容
1. HTMLファイルの読み込み
2. テーブルから以下の情報を抽出
   - 属性カラム：「：」と「・」で分解し、note、class_name、subclass_nameを取得
   - 科目名カラム：科目名とリンクから科目コードを取得
3. 抽出した情報をJSONファイルとして保存

## デバッグ機能
- 処理中のログを出力
- 整形されたHTMLを`.pretty.html`として保存（初回のみ） 