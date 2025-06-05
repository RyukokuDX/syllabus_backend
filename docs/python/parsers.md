# パーサー一覧

[readmeへ](../../README.md)

## 目次
1. [概要](#概要)
2. [パーサー一覧](#パーサー一覧)
3. [実行方法](#実行方法)
4. [更新履歴](#更新履歴)

## 概要

このドキュメントでは、シラバスデータベースの構築に使用される各パーサーの役割と処理内容について説明します。
各パーサーは特定のデータソースから情報を抽出し、データベースに格納するための処理を行います。

## パーサー一覧

| パーサー名 | ファイル名 | 処理内容 | データソース |
|------------|------------|----------|--------------|
| 科目区分パーサー | 01_class.py | 科目区分の抽出 | `src/course_guide/{year}/csv/*.csv`（タブ区切り） |
| 科目細分パーサー | 02_subclass.py | 科目細分の抽出 | `src/course_guide/{year}/csv/*.csv`（タブ区切り） |
| 学部パーサー | 03_faculty.py | 学部情報の抽出 | `src/course_guide/{year}/csv/*.csv`（タブ区切り） |
| 科目名パーサー | 04_subject_name.py | 科目名の抽出 | `src/course_guide/{year}/csv/*.csv`（タブ区切り） |
| 教員パーサー | 05_instructor.py | 教員情報の抽出 | `src/course_guide/{year}/csv/*.csv`（タブ区切り） |
| 教科書パーサー | 06_book.py | 教科書情報の抽出 | `src/syllabus/{year}/html/*.html` |
| 教科書著者パーサー | 07_book_author.py | 教科書著者情報の抽出 | `src/syllabus/{year}/html/*.html` |
| シラバスマスターパーサー | 08_syllabus_master.py | シラバス基本情報の抽出 | `src/syllabus/{year}/html/*.html` |
| シラバスパーサー | 09_syllabus.py | シラバス詳細情報の抽出 | `src/syllabus/{year}/html/*.html` |
| 科目成績パーサー | 10_subject_grade.py | 成績情報の抽出 | `src/course_guide/{year}/csv/*.csv`（タブ区切り） |
| 科目属性パーサー | 16_subject_attribute.py | 科目属性の抽出 | `src/course_guide/{year}/csv/*.csv`（タブ区切り） |
| 科目パーサー | 17_subject.py | 科目情報の統合 | `src/syllabus/{year}/data/syllabus_{year}.db` |
| 科目属性値パーサー | 19_subject_attribute_value.py | 科目属性値の抽出 | `src/course_guide/{year}/csv/*.csv`（タブ区切り） |

## 実行方法

パーサーは以下のコマンドで実行できます：

```bash
./syllabus.sh parser [パーサー名または番号]
```

> **注意:** `src/course_guide/{year}/csv/*.csv` のデータソースは**タブ区切り**です。

例：
```bash
./syllabus.sh parser 01  # 科目区分パーサーを実行
./syllabus.sh parser class  # 科目区分パーサーを実行
```

## 更新履歴

| 日付 | バージョン | 更新者 | 内容 |
|------|------------|--------|------|
| 2024-03-20 | 1.0.0 | 開発者 | 初版作成 |

[🔝 ページトップへ](#パーサー一覧) 