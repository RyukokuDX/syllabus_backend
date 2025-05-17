# シラバス検索ページパーサー (`raw_page_parser.py`)

[readmeへ](../../README.md) | [DB更新手順へ](../database_update_workflow.md)

## 概要
シラバス検索ページのHTMLファイルから科目情報を抽出し、データベース更新用のJSONファイルを生成します。
BeautifulSoupを使用してHTMLを解析し、必要な情報を構造化されたデータとして取得します。

## 機能
- HTMLファイルの解析
- 科目情報の抽出
- JSONファイルの生成
- デバッグ用の整形HTMLの出力

## 使用方法

### コマンドライン
```bash
# 基本的な使用方法
python src/db/raw_page_parser.py -y 2024

# デバッグモードで実行（詳細なログ出力）
python src/db/raw_page_parser.py -y 2024 --debug
```

### オプション
| オプション | 説明 | デフォルト値 |
|------------|------|--------------|
| `-y`, `--year` | 対象年度（必須） | - |
| `--debug` | デバッグモードの有効化 | False |
| `--output-dir` | 出力ディレクトリの指定 | `db/updates/subject/add` |

## 入力ファイル
### ディレクトリ構造
```
src/syllabus/{年}/search_page/
  ├── page1.html
  ├── page2.html
  └── ...
```

### HTMLファイル形式
```html
<table class="dataT">
  <tr>
    <td class="attribute">専門科目：情報系・必修</td>
    <td class="subject">
      <a href="syllabus.php?code=SUBJ001">プログラミング基礎</a>
    </td>
  </tr>
  <!-- 他の科目情報 -->
</table>
```

## 出力ファイル
### ディレクトリ構造
```
db/updates/subject/add/
  ├── SUBJ001.json
  ├── SUBJ002.json
  └── ...
```

### JSONファイル形式
```json
{
  "content": {
    "subject_code": "SUBJ001",
    "name": "プログラミング基礎",
    "class_name": "専門科目",
    "subclass_name": "情報系",
    "class_note": "必修"
  }
}
```

## 処理フロー
1. コマンドライン引数の解析
   - 年度の取得
   - オプションの設定

2. HTMLファイルの読み込み
   - 指定された年度のディレクトリからHTMLファイルを検索
   - BeautifulSoupによるパース
   - デバッグモード時は整形HTMLを出力

3. データの抽出
   - テーブルの特定（class="dataT"）
   - 各行からの情報抽出
     - 属性カラム：「：」と「・」で分解
     - 科目名カラム：科目名とリンクから科目コードを取得

4. JSONファイルの生成
   - 科目ごとにJSONファイルを作成
   - 出力ディレクトリに保存

## エラーハンドリング
- HTMLファイルが存在しない場合
- HTMLの構造が不正な場合
- 必須情報が取得できない場合
- ファイル書き込み権限がない場合

## デバッグ機能
- 詳細なログ出力
  - ファイル処理状況
  - 抽出データの内容
  - エラー情報
- 整形されたHTMLの出力
  - ファイル名: `{元のファイル名}.pretty.html`
  - 1回目の実行時のみ生成

## 関連ドキュメント
- [DB更新手順](../database_update_workflow.md)
- [DB更新スクリプト](update_db.md)

## 更新履歴

| 日付 | バージョン | 更新者 | 内容 |
|------|------------|--------|------|
| 2024-03-20 | 1.0.0 | 藤原 | 初版作成 |
| 2024-03-21 | 1.1.0 | 藤原 | 処理フローとデバッグ機能の説明を追加 |

[🔝 ページトップへ](#シラバス検索ページパーサー-raw_page_parserpy) 