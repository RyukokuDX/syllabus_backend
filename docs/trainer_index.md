---
title: トレーニングデータインデックス
file_version: v1.0.2
project_version: v3.0.5
last_updated: 2025-07-10
---

# トレーニングデータインデックス

- File Version: v1.0.2
- Project Version: v3.0.5
- Last Updated: 2025-07-10

[ドキュメント作成ガイドラインへ](./doc.md)

## 目次
1. [概要](#概要)
2. [トレーニングデータ一覧](#トレーニングデータ一覧)
3. [ページトップへ](#トレーニングデータインデックス)

## 概要
本ドキュメントは、trainerディレクトリ配下の学習データ用SQL・レスポンスファイルの対応関係を一覧化したものです。
SQLファイルのYAML front matterコメントからorderやdesc等を抽出し、対応するレスポンスファイルの有無・件数も自動集計しています。

## トレーニングデータ一覧

| order（自然言語クエリ） | SQLファイル | レスポンス |
|------------------------|------------|-----------|
| 青井先生の2025年の担当科目一覧を科目名と対象課程のリストの形で表示する | [📄](trainer/sql/aoi_2025.sql) | [📄](trainer/response/aoi_2025.tsv) |
|  | [📄](trainer/sql/check_tokubetu_kenkyu.sql) | [📄](trainer/response/check_tokubetu_kenkyu.tsv) |
| 知能の専門応用科目で使用する教科書の冊数と総額を取得 | [📄](trainer/sql/chinou_book.sql) | [📄](trainer/response/chinou_book.tsv) |
| 科目名に「結晶学入門」を含む全レコードの詳細をJSON形式で抽出する | [📄](trainer/sql/kessyou_kougaku_full.sql) | [📄](trainer/response/kessyou_kougaku_full.tsv) |
| 機械の必修科目のうち、期末試験がない科目の科目名一覧を取得 | [📄](trainer/sql/kikai_mandatory_noexam.sql) | [📄](trainer/response/kikai_mandatory_noexam.tsv) |
| 登録されている最も高い本を利用している科目情報を抽出する | [📄](trainer/sql/lecture_of_the_most_expensive_book.sql) | [📄](trainer/response/lecture_of_the_most_expensive_book.tsv) |
| 丸山先生の2025年の専門応用科目の担当科目一覧を科目名と対象課程のリストの形で表示する | [📄](trainer/sql/maruyama_2025.sql) | [📄](trainer/response/maruyama_2025.tsv) |
| 丸山先生の2025年の専門基礎科目の担当科目一覧を科目名と対象課程のリストの形で表示する | [📄](trainer/sql/maruyama_basic_2025.sql) | [📄](trainer/response/maruyama_basic_2025.tsv) |
| 数理の専門応用科目のうち、成績評価基準一覧に「レポート」を含まないものを抽出 | [📄](trainer/sql/math_noreport.sql) | [📄](trainer/response/math_noreport.tsv) |
| 最も多くの講義を担当している先生を教えて | [📄](trainer/sql/most_busy_teacher.sql) | [📄](trainer/response/most_busy_teacher.tsv) |
| 課程別に最も高い参考書のリストを作成する | [📄](trainer/sql/most_expensive_refs.sql) | [📄](trainer/response/most_expensive_refs.tsv) |
| 課程別に最も高い教科書のリストを作成する | [📄](trainer/sql/most_expensive_texts.sql) | [📄](trainer/response/most_expensive_texts.tsv) |
| 応用化学の専攻科目の選択科目で、レポートの評価割合が50%以上の科目名と教員名、レポート評価の割合の一覧を取得 | [📄](trainer/sql/ouka_report_over_50.sql) | [📄](trainer/response/ouka_report_over_50.tsv) |

[🔝 ページトップへ](#トレーニングデータインデックス)
