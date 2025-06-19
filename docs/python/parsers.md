---
title: パーサー一覧
file_version: v1.1.1
project_version: v1.3.8
last_updated: 2025-06-19
---

# パーサー一覧

- File Version: v1.1.1
- Project Version: v1.3.8
- Last Updated: 2025-06-19

[readmeへ](../../README.md)

## 目次
1. [概要](#概要)
2. [パーサー一覧](#パーサー一覧)
3. [実行方法](#実行方法)

## 概要

このドキュメントでは、シラバスデータベースの構築に使用される各パーサーの役割と処理内容について説明します。
各パーサーは特定のデータソースから情報を抽出し、データベースに格納するための処理を行います。

## パーサー一覧

> **注意:** `src/course_guide/{year}/csv/*.csv` のデータソースは**タブ区切り**です。

| パーサー名 | ファイル名 | 処理内容 | データソース | 対応テーブル |
|------------|------------|----------|--------------|--------------|
| 科目区分パーサー | 01_class.py | 科目区分の抽出 | `src/course_guide/{year}/csv/*.csv`（タブ区切り） | class |
| 科目小区分パーサー | 02_subclass.py | 科目小区分の抽出 | `src/course_guide/{year}/csv/*.csv`（タブ区切り） | subclass |
| 学部パーサー | 03_faculty.py | 学部情報の抽出 | `src/course_guide/{year}/csv/*.csv`（タブ区切り） | faculty |
| 科目名パーサー | 04_subject_name.py | 科目名の抽出 | `src/syllabus/{year}/json/*.json` | subject_name |
| 教員パーサー | 05_instructor.py | 教員情報の抽出 | `src/syllabus/{year}/json/*.json` | instructor |
| 書籍パーサー | 06_book.py | 書籍情報の抽出 | `src/syllabus/{year}/json/*.json` | book |
| シラバスマスターパーサー | 07_syllabus_master.py | シラバスマスター情報の抽出 | `src/syllabus/{year}/json/*.json` | syllabus_master |
| シラバスパーサー | 09_syllabus.py | シラバス詳細情報の抽出 | `src/syllabus/{year}/json/*.json` | syllabus |
| 科目履修可能学年パーサー | 10_subject_grade.py | 履修可能学年の抽出 | `src/syllabus/{year}/json/*.json` | subject_grade |
| 科目属性パーサー | 16_subject_attribute.py | 科目属性の抽出 | `src/course_guide/{year}/csv/*.csv`（タブ区切り） | subject_attribute |
| 科目パーサー | 17_subject.py | 科目情報の統合 | `src/course_guide/{year}/csv/*.csv`（タブ区切り） | subject |
| 科目属性値パーサー | 19_subject_attribute_value.py | 科目属性値の抽出 | `src/course_guide/{year}/csv/*.csv`（タブ区切り） | subject_attribute_value |

### 未実装パーサー（structure.md準拠）

以下のパーサーは`structure.md`で定義されているが、まだ実装されていません：

| パーサー名 | ファイル名 | 処理内容 | データソース | 対応テーブル |
|------------|------------|----------|--------------|--------------|
| 講義時間パーサー | 11_lecture_time.py | 講義時間情報の抽出 | `src/syllabus/{year}/json/*.json` | lecture_time |
| 講義セッションパーサー | 12_lecture_session.py | 講義セッション情報の抽出 | `src/syllabus/{year}/json/*.json` | lecture_session |
| シラバス教員関連パーサー | 13_syllabus_instructor.py | シラバス教員関連の抽出 | `src/syllabus/{year}/json/*.json` | syllabus_instructor |
| 講義セッション教員パーサー | 14_lecture_session_instructor.py | 講義セッション教員の抽出 | `src/syllabus/{year}/json/*.json` | lecture_session_instructor |
| シラバス教科書関連パーサー | 15_syllabus_book.py | シラバス教科書関連の抽出 | `src/syllabus/{year}/json/*.json` | syllabus_book |
| 成績評価基準パーサー | 18_grading_criterion.py | 成績評価基準の抽出 | `src/syllabus/{year}/json/*.json` | grading_criterion |
| 科目シラバス関連パーサー | 20_subject_syllabus.py | 科目シラバス関連の抽出 | `src/course_guide/{year}/csv/*.csv`（タブ区切り） | subject_syllabus |
| シラバス系統的履修パーサー | 21_syllabus_study_system.py | シラバス系統的履修の抽出 | `src/syllabus/{year}/json/*.json` | syllabus_study_system |

## 実行方法

パーサーは以下のコマンドで実行できます：

```bash
./syllabus.sh parser [パーサー名または番号]
```

例：
```bash
./syllabus.sh parser 01  # 科目区分パーサーを実行
./syllabus.sh parser class  # 科目区分パーサーを実行
```

[🔝 ページトップへ](#パーサー一覧) 