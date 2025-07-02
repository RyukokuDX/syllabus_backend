---
title: 06_book.pyの仕様書
file_version: v2.3.0
project_version: v2.3.0
last_updated: 2025-07-02
---

# `06_book.py`の仕様書　

- File Version: v2.3.0
- Project Version: v2.3.0
- Last Updated: 2025-07-02

[readmeへ](../../README.md) | [ドキュメント作成ガイドラインへ](./doc.md) | [パーサー一覧へ](./parsers.md)

## 目次
1. [概要](#概要)
2. [解析対象](#解析対象)
3. [出力形式](#出力形式)
4. [処理フロー](#処理フロー)
5. [類似度計算](#類似度計算)
6. [BibTeX処理](#bibtex処理)
7. [テーブル分類ルール](#テーブル分類ルール)
8. [categorization_statusの種類](#categorization_statusの種類)

## 概要
`06_book.py`は、シラバスから書籍情報を抽出し、正規のISBNを持つ書籍は`book`テーブル用のJSON、問題のある書籍は`book_uncategorized`テーブル用のJSONを生成するスクリプトです。CiNii APIとBibTeXデータを活用して書籍情報の精度を向上させます。

**注意**: 現在の実装では教科書（`詳細情報.テキスト.内容.書籍`）のみを処理対象としており、参考書（`詳細情報.参考文献.内容.書籍`）は処理されません。

## 解析対象
### 対象ディレクトリ
- `src/syllabus/{year}/json/`
  - `{year}`は後述の方法で取得

### 対象フィールド
現在の実装では以下のフィールドのみを解析対象としています：
- `"詳細情報"."テキスト"."内容"."書籍"`のリスト

**注意**: `"詳細情報"."参考文献"."内容"."書籍"`のリストは現在の実装では処理されていません。

これらのリスト内のレコードを「対象レコード」と呼びます。

## 出力形式
### 基本形式
- 正規のISBNを持つ書籍：`docs/database/structure.md`のbookテーブルのカラムに対応したJSON形式
- 問題のある書籍：`docs/database/structure.md`のbook_uncategorizedテーブルのカラムに対応したJSON形式
- 出力は2つのファイルに分けて生成

### 出力構造

#### bookテーブル用JSON
```json
{
  "books": [
    {
      "title": "書籍タイトル",
      "author": "著者名（カンマ区切り）",
      "publisher": "出版社名",
      "price": 価格,
      "isbn": "正規のISBN番号",
      "created_at": "作成日時"
    }
  ]
}
```

#### book_uncategorizedテーブル用JSON
```json
{
  "book_uncategorized": [
    {
      "syllabus_code": "シラバスコード",
      "title": "書籍タイトル",
      "author": "著者名",
      "publisher": "出版社名",
      "price": 価格,
      "role": "利用方法（教科書、参考書など）",
      "isbn": "ISBN番号（不正・未入力含む）",
      "categorization_status": "未分類理由",
      "created_at": "作成日時",
      "updated_at": "更新日時"
    }
  ]
}
```

## 処理フロー
### 年度取得
1. 起動時の引数で`{year}`を取得
2. 引数が空の場合：
   - ユーザーに入力を再要請
   - 再要請時も空の場合：今年の年数を`{year}`とする

### 書籍情報処理
tqdmで進捗を表示しながら、シラバスJSONの`詳細情報.テキスト.内容.書籍`を以下のように処理：

#### ISBNがnullの場合
- `book_uncategorized`テーブル用JSONに追記
- categorization_status: "ISBNなし"

#### ISBNが存在する場合
- 桁数確認（数字以外の文字を除去した後の長さで判定）
  - 異常あり：
    - `book_uncategorized`テーブル用JSONに追記
    - categorization_status: "不正ISBN: 桁数違反"
  - 異常なし：
    - チェックディジット（cd）確認
      - 異常あり：
        - `book_uncategorized`テーブル用JSONに追記
        - categorization_status: "不正ISBN: cd違反"
      - 異常なし：
        - `src/books/json/{ISBN}.json`の存在確認
          - 存在しない：
            - CiNii APIで検索
              - ヒットなし：
                - `book_uncategorized`テーブル用JSONに追記
                - categorization_status: "問題ISBN: ciniiデータ不在"
              - ヒットあり：
                - `src/books/json/{ISBN}.json`に保存
                - 存在する場合の処理に進む
          - 存在する：
            - BibTeX経由で書籍情報を取得
              - 取得成功：
                - 書籍名の類似度比較
                  - 類似度0.05以下：
                    - `book_uncategorized`テーブル用JSONに追記
                    - categorization_status: "問題レコード: 書籍名類似度低"
                  - 類似度0.05以上：
                    - priceフィールド：該当レコードから取得
                    - その他：BibTeXから取得
                    - `book`テーブル用JSONに追記
              - 取得失敗：
                - 既存のCiNiiデータを使用
                - 書籍名の類似度比較（閾値0.05）
                - 類似度が低い場合は`book_uncategorized`テーブル用JSONに追記

### 著者情報の処理
- 書籍情報の`author`フィールドはカンマ区切りの文字列として保存
- 著者名の正規化（前後の空白除去、重複除去）を実施
- 複数の区切り文字に対応（カンマ、セミコロン、and、ほか）
- シラバス、BibTeX、CiNiiの順で著者情報を取得し、存在する場合は正規化して使用
- `normalize_author()`関数で著者名の統一的な正規化を実施

### 参考書の処理について
現在の実装では、`詳細情報.参考文献.内容.書籍`の処理は実装されていません。参考書の情報も含めて処理する場合は、実装の拡張が必要です。

## 類似度計算
### 概要
書籍名の類似度は、文字列の類似度と単語の類似度を組み合わせて計算します。

### 計算方法
1. 前処理
   - 大文字小文字の違いを無視
   - 記号の違いを無視
   - 余分な空白を正規化

2. 類似度の計算
   - 文字列の類似度（重み: 0.7）
     - レーベンシュタイン距離を使用
     - 距離が小さいほど類似度が高い
   - 単語の類似度（重み: 0.3）
     - 共通する単語の割合を計算
     - シリーズ名の違いによる影響を軽減

3. 閾値
   - 0.05未満：明らかに異なる書籍（book_uncategorizedテーブルに分類）
   - 0.05以上：同じ書籍の可能性が高い（bookテーブルに分類）

## BibTeX処理
### 処理フロー
1. 既存JSONファイルからBN（CiNii ID）を抽出
2. `src/books/bib/{BN}.bib`の存在確認
3. 存在しない場合：
   - CiNiiからBibTeXファイルを取得
   - `src/books/bib/{BN}.bib`に保存
4. BibTeXファイルをパースして書籍情報を抽出

### BibTeXパーサー
- 正しいBibTeX形式に対応
- author、title、publisherフィールドを抽出
- ダブルクォートとカンマの適切な処理

### データ保存先
- JSONファイル: `src/books/json/{ISBN}.json`
- BibTeXファイル: `src/books/bib/{BN}.bib`

## テーブル分類ルール
### bookテーブル（正規のISBNを持つ書籍）
以下の条件を全て満たす書籍：
- ISBNが存在する
- ISBNの桁数が正しい（10桁または13桁）
- ISBNのチェックディジットが正しい
- CiNii APIで書籍情報が取得できる
- 書籍名の類似度が0.05以上

### book_uncategorizedテーブル（問題のある書籍）
以下のいずれかの条件に該当する書籍：
- ISBNが存在しない
- ISBNの桁数が不正
- ISBNのチェックディジットが不正
- CiNii APIで書籍情報が取得できない
- 書籍名の類似度が0.05未満
- BibTeXデータでタイトル、著者、出版社が空

**注意**: 現在の実装では教科書のみを処理対象としており、参考書は処理されません。

## categorization_statusの種類
### 未分類理由の分類
1. **ISBNなし**
   - ISBNフィールドが空またはnullの場合

2. **不正ISBN: 桁数違反**
   - ISBNの桁数が10または13でない場合

3. **不正ISBN: cd違反**
   - ISBNのチェックディジットが正しくない場合

4. **問題ISBN: ciniiデータ不在**
   - CiNii APIで書籍情報が見つからない場合

5. **問題レコード: 書籍名類似度低**
   - シラバスとCiNii/BibTeXの書籍名の類似度が0.05未満の場合

6. **不正BibTeX データ: Null検知**
   - BibTeXデータでタイトル、著者、出版社が空の場合

7. **不正CiNii データ: Null検知**
   - CiNiiデータでタイトル、著者、出版社が空の場合

### デバッグ情報
- tqdm.writeを使用して詳細なデバッグ情報を出力
- 処理中の書籍情報、類似度計算結果、データ取得状況を記録
- テーブル分類結果を記録

[🔝 ページトップへ](#06_bookpyの仕様書)