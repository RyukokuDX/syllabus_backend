---
title: データベース構造定義
file_version: v3.0.0
project_version: v3.0.0
last_updated: 2025-07-08
---
<!-- Curosr はversion 弄るな -->

<!--
更新時の注意事項:
- 準拠の意味は、類推せずに内容に従うという意味です
- 更新前に必ず docs/database/policy.md の内容を確認し、structure.mdの更新はpolicy.mdに準拠すること
- 更新が承認された後、以下のファイルを docs/database/structure.md に準拠して更新すること
    - docs/database/er.md
    - src/db/models.py
    - docker/postgresql/init/init.sql.template
    - src/db/migratinos/*.py
-->

# データベース構造定義

- File Version: v3.0.0
- Project Version: v3.0.0
- Last Updated: 2025-07-08

[readmeへ](../../README.md) | [設計ポリシーへ](policy.md) | [ER図へ](er.md)

## 目次

### テーブル構成
1. [class 科目区分](#class-科目区分)
2. [subclass 科目小区分](#subclass-科目小区分)
3. [faculty 開講学部・課程](#faculty-開講学部課程)
4. [subject_name 科目名マスタ](#subject_name-科目名マスタ)
5. [instructor 教員](#instructor-教員)
6. [syllabus_master シラバスマスタ](#syllabus_master-シラバスマスタ)
7. [book 書籍](#book-書籍)
8. [book_uncategorized 未分類書籍](#book_uncategorized-未分類書籍)
9. [syllabus シラバス情報](#syllabus-シラバス情報)
10. [subject_grade 科目履修可能学年](#subject_grade-科目履修可能学年)
11. [lecture_time 講義時間](#lecture_time-講義時間)
12. [lecture_session 講義回数](#lecture_session-講義回数)
13. [lecture_session_irregular 不定形講義回数](#lecture_session_irregular-不定形講義回数)
14. [syllabus_instructor シラバス教員関連](#syllabus_instructor-シラバス教員関連)
15. [lecture_session_instructor 講義回数担当者](#lecture_session_instructor-講義回数担当者)
16. [syllabus_book シラバス教科書関連](#syllabus_book-シラバス教科書関連)
17. [grading_criterion 成績評価基準](#grading_criterion-成績評価基準)
18. [subject_attribute 科目属性](#subject_attribute-科目属性)
19. [subject 科目基本情報](#subject-科目基本情報)
20. [subject_attribute_value 科目属性値](#subject_attribute_value-科目属性値)
21. [syllabus_faculty シラバス学部関連](#syllabus_faculty-シラバス学部関連)
22. [syllabus_study_system シラバス系統的履修](#syllabus_study_system-シラバス系統的履修)


## テーブル構成

### class 科目区分

#### テーブル概要
科目の大区分を管理するテーブル。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|----------|----------|------|------|--------|
| class_id | INTEGER | NO | クラスID（主キー） | システム生成 |
| class_name | TEXT | NO | クラス名 | 履修要綱 |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | class_id | 主キー |
| UNIQUE | class_name | クラス名の一意性 |
| idx_class_name | class_name | クラス名での検索用 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| - | - | - |

[🔝 ページトップへ](#データベース構造定義)

### subclass 科目小区分

#### テーブル概要
科目の小区分を管理するテーブル。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|----------|----------|------|------|--------|
| subclass_id | INTEGER | NO | 小区分ID（主キー） | システム生成 |
| subclass_name | TEXT | NO | 小区分名 | 履修要綱 |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | subclass_id | 主キー |
| UNIQUE | subclass_name | 小区分名の一意性 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| - | - | - |

[🔝 ページトップへ](#データベース構造定義)

### faculty 開講学部・課程

#### テーブル概要
開講学部・課程を管理するテーブル。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|----------|----------|------|------|--------|
| faculty_id | INTEGER | NO | 学部ID（主キー） | システム生成 |
| faculty_name | TEXT | NO | 学部・課程名 | シラバス検索画面 |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | faculty_id | 主キー |
| UNIQUE | faculty_name | 学部・課程名の一意性 |
| idx_faculty_name | faculty_name | 学部・課程名での検索用 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| - | - | - |

[🔝 ページトップへ](#データベース構造定義)

### subject_name 科目名マスタ

#### テーブル概要
科目名を管理するマスタテーブル。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|----------|----------|------|------|--------|
| subject_name_id | INTEGER | NO | 主キー | システム生成 |
| name | TEXT | NO | 科目名 | シラバス検索画面 |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | subject_name_id | 主キー |
| UNIQUE | name | 科目名の一意性 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| - | - | - |

[🔝 ページトップへ](#データベース構造定義)

### instructor 教員

#### テーブル概要
教員の基本情報を管理するテーブル。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|----------|----------|------|------|--------|
| instructor_id | INTEGER | NO | 教員ID（主キー） | システム生成 |
| name | TEXT | NO | 名前 (漢字かカナ) | Web Syllabus |
| name_kana | TEXT | YES | 名前（カナ） | Web Syllabus |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | instructor_id | 主キー |
| idx_instructor_name | name | 名前での検索用 |
| idx_instructor_name_kana | name_kana | カナ名前での検索用 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| - | - | - |

[🔝 ページトップへ](#データベース構造定義)

### syllabus_master シラバスマスタ

#### テーブル概要
シラバスコードと年度の組み合わせを管理するマスターテーブル。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|----------|----------|------|------|--------|
| syllabus_id | INTEGER | NO | シラバスID（主キー） | システム生成 |
| syllabus_code | TEXT | NO | シラバス管理番号 | Web Syllabus |
| syllabus_year | INTEGER | NO | シラバス年 | Web Syllabus |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |
| updated_at | TIMESTAMP | YES | 更新日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | syllabus_id | 主キー |
| UNIQUE | (syllabus_code, syllabus_year) | シラバスコードと年度の一意性 |
| idx_syllabus_master_code | syllabus_code | シラバスコードでの検索用 |
| idx_syllabus_master_year | syllabus_year | 年度での検索用 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| - | - | - |

[🔝 ページトップへ](#データベース構造定義)

### book 書籍

#### テーブル概要
教科書・参考文献として使用される書籍の情報を管理するテーブル。著者情報はカンマ区切りの単一フィールドで管理。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|----------|----------|------|------|--------|
| book_id | INTEGER | NO | 書籍ID（主キー） | システム生成 |
| title | TEXT | NO | 書籍タイトル | Web Syllabus |
| author | TEXT | YES | 著者名（カンマ区切り） | Web Syllabus |
| publisher | TEXT | YES | 出版社名 | Web Syllabus |
| price | INTEGER | YES | 価格（税抜） | Web Syllabus |
| isbn | TEXT | YES | ISBN番号 | Web Syllabus |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | book_id | 主キー |
| UNIQUE | isbn | ISBN番号の一意性 |
| idx_book_title | title | 書籍タイトルでの検索用 |
| idx_book_isbn | isbn | ISBN番号での検索用 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| - | - | - |

#### 設計思想
##### 主キー設計
- **サロゲートキー（book_id）を採用**: 安定した主キーとしてbook_idを使用
- **ISBNはNULL可**: 将来的に他の識別子（ASIN、DOI、OCLCなど）を追加する可能性を考慮
- **ISBNの一意性**: 正規のISBN番号の重複を防ぐためUNIQUE制約を設定

##### データ分離戦略
- **bookテーブル**: 正規のISBNを持つ書籍のみを管理
- **book_uncategorizedテーブル**: ISBNなし、不正ISBN、問題のある書籍を管理
- **明確な責任分離**: データ品質に基づいてテーブルを分離し、管理を簡素化

##### 拡張性の考慮
- **段階的拡張**: 必要に応じて他の識別子フィールドを追加可能
- **複合UNIQUE制約**: 将来的に複数の識別子の組み合わせで一意性を保証可能
- **後方互換性**: 既存のISBN中心の運用を維持しつつ拡張性を確保

##### 運用上の利点
- **シンプルな参照**: book_idによる安定した外部キー参照
- **ISBN検索の効率性**: ISBNでの高速検索が可能
- **データ品質の保証**: 正規データと問題データの明確な分離

[🔝 ページトップへ](#データベース構造定義)

### book_uncategorized 未分類書籍

#### テーブル概要
正規のbookテーブルに分類できない書籍情報（ISBNなし、不正ISBN、タイトル不一致、データ不足など）を管理するテーブル。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|----------|----------|------|------|--------|
| id | INTEGER | NO | 主キー | システム生成 |
| syllabus_id | INTEGER | NO | シラバスID（外部キー） | システム生成 |
| title | TEXT | NO | 書籍タイトル | Web Syllabus |
| author | TEXT | YES | 著者名 | Web Syllabus |
| publisher | TEXT | YES | 出版社名 | Web Syllabus |
| price | INTEGER | YES | 価格（税抜） | Web Syllabus |
| role | TEXT | NO | 利用方法（教科書、参考書など） | Web Syllabus |
| isbn | TEXT | YES | ISBN番号（不正・未入力含む） | Web Syllabus |
| categorization_status | TEXT | YES | 未分類理由（ISBNなし、不正ISBN、タイトル不一致、データ不足など） | システム判定 |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |
| updated_at | TIMESTAMP | YES | 更新日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | id | 主キー |
| idx_book_uncategorized_syllabus | syllabus_id | シラバスIDでの検索用 |
| idx_book_uncategorized_title | title | 書籍タイトルでの検索用 |
| idx_book_uncategorized_isbn | isbn | ISBN番号での検索用 |
| idx_book_uncategorized_status | categorization_status | 未分類理由での検索用 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| syllabus_id | syllabus_master(syllabus_id) | CASCADE |

#### 補足
- 正規のbookテーブルに分類できない全ての書籍情報を管理
- categorization_statusで未分類理由を明示
- シラバスIDとの関連を保持し、どのシラバスで参照されているかを追跡可能

#### 設計思想
##### データ品質管理
- **問題データの集約**: ISBNなし、不正ISBN、タイトル不一致など、様々な問題データを一元管理
- **未分類理由の明示**: categorization_statusフィールドで問題の種類を明確化
- **追跡可能性**: どのシラバスで参照されているかを保持し、データの出所を追跡

##### bookテーブルとの関係
- **補完的役割**: bookテーブルで管理できないデータを補完
- **明確な境界**: 正規データと問題データの境界を明確に定義
- **段階的改善**: 将来的に問題データを正規データに移行する可能性を考慮

##### 運用上の利点
- **データ品質の可視化**: 問題データの種類と量を把握可能
- **改善の指針**: categorization_statusによる問題の分類で改善方針を決定
- **完全性の保証**: 全ての書籍情報を漏れなく管理

[🔝 ページトップへ](#データベース構造定義)

### syllabus シラバス情報

#### テーブル概要
各科目のシラバス情報を管理するテーブル。Web Syllabusから取得される科目の詳細情報、授業内容、評価方法などを格納。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|----------|----------|------|------|--------|
| syllabus_id | INTEGER | NO | シラバスID（主キー、外部キー） | システム生成 |
| subject_name_id | INTEGER | NO | 科目名ID（外部キー） | Web Syllabus |
| subtitle | TEXT | YES | 科目サブタイトル | Web Syllabus |
| term | TEXT | NO | 開講学期 | Web Syllabus |
| campus | TEXT | NO | 開講キャンパス | Web Syllabus |
| credits | INTEGER | NO | 単位数 | Web Syllabus |
| goals | TEXT | YES | 目的 | Web Syllabus |
| summary | TEXT | YES | 授業概要 | Web Syllabus |
| attainment | TEXT | YES | 到達目標 | Web Syllabus |
| methods | TEXT | YES | 授業方法 | Web Syllabus |
| outside_study | TEXT | YES | 授業外学習 | Web Syllabus |
| textbook_comment | TEXT | YES | 教科書に関するコメント | Web Syllabus |
| reference_comment | TEXT | YES | 参考文献に関するコメント | Web Syllabus |
| grading_comment | TEXT | YES | 成績評価に関するコメント | Web Syllabus |
| advice | TEXT | YES | 履修上の注意 | Web Syllabus |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |
| updated_at | TIMESTAMP | YES | 更新日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | syllabus_id | 主キー |
| idx_syllabus_term | term | 開講学期での検索用 |
| idx_syllabus_campus | campus | 開講キャンパスでの検索用 |
| idx_syllabus_subject_name | subject_name_id | 科目名IDでの検索用 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| syllabus_id | syllabus_master(syllabus_id) | CASCADE |
| subject_name_id | subject_name(subject_name_id) | CASCADE |

[🔝 ページトップへ](#データベース構造定義)

### subject_grade 科目履修可能学年

#### テーブル概要
科目の履修可能学年を管理するテーブル。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|----------|----------|------|------|--------|
| id | INTEGER | NO | 主キー | システム生成 |
| syllabus_id | INTEGER | NO | シラバスID（外部キー） | システム生成 |
| grade | TEXT | NO | 履修可能学年 | web syllabus |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |
| updated_at | TIMESTAMP | YES | 更新日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | id | 主キー |
| UNIQUE | (syllabus_id, grade) | シラバスと学年の一意性 |
| idx_subject_grade_grade | grade | 学年での検索用 |
| idx_subject_grade_syllabus | syllabus_id | シラバスIDでの検索用 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| syllabus_id | syllabus_master(syllabus_id) | CASCADE |

#### 補足
gradeの値は以下の形式で、学生の学年を表します：
- 学部生: 学部1年生, 学部2年生, 学部3年生, 学部4年生
- 修士課程: 修士1年生, 修士2年生
- 博士課程: 博士1年生, 博士2年生, 博士3年生

[🔝 ページトップへ](#データベース構造定義)

### lecture_time 講義時間

#### テーブル概要
各科目の開講時間情報を管理するテーブル。複数時限に対応。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|----------|----------|------|------|--------|
| id | INTEGER | NO | ID（主キー） | システム生成 |
| syllabus_id | INTEGER | NO | シラバスID（外部キー） | システム生成 |
| day_of_week | TEXT | NO | 曜日 or 集中 | Web Syllabus |
| period | TINYINT | NO | 時限 | Web Syllabus |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |
| updated_at | TIMESTAMP | YES | 更新日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | id | 主キー |
| UNIQUE | (syllabus_id, day_of_week, period) | シラバスと曜日・時限の一意性 |
| idx_lecture_time_day_period | (day_of_week, period) | 曜日・時限での検索用 |
| idx_lecture_time_syllabus | syllabus_id | シラバスIDでの検索用 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| syllabus_id | syllabus_master(syllabus_id) | CASCADE |

#### 補足
day_of_weekの値は集中講義ならは"集中"とし,
periodは"0"とする.

[🔝 ページトップへ](#データベース構造定義)

### lecture_session 講義回数

#### テーブル概要
各科目の講義回数ごとの情報を管理するテーブル。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|----------|----------|------|------|--------|
| lecture_session_id | INTEGER | NO | 講義回数ID（主キー） | システム生成 |
| syllabus_id | INTEGER | NO | シラバスID（外部キー） | システム生成 |
| session_number | INTEGER | NO | 回数 | Web Syllabus |
| contents | TEXT | YES | 学修内容 | Web Syllabus |
| other_info | TEXT | YES | その他情報 | Web Syllabus |
| lecture_format | TEXT | YES | 講義形式（対面、オンライン、ハイブリッド） | Web Syllabus |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |
| updated_at | TIMESTAMP | YES | 更新日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | lecture_session_id | 主キー |
| idx_lecture_session_syllabus | syllabus_id | シラバスIDでの検索用 |
| idx_lecture_session_number | session_number | 回数での検索用 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| syllabus_id | syllabus_master(syllabus_id) | CASCADE |

#### 補足
- lecture_formatフィールドには講義形式（対面、オンライン、ハイブリッド）を格納

[🔝 ページトップへ](#データベース構造定義)

### lecture_session_irregular 不定形講義回数

#### テーブル概要
不定形の講義回数情報を管理するテーブル。
講義回数のデータが激しく乱れているため、正規化せずに生データとして管理。
不定形テーブルとは
    - 回数フィールドの値が回数として解釈できないものを含む
    - 回数フィールドの値が重複を含む
ものとしている.

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|----------|----------|------|------|--------|
| lecture_session_irregular_id | INTEGER | NO | 不定形講義回数ID（主キー） | システム生成 |
| syllabus_id | INTEGER | NO | シラバスID（外部キー） | システム生成 |
| session_pattern | TEXT | NO | 回数パターン | Web Syllabus |
| contents | TEXT | YES | 学修内容 | Web Syllabus |
| other_info | TEXT | YES | その他情報 | Web Syllabus |
| instructor | TEXT | YES | 担当者名（生データ） | Web Syllabus |
| error_message | TEXT | NO | エラーメッセージ | システム生成 |
| lecture_format | TEXT | YES | 講義形式（対面、オンライン、ハイブリッド） | Web Syllabus |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |
| updated_at | TIMESTAMP | YES | 更新日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | lecture_session_irregular_id | 主キー |
| idx_lecture_session_irregular_syllabus | syllabus_id | シラバスIDでの検索用 |
| idx_lecture_session_irregular_pattern | session_pattern | 回数パターンでの検索用 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| syllabus_id | syllabus_master(syllabus_id) | CASCADE |

#### 補足
- session_patternの例：「I-1」「I-2」「12,15,34,56,78」「1-8」など
- 通常の講義回数（1-15回）とは異なる形式の回数を管理
- 授業回数とは関係ない番号（I-1、I-2など）も含む
- 講義回数のデータが激しく乱れているため、正規化せずに生データとして管理
- instructorフィールドには担当者名を生データとして格納
- error_messageフィールドにはデータ処理時のエラー情報を格納
- lecture_formatフィールドには講義形式（対面、オンライン、ハイブリッド）を格納

[🔝 ページトップへ](#データベース構造定義)

### syllabus_instructor シラバス教員関連

#### テーブル概要
シラバスと教員の関連を管理する中間テーブル。Web Syllabusから取得される教員の役割情報を格納。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|----------|----------|------|------|--------|
| id | INTEGER | NO | ID（主キー） | システム生成 |
| syllabus_id | INTEGER | NO | シラバスID（外部キー） | システム生成 |
| instructor_id | INTEGER | NO | 教員ID（外部キー） | Web Syllabus |
| role | TEXT | YES | 役割 | Web Syllabus |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |
| updated_at | TIMESTAMP | YES | 更新日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | id | 主キー |
| idx_syllabus_instructor_syllabus | syllabus_id | シラバスIDでの検索用 |
| idx_syllabus_instructor_instructor | instructor_id | 教員IDでの検索用 |
| UNIQUE | (syllabus_id, instructor_id) | シラバスと教員の一意性 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| syllabus_id | syllabus_master(syllabus_id) | CASCADE |
| instructor_id | instructor(instructor_id) | CASCADE |

#### 補足
- 一つのシラバスに対して複数の教員が存在する可能性がある
- 教員の役割（主担当、副担当など）を管理
- 年度ごとに教員情報が異なる場合に対応

[🔝 ページトップへ](#データベース構造定義)

### lecture_session_instructor 講義回数担当者

#### テーブル概要
講義回数ごとの担当者情報を管理するテーブル。Web Syllabusから取得される講義回数ごとの担当者情報を格納。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|----------|----------|------|------|--------|
| id | INTEGER | NO | ID（主キー） | システム生成 |
| lecture_session_id | INTEGER | NO | 講義回数ID（外部キー） | システム生成 |
| instructor_id | INTEGER | NO | 担当者ID（外部キー） | Web Syllabus |
| role | TEXT | YES | 役割 | Web Syllabus |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |
| updated_at | TIMESTAMP | YES | 更新日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | id | 主キー |
| idx_lecture_session_instructor_session | lecture_session_id | 講義回数IDでの検索用 |
| idx_lecture_session_instructor_instructor | instructor_id | 担当者IDでの検索用 |
| UNIQUE | (lecture_session_id, instructor_id) | 講義回数と担当者の一意性 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| lecture_session_id | lecture_session(lecture_session_id) | CASCADE |
| instructor_id | instructor(instructor_id) | CASCADE |

#### 補足
- 一つの講義回数に対して複数の担当者が存在する可能性がある
- 年度ごとに担当者情報が異なる場合に対応

[🔝 ページトップへ](#データベース構造定義)

### syllabus_book シラバス教科書関連

#### テーブル概要
シラバスと教科書の関連を管理する中間テーブル。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|----------|----------|------|------|--------|
| id | INTEGER | NO | ID | システム生成 |
| syllabus_id | INTEGER | NO | シラバスID（外部キー） | システム生成 |
| book_id | INTEGER | NO | 書籍ID | Web Syllabus |
| role | TEXT | NO | 利用方法(教科書, 参考書) | Web Syllabus |
| note | TEXT | YES | 備考 | Web Syllabus |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | id | 主キー |
| idx_syllabus_book_syllabus | syllabus_id | シラバスIDでの検索用 |
| idx_syllabus_book_book | book_id | 書籍IDでの検索用 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| syllabus_id | syllabus_master(syllabus_id) | CASCADE |
| book_id | book(book_id) | CASCADE |

[🔝 ページトップへ](#データベース構造定義)

### grading_criterion 成績評価基準

#### テーブル概要
成績評価の基準と比率を管理するテーブル。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|----------|----------|------|------|--------|
| id | INTEGER | NO | ID（主キー） | システム生成 |
| syllabus_id | INTEGER | NO | シラバスID（外部キー） | システム生成 |
| criteria_type | TEXT | NO | 評価種別 | Web Syllabus |
| criteria_description | TEXT | YES | 評価基準の詳細説明 | Web Syllabus |
| ratio | INTEGER | YES | 評価比率 | Web Syllabus |
| note | TEXT | YES | 備考 | Web Syllabus |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | id | 主キー |
| idx_grading_criterion_type | criteria_type | 評価種別での検索用 |
| idx_grading_criterion_syllabus | syllabus_id | シラバスIDでの検索用 |
| UNIQUE | (syllabus_id, criteria_type) | シラバスと評価種別の一意性 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| syllabus_id | syllabus_master(syllabus_id) | CASCADE |

[🔝 ページトップへ](#データベース構造定義)

### subject_attribute 科目属性

#### テーブル概要
科目の属性を管理するマスターテーブル。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|----------|----------|------|------|--------|
| attribute_id | INTEGER | NO | 属性ID（主キー） | システム生成 |
| attribute_name | TEXT | NO | 属性名 | 履修要綱 |
| description | TEXT | YES | 属性の説明 | 手入力 |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | attribute_id | 主キー |
| UNIQUE | attribute_name | 属性名の一意性 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| - | - | - |

#### 補足
- 属性の例：要件種別、履修条件、開講条件など

[🔝 ページトップへ](#データベース構造定義)

### subject 科目基本情報

#### テーブル概要
科目の基本情報を管理するテーブル。科目のマスターデータを格納。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|----------|----------|------|------|--------|
| subject_id | INTEGER | NO | ID（主キー） | システム生成 |
| subject_name_id | INTEGER | NO | 科目名ID（外部キー） | 履修要綱 |
| faculty_id | INTEGER | NO | 開講学部ID（外部キー） | 履修要綱 |
| curriculum_year | INTEGER | NO | 要綱年 | 履修要綱 |
| class_id | INTEGER | NO | クラスID（外部キー） | 履修要綱 |
| subclass_id | INTEGER | YES | 小区分ID（外部キー） | 履修要綱 |
| requirement_type | TEXT | NO | 必修/選択区分 | 履修要綱 |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |
| updated_at | TIMESTAMP | YES | 更新日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | subject_id | 主キー |
| idx_subject_unique | (subject_name_id, faculty_id, class_id, subclass_id, curriculum_year) | 科目情報の一意性 |
| idx_subject_subject_name | subject_name_id | 科目名IDでの検索用 |
| idx_subject_class | class_id | クラスIDでの検索用 |
| idx_subject_faculty | faculty_id | 学部IDでの検索用 |
| idx_subject_curriculum_year | curriculum_year | 要綱年での検索用 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| subject_name_id | subject_name(subject_name_id) | RESTRICT |
| faculty_id | faculty(faculty_id) | RESTRICT |
| class_id | class(class_id) | RESTRICT |
| subclass_id | subclass(subclass_id) | RESTRICT |

#### 補足
- 本来は複合キー(subject_name_id, faculty_id, curriculum_year)
だが、サロゲートキー(subject_id)を使用

[🔝 ページトップへ](#データベース構造定義)

### subject_attribute_value 科目属性値

#### テーブル概要
科目の属性値を管理するテーブル。EAVパターンを使用して科目の属性値を格納。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|----------|----------|------|------|--------|
| id | INTEGER | NO | 主キー | システム生成 |
| subject_id | INTEGER | NO | 科目ID（外部キー） | シラバス検索画面 |
| attribute_id | INTEGER | NO | 属性ID（外部キー） | システム定義 |
| value | TEXT | NO | 属性値 | シラバス検索画面 |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |
| updated_at | TIMESTAMP | YES | 更新日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | id | 主キー |
| idx_subject_attribute_value_unique | (subject_id, attribute_id, value) | 科目・属性・値の一意性 |
| idx_subject_attribute_value_subject | subject_id | 科目IDでの検索用 |
| idx_subject_attribute_value_attribute | attribute_id | 属性IDでの検索用 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| subject_id | subject(subject_id) | CASCADE |
| attribute_id | subject_attribute(attribute_id) | RESTRICT |

#### 補足
- 一つの科目に対して複数の属性値が存在する
- 年度ごとに属性値が異なる場合に対応
- 属性値は全てTEXT型で格納し、アプリケーション側で適切な型に変換
- 科目とシラバスの関連は`subject_name_id`を通じて`subject`テーブルと`syllabus`テーブルで管理

[🔝 ページトップへ](#データベース構造定義)

### syllabus_faculty シラバス学部関連

#### テーブル概要
シラバスと学部・課程の関連を管理する中間テーブル。シラバスがどの学部・課程で開講されるかを管理。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|----------|----------|------|------|--------|
| id | INTEGER | NO | ID（主キー） | システム生成 |
| syllabus_id | INTEGER | NO | シラバスID（外部キー） | システム生成 |
| faculty_id | INTEGER | NO | 学部・課程ID（外部キー） | システム生成 |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |
| updated_at | TIMESTAMP | YES | 更新日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | id | 主キー |
| idx_syllabus_faculty_syllabus | syllabus_id | シラバスIDでの検索用 |
| idx_syllabus_faculty_faculty | faculty_id | 学部・課程IDでの検索用 |
| UNIQUE | (syllabus_id, faculty_id) | シラバスと学部・課程の一意性 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| syllabus_id | syllabus_master(syllabus_id) | CASCADE |
| faculty_id | faculty(faculty_id) | CASCADE |

#### 補足
- 一つのシラバスに対して複数の学部・課程が存在する可能性がある
- 年度ごとに開講学部・課程が異なる場合に対応
- シラバスと学部・課程の多対多の関係を管理

[🔝 ページトップへ](#データベース構造定義)

### syllabus_study_system シラバス系統的履修

#### テーブル概要
シラバスの系統的履修関係を管理するテーブル。科目間の履修順序や前提条件を表現。Web Syllabusの「履修条件」から取得される情報を格納。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|----------|----------|------|------|--------|
| id | INTEGER | NO | ID（主キー） | システム生成 |
| source_syllabus_id | INTEGER | NO | 引用元シラバスID（外部キー） | Web Syllabus |
| target | TEXT | NO | 引用先科目 | Web Syllabus |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |
| updated_at | TIMESTAMP | YES | 更新日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | id | 主キー |
| idx_syllabus_study_system_source | source_syllabus_id | 引用元シラバスIDでの検索用 |
| idx_syllabus_study_system_target | target | 引用先科目での検索用 |
| UNIQUE | (source_syllabus_id, target) | 引用関係の一意性 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| source_syllabus_id | syllabus_master(syllabus_id) | CASCADE |

#### 補足
- 引用先の科目は、Web Syllabusの「履修条件」から取得した生のテキストをそのまま保存
- 科目の分解や正規化は行わない

[🔝 ページトップへ](#データベース構造定義)

## データソースと更新ポリシー

### データソースの種類

#### 1. シラバス検索画面
- シラバスの検索画面を整形したものをクロール

[目次へ戻る](#目次)

## 関連ドキュメント
- [データベース設計ポリシー]
- [データベース操作クラス](../python/database.md)
- [データモデル定義](../python/models.md)
