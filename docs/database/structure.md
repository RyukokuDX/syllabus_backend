# データベース構造定義

[readmeへ](../../README.md) | [設計ポリシーへ](policy.md) | [ER図へ](er.md)

## 目次

### テーブル構成
1. [class 科目区分](#class-科目区分)
2. [subclass 科目小区分](#subclass-科目小区分)
3. [faculty 開講学部・課程](#faculty-開講学部課程)
4. [subject_name 科目名マスタ](#subject_name-科目名マスタ)
5. [instructor 教員](#instructor-教員)
6. [book 書籍](#book-書籍)
7. [book_author 書籍著者](#book_author-書籍著者)
8. [syllabus_master シラバスマスタ](#syllabus_master-シラバスマスタ)
9. [syllabus シラバス情報](#syllabus-シラバス情報)
10. [subject_grade 科目履修可能学年](#subject_grade-科目履修可能学年)
11. [lecture_time 講義時間](#lecture_time-講義時間)
12. [lecture_session 講義回数](#lecture_session-講義回数)
13. [syllabus_instructor シラバス教員関連](#syllabus_instructor-シラバス教員関連)
14. [syllabus_book シラバス教科書関連](#syllabus_book-シラバス教科書関連)
15. [grading_criterion 成績評価基準](#grading_criterion-成績評価基準)
16. [subject_attribute 科目属性](#subject_attribute-科目属性)
17. [subject 科目基本情報](#subject-科目基本情報)
18. [subject_syllabus 科目シラバス関連](#subject_syllabus-科目シラバス関連)
19. [subject_attribute_value 科目属性値](#subject_attribute_value-科目属性値)
20. [syllabus_study_system シラバス系統的履修](#syllabus_study_system-シラバス系統的履修)
21. [lecture_session_instructor 講義回数担当者](#lecture_session_instructor-講義回数担当者)

## 更新履歴

| 日付 | バージョン | 更新者 | 内容 |
|------|------------|--------|------|
| 2024-05-19 | 1.0.0 | 藤原 | 初版作成 |
| 2024-05-20 | 1.1.0 | 藤原 | テーブル名・カラム名の統一（subject_code → syllabus_code） |
| 2024-05-20 | 1.1.1 | 藤原 | requirementテーブルの主キーをrequirement_codeに修正 |
| 2024-05-20 | 1.1.2 | 藤原 | インデックス名の統一、外部キー制約の整理 |
| 2024-05-21 | 1.1.3 | 藤原 | 正規化を強化。facultyテーブルをsubjectテーブルの直後に移動、目次・本文順序修正 |
| 2024-05-21 | 1.1.4 | 藤原 | requirementテーブルの主キーをrequirement_idに変更、関連テーブルの外部キー制約を修正 |
| 2024-05-21 | 1.1.5 | 藤原 | subject_requirementテーブルを削除、requirementテーブルにsyllabus_codeを追加 |
| 2024-05-21 | 1.1.6 | 藤原 | 外部キー制約の整合性を修正、インデックスを最適化 |
| 2024-05-21 | 1.1.7 | 藤原 | 不要な関連を削除、テーブル間の参照整合性を強化 |
| 2024-05-21 | 1.1.8 | 藤原 | programテーブルを追加、subject_programテーブルの外部キー制約を修正 |
| 2024-05-21 | 1.1.9 | 藤原 | subjectテーブルにサロゲートキーを追加、syllabusテーブルとの関連を整理 |
| 2024-05-21 | 1.1.10 | 藤原 | subjectテーブルの主キー名をidに変更、syllabusテーブルからyearカラムを移動 |
| 2024-05-21 | 1.1.11 | 藤原 | テーブル構成をデータソースの依存度に基づいて再構成 |
| 2024-05-21 | 1.1.12 | 藤原 | syllabusテーブルの履修可能学年フィールドをビットマスク方式に変更、パフォーマンスと拡張性を改善 |
| 2024-05-21 | 1.1.13 | 藤原 | requirementテーブルをEAVパターンに変更、programテーブルとsubject_programテーブルを削除 |
| 2024-05-29 | 1.1.14 | 藤原 | マスターテーブルのタイムスタンプカラムを整理、instructorテーブルの主キーをinstructor_idに変更 |
| 2024-05-29 | 1.1.15 | 藤原 | syllabus_bookテーブルのroleカラムをTEXT型に変更、subject_syllabusテーブルからlecture_codeを削除 |
| 2024-05-29 | 1.1.16 | 藤原 | syllabus_study_systemテーブルの説明を更新、Web Syllabusを情報源として明記 |
| 2024-05-29 | 1.1.17 | 藤原 | 講義時間管理のテーブル構造を改善、lecture_timeとlecture_sessionテーブルを追加 |

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
| idx_class_name | class_name | クラス名での検索用 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| - | - | - |

[目次へ戻る](#目次)

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

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| - | - | - |

[目次へ戻る](#目次)

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

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| - | - | - |

[目次へ戻る](#目次)

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

[目次へ戻る](#目次)

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
| UNIQUE | instructor_code | 教職員番号の一意性 |
| idx_instructor_name | (last_name, first_name) | 氏名での検索用 |
| idx_instructor_name_kana | (last_name_kana, first_name_kana) | カナ氏名での検索用 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| - | - | - |

[目次へ戻る](#目次)

### book 書籍

#### テーブル概要
教科書・参考文献として使用される書籍の情報を管理するテーブル。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|----------|----------|------|------|--------|
| book_id | INTEGER | NO | 書籍ID（主キー） | システム生成 |
| url | TEXT | NO | 書籍のURL | Web Syllabus |
| title | TEXT | NO | 書籍タイトル | Web Syllabus |
| publisher | TEXT | YES | 出版社名 | Web Syllabus |
| price | INTEGER | YES | 価格（税抜） | Web Syllabus |
| isbn | TEXT | YES | ISBN番号 | Web Syllabus |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | book_id | 主キー |
| UNIQUE | isbn | ISBN番号の一意性 |
| UNIQUE | url | URLの一意性 |
| idx_book_title | title | 書籍タイトルでの検索用 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| - | - | - |

[目次へ戻る](#目次)

### book_author 書籍著者

#### テーブル概要
書籍の著者情報を管理するテーブル。1つの書籍に複数の著者が存在する場合に対応。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|----------|----------|------|------|--------|
| book_author_id | INTEGER | NO | 著者ID（主キー） | システム生成 |
| book_id | INTEGER | NO | 書籍ID（外部キー） | Web Syllabus |
| author_name | TEXT | NO | 著者名 | Web Syllabus |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | book_author_id | 主キー |
| idx_book_author_book | book_id | 書籍IDでの検索用 |
| idx_book_author_name | author_name | 著者名での検索用 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| book_id | book(book_id) | CASCADE |

[目次へ戻る](#目次)

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

[目次へ戻る](#目次)

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

[目次へ戻る](#目次)

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
| idx_lecture_time_day_period | (day_of_week, period) | 曜日・時限での検索用 |
| idx_lecture_time_syllabus | syllabus_id | シラバスIDでの検索用 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| syllabus_id | syllabus_master(syllabus_id) | CASCADE |

#### 補足
day_of_weekの値は集中講義ならは"集中"とし,
periodは"0"とする.

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

### lecture_session_instructor 講義回数担当者

#### テーブル概要
講義回数ごとの担当者情報を管理するテーブル。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|----------|----------|------|------|--------|
| id | INTEGER | NO | ID（主キー） | システム生成 |
| lecture_session_id | INTEGER | NO | 講義回数ID（外部キー） | システム生成 |
| instructor_id | INTEGER | NO | 担当者ID（外部キー） | Web Syllabus |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | id | 主キー |
| idx_lecture_session_instructor_session | lecture_session_id | 講義回数IDでの検索用 |
| idx_lecture_session_instructor_instructor | instructor_id | 担当者IDでの検索用 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| lecture_session_id | lecture_session(lecture_session_id) | CASCADE |
| instructor_id | instructor(instructor_id) | CASCADE |

[目次へ戻る](#目次)

### syllabus_instructor シラバス教員関連

#### テーブル概要
シラバスと教員の関連を管理する中間テーブル。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|----------|----------|------|------|--------|
| id | INTEGER | NO | ID | システム生成 |
| syllabus_id | INTEGER | NO | シラバスID（外部キー） | システム生成 |
| instructor_id | INTEGER | NO | 教員ID | Web Syllabus |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | id | 主キー |
| idx_syllabus_instructor_syllabus | syllabus_id | シラバスIDでの検索用 |
| idx_syllabus_instructor_instructor | instructor_id | 教員IDでの検索用 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| syllabus_id | syllabus_master(syllabus_id) | CASCADE |
| instructor_id | instructor(instructor_id) | CASCADE |

[目次へ戻る](#目次)

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

[目次へ戻る](#目次)

### grading_criterion 成績評価基準

#### テーブル概要
成績評価の基準と比率を管理するテーブル。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|----------|----------|------|------|--------|
| id | INTEGER | NO | ID（主キー） | システム生成 |
| syllabus_id | INTEGER | NO | シラバスID（外部キー） | システム生成 |
| criteria_type | TEXT | NO | 評価種別 | Web Syllabus |
| ratio | INTEGER | YES | 評価比率 | Web Syllabus |
| note | TEXT | YES | 備考 | Web Syllabus |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | id | 主キー |
| idx_grading_criterion_type | criteria_type | 評価種別での検索用 |
| idx_grading_criterion_syllabus | syllabus_id | シラバスIDでの検索用 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| syllabus_id | syllabus_master(syllabus_id) | CASCADE |

[目次へ戻る](#目次)

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

### subject 科目基本情報

#### テーブル概要
科目の基本情報を管理するテーブル。科目のマスターデータを格納。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|----------|----------|------|------|--------|
| subject_id | INTEGER | NO | ID（主キー） | システム生成 |
| subject_name_id | INTEGER | NO | 科目名ID（外部キー） | 履修要綱 |
| faculty_id | INTEGER | NO | 開講学部ID（外部キー） | 履修要綱 |
| class_id | INTEGER | NO | クラスID（外部キー） | 履修要綱 |
| subclass_id | INTEGER | YES | 小区分ID（外部キー） | 履修要綱 |
| curriculum_year | INTEGER | NO | 要綱年 | 履修要綱 |
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

### subject_syllabus 科目シラバス関連

#### テーブル概要
科目とシラバスの関連を管理するテーブル。年度ごとのシラバス情報を管理。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|----------|----------|------|------|--------|
| id | INTEGER | NO | 主キー | システム生成 |
| subject_id | INTEGER | NO | 科目ID（外部キー） | シラバス検索画面 |
| syllabus_id | INTEGER | NO | シラバスID（外部キー） | システム生成 |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |
| updated_at | TIMESTAMP | YES | 更新日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | id | 主キー |
| idx_subject_syllabus_unique | (subject_id, syllabus_id) | 科目とシラバスの一意性 |
| idx_subject_syllabus_subject | subject_id | 科目IDでの検索用 |
| idx_subject_syllabus_syllabus | syllabus_id | シラバスIDでの検索用 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| subject_id | subject(subject_id) | CASCADE |
| syllabus_id | syllabus_master(syllabus_id) | RESTRICT |

#### 補足
- 一つの科目に対して複数のシラバスが存在する可能性がある
- 年度ごとにシラバス情報が異なる場合に対応
- シラバスコードと科目の関連を直接管理
- curriculum_year+8までは追跡しないといけない

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
| idx_subject_attribute_value_unique | (subject_id, attribute_id) | 科目・属性の一意性 |
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
- シラバスコードはsubject_syllabusテーブルで管理

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

### lecture_session_instructor 講義回数担当者

#### テーブル概要
講義回数ごとの担当者情報を管理するテーブル。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|----------|----------|------|------|--------|
| id | INTEGER | NO | ID（主キー） | システム生成 |
| lecture_session_id | INTEGER | NO | 講義回数ID（外部キー） | システム生成 |
| instructor_id | INTEGER | NO | 担当者ID（外部キー） | Web Syllabus |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | id | 主キー |
| idx_lecture_session_instructor_session | lecture_session_id | 講義回数IDでの検索用 |
| idx_lecture_session_instructor_instructor | instructor_id | 担当者IDでの検索用 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| lecture_session_id | lecture_session(lecture_session_id) | CASCADE |
| instructor_id | instructor(instructor_id) | CASCADE |

[目次へ戻る](#目次)

## データソースと更新ポリシー

### データソースの種類

#### 1. シラバス検索画面
- シラバスの検索画面を整形したものをクロール

[目次へ戻る](#目次)

## 関連ドキュメント
- [データベース設計ポリシー]
- [データベース操作クラス](../python/database.md)
- [データモデル定義](../python/models.md)
