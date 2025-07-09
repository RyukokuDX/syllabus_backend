---
title: トレーニングデータインデックス
file_version: v1.0.1
project_version: v3.0.1
last_updated: 2025-07-09
---

# トレーニングデータインデックス

- File Version: v1.0.1
- Project Version: v3.0.1
- Last Updated: 2025-07-09

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
| 知能の専門応用科目で使用する教科書の冊数と総額を取得 | [📄](trainer/sql/chinou_book.sql) | [📄](trainer/response/chinou_book.tsv) |
| 数理の専門応用科目のうち、成績評価基準一覧に「レポート」を含まないものを抽出 | [📄](trainer/sql/math_noreport.sql) | [📄](trainer/response/math_noreport.tsv) |

[🔝 ページトップへ](#トレーニングデータインデックス)
