# データベース構造定義

[readmeへ](../../README.md) | [設計ポリシーへ](policy.md) | [ER図へ](er.md)

## 目次

### テーブル構成
1. [class 科目区分](#class-科目区分)
2. [subclass 科目小区分](#subclass-科目小区分)
3. [class_note 科目区分の備考](#class_note-科目区分の備考)
4. [faculty 開講学部・課程](#faculty-開講学部課程)
5. [subject_name 科目名マスタ](#subject_name-科目名マスタ)
6. [syllabus シラバス情報](#syllabus-シラバス情報)
7. [syllabus_eligible_grade シラバス履修可能学年](#syllabus_eligible_grade-シラバス履修可能学年)
8. [syllabus_faculty_enrollment シラバス学部課程入学年度制限](#syllabus_faculty_enrollment-シラバス学部課程入学年度制限)
9. [subject 科目基本情報](#subject-科目基本情報)
10. [instructor 教員](#instructor-教員)
11. [book 書籍](#book-書籍)
12. [book_author 書籍著者](#book_author-書籍著者)
13. [lecture_session 講義時間](#lecture_session-講義時間)
14. [syllabus_instructor シラバス教員関連](#syllabus_instructor-シラバス教員関連)
15. [syllabus_book シラバス教科書関連](#syllabus_book-シラバス教科書関連)
16. [grading_criterion 成績評価基準](#grading_criterion-成績評価基準)
17. [requirement_header 科目要件ヘッダー](#requirement_header-科目要件ヘッダー)
18. [requirement_attribute 科目要件属性](#requirement_attribute-科目要件属性)
19. [requirement 科目要件値](#requirement-科目要件値)

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

## テーブル構成

### class 科目区分

#### テーブル概要
科目の大区分を管理するテーブル。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|----------|----------|------|------|--------|
| class_id | INTEGER | NO | クラスID（主キー） | システム生成 |
| class_name | TEXT | NO | クラス名 | シラバス検索画面 |

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
| subclass_name | TEXT | NO | 小区分名 | シラバス検索画面 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | subclass_id | 主キー |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| - | - | - |

[目次へ戻る](#目次)

### class_note 科目区分の備考

#### テーブル概要
科目区分の備考を管理するテーブル。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|----------|----------|------|------|--------|
| class_note_id | INTEGER | NO | 備考ID（主キー） | システム生成 |
| class_note | TEXT | NO | 備考内容 | シラバス検索画面 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | class_note_id | 主キー |

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
| name | TEXT | NO | 科目名 | web syllabus |

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

### syllabus シラバス情報

#### テーブル概要
各科目のシラバス情報を管理するテーブル。Web Syllabusから取得される科目の詳細情報、授業内容、評価方法などを格納。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|----------|----------|------|------|--------|
| syllabus_code | TEXT | NO | シラバス管理番号（主キー） | Web Syllabus |
| subject_name_id | INTEGER | NO | 科目名ID（外部キー） | Web Syllabus |
| subtitle | TEXT | YES | 科目サブタイトル | Web Syllabus |
| term | TEXT | NO | 開講学期 | Web Syllabus |
| campus | TEXT | NO | 開講キャンパス | Web Syllabus |
| credits | INTEGER | NO | 単位数 | Web Syllabus |
| summary | TEXT | YES | 授業概要 | Web Syllabus |
| goals | TEXT | YES | 到達目標 | Web Syllabus |
| methods | TEXT | YES | 授業方法 | Web Syllabus |
| outside_study | TEXT | YES | 授業外学習 | Web Syllabus |
| notes | TEXT | YES | 履修上の注意 | Web Syllabus |
| remarks | TEXT | YES | その他備考 | Web Syllabus |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |
| updated_at | TIMESTAMP | YES | 更新日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | syllabus_code | 主キー |
| idx_syllabus_term | term | 開講学期での検索用 |
| idx_syllabus_campus | campus | 開講キャンパスでの検索用 |
| idx_syllabus_subject_name | subject_name_id | 科目名IDでの検索用 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| subject_name_id | subject_name(subject_name_id) | CASCADE |

[目次へ戻る](#目次)

### syllabus_eligible_grade シラバス履修可能学年

#### テーブル概要
シラバスの履修可能学年を管理するテーブル。1つのシラバスが複数の学年で履修可能な場合に対応。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|----------|----------|------|------|--------|
| id | INTEGER | NO | 主キー | システム生成 |
| syllabus_code | TEXT | NO | シラバス管理番号（外部キー） | Web Syllabus |
| syllabus_year | INTEGER | NO | シラバス年度 | Web Syllabus |
| grade | TEXT | NO | 履修可能学年 | Web Syllabus |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |
| updated_at | TIMESTAMP | YES | 更新日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | id | 主キー |
| uix_syllabus_eligible_grade | syllabus_code, syllabus_year, grade | 一意制約 |
| idx_syllabus_eligible_grade_syllabus | syllabus_code | シラバスコードでの検索用 |
| idx_syllabus_eligible_grade_grade | grade | 学年での検索用 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| syllabus_code | syllabus(syllabus_code) | CASCADE |

#### 補足
gradeの値は以下の形式で、学生の学年を表します：
- 学部生: 学部1年生, 学部2年生, 学部3年生, 学部4年生
- 修士課程: 修士1年生, 修士2年生
- 博士課程: 博士1年生, 博士2年生, 博士3年生

[目次へ戻る](#目次)

### syllabus_faculty_enrollment シラバス学部課程入学年度制限

#### テーブル概要
シラバスの入学年度制限と学部課程関連情報を管理するテーブル。Web Syllabusから取得される入学年度制限情報と学部課程情報を格納。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|----------|----------|------|------|--------|
| id | INTEGER | NO | 主キー | システム生成 |
| syllabus_code | TEXT | NO | シラバス管理番号（外部キー） | Web Syllabus |
| syllabus_year | INTEGER | NO | シラバス年度 | Web Syllabus |
| faculty_id | INTEGER | NO | 学部ID（外部キー） | Web Syllabus |
| enrollment_year | INTEGER | YES | 入学年度 | Web Syllabus |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | id | 主キー |
| idx_syllabus_faculty_enrollment_syllabus | syllabus_code | シラバスコードでの検索用 |
| idx_syllabus_faculty_enrollment_faculty | faculty_id | 学部IDでの検索用 |
| idx_syllabus_faculty_enrollment_syllabus_year | syllabus_year | シラバス年度での検索用 |
| idx_syllabus_faculty_enrollment_unique | (syllabus_code, enrollment_year, syllabus_year, faculty_id) | 一意制約 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| syllabus_code | syllabus(syllabus_code) | CASCADE |
| faculty_id | faculty(faculty_id) | CASCADE |

[目次へ戻る](#目次)

### subject 科目基本情報

#### テーブル概要
科目の基本情報を管理するテーブル。シラバス検索画面から取得される科目のマスターデータを格納。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|----------|----------|------|------|--------|
| id | INTEGER | NO | ID（主キー） | システム生成 |
| syllabus_code | TEXT | NO | シラバス管理番号（外部キー） | シラバス検索画面 |
| syllabus_year | INTEGER | NO | 開講年度 | シラバス検索画面 |
| faculty_id | INTEGER | NO | 開講学部ID（外部キー） | シラバス検索画面 |
| class_id | INTEGER | NO | クラスID（外部キー） | シラバス検索画面 |
| subclass_id | INTEGER | YES | 小区分ID（外部キー） | シラバス検索画面 |
| class_note_id | INTEGER | YES | 備考ID（外部キー） | シラバス検索画面 |
| lecture_code | TEXT | YES | 時間割コード | シラバス検索画面 |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |
| updated_at | TIMESTAMP | YES | 更新日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | id | 主キー |
| idx_subject_unique | (syllabus_code, syllabus_year, faculty_id, class_id, subclass_id, class_note_id) | 科目情報の一意性 |
| idx_subject_syllabus | syllabus_code | シラバス管理番号での検索用 |
| idx_subject_class | class_id | クラスIDでの検索用 |
| idx_subject_faculty | faculty_id | 学部IDでの検索用 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| syllabus_code | syllabus(syllabus_code) | RESTRICT |
| faculty_id | faculty(faculty_id) | RESTRICT |
| class_id | class(class_id) | RESTRICT |
| subclass_id | subclass(subclass_id) | RESTRICT |
| class_note_id | class_note(class_note_id) | RESTRICT |

**** 補足
- 本来は複合キー(syllabus_code, syllabus_year, faculty_id, class_note)
だが, class_noteにNULLがあるため、サロゲートキー(id)を使用

[目次へ戻る](#目次)

### instructor 教員

#### テーブル概要
教員の基本情報を管理するテーブル。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|----------|----------|------|------|--------|
| instructor_code | TEXT | NO | 独自教職員番号 | システム生成 |
| last_name | TEXT | NO | 苗字 | Web Syllabus |
| first_name | TEXT | NO | 名前 | Web Syllabus |
| last_name_kana | TEXT | YES | 苗字（カナ） | Web Syllabus |
| first_name_kana | TEXT | YES | 名前（カナ） | Web Syllabus |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |
| updated_at | TIMESTAMP | YES | 更新日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | instructor_code | 主キー |
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
| title | TEXT | NO | 書籍タイトル | Web Syllabus |
| publisher | TEXT | YES | 出版社名 | Web Syllabus |
| price | INTEGER | YES | 価格（税抜） | Web Syllabus |
| isbn | TEXT | YES | ISBN番号 | Web Syllabus |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |
| updated_at | TIMESTAMP | YES | 更新日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | book_id | 主キー |
| UNIQUE | isbn | ISBN番号の一意性 |
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

### lecture_session 講義時間

#### テーブル概要
各科目の開講時間情報を管理するテーブル。複数時限に対応。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|----------|----------|------|------|--------|
| id | INTEGER | NO | ID（主キー） | システム生成 |
| syllabus_code | TEXT | NO | シラバス管理番号（外部キー） | Web Syllabus |
| syllabus_year | INTEGER | NO | 開講年度 | Web Syllabus |
| day_of_week | TEXT | NO | 曜日 or 集中 | Web Syllabus |
| period | TINYINT | NO | 時限 | Web Syllabus |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |
| updated_at | TIMESTAMP | YES | 更新日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | id | 主キー |
| idx_lecture_session_day_period | (day_of_week, period) | 曜日・時限での検索用 |
| idx_lecture_session_syllabus | (syllabus_code, syllabus_year) | シラバス管理番号と年度での検索用 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| syllabus_code | syllabus(syllabus_code) | CASCADE |

#### 補足
day_of_weekの値は集中講義ならは"集中"とし,
periodは"0"とする.

[目次へ戻る](#目次)

### syllabus_instructor シラバス教員関連

#### テーブル概要
シラバスと教員の関連を管理する中間テーブル。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|----------|----------|------|------|--------|
| id | INTEGER | NO | ID | システム生成 |
| syllabus_code | TEXT | NO | シラバス管理番号 | Web Syllabus |
| instructor_code | TEXT | NO | 教職員番号 | Web Syllabus |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | id | 主キー |
| idx_syllabus_instructor_subject | syllabus_code | シラバス管理番号での検索用 |
| idx_syllabus_instructor_instructor | instructor_code | 教職員番号での検索用 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| syllabus_code | syllabus(syllabus_code) | CASCADE |
| instructor_code | instructor(instructor_code) | CASCADE |

[目次へ戻る](#目次)

### syllabus_book シラバス教科書関連

#### テーブル概要
シラバスと教科書の関連を管理する中間テーブル。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|----------|----------|------|------|--------|
| id | INTEGER | NO | ID | システム生成 |
| syllabus_code | TEXT | NO | シラバス管理番号 | Web Syllabus |
| book_id | INTEGER | NO | 書籍ID | Web Syllabus |
| role | TINYINT | NO | 利用方法(1: 教科書, 2:参考書) | Web Syllabus |
| note | TEXT | YES | 備考 | Web Syllabus |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | id | 主キー |
| idx_syllabus_book_syllabus | syllabus_code | シラバス管理番号での検索用 |
| idx_syllabus_book_book | book_id | 書籍IDでの検索用 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| syllabus_code | syllabus(syllabus_code) | CASCADE |
| book_id | book(book_id) | CASCADE |

[目次へ戻る](#目次)

### grading_criterion 成績評価基準

#### テーブル概要
成績評価の基準と比率を管理するテーブル。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|----------|----------|------|------|--------|
| id | INTEGER | NO | ID（主キー） | システム生成 |
| syllabus_code | TEXT | NO | シラバス管理番号（外部キー） | Web Syllabus |
| criteria_type | TEXT | NO | 評価種別 | Web Syllabus |
| ratio | INTEGER | YES | 評価比率 | Web Syllabus |
| note | TEXT | YES | 備考 | Web Syllabus |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | id | 主キー |
| idx_grading_criterion_type | criteria_type | 評価種別での検索用 |
| idx_grading_criterion_syllabus | syllabus_code | シラバス管理番号での検索用 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| syllabus_code | syllabus(syllabus_code) | CASCADE |

[目次へ戻る](#目次)

### requirement_header 科目要件ヘッダー

#### テーブル概要
科目要件の基本情報を管理するテーブル。年度、学部、科目の組み合わせごとに1レコードが作成される。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|----------|----------|------|------|--------|
| requirement_header_id | INTEGER | NO | 要件ヘッダーID（主キー） | システム生成 |
| requirement_year | INTEGER | NO | 要項年 | 履修要綱 |
| faculty_id | INTEGER | NO | 要項学部・課程 | 履修要綱 |
| subject_name_id | INTEGER | NO | 科目名ID | 履修要綱 |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |
| updated_at | TIMESTAMP | YES | 更新日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | requirement_header_id | 主キー |
| UNIQUE | (requirement_year, faculty_id, subject_name_id) | 年度・学部・科目の一意性 |
| idx_requirement_header_faculty | faculty_id | 学部IDでの検索用 |
| idx_requirement_header_subject | subject_name_id | 科目名IDでの検索用 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| faculty_id | faculty(faculty_id) | RESTRICT |
| subject_name_id | subject_name(subject_name_id) | RESTRICT |

[目次へ戻る](#目次)

### requirement_attribute 科目要件属性

#### テーブル概要
科目要件の属性名を管理するマスターテーブル。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|----------|----------|------|------|--------|
| requirement_attribute_id | INTEGER | NO | 属性ID（主キー） | システム生成 |
| name | TEXT | NO | 属性名 | システム定義 |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | requirement_attribute_id | 主キー |
| UNIQUE | name | 属性名の一意性 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| - | - | - |

[目次へ戻る](#目次)

### requirement 科目要件値

#### テーブル概要
科目要件の属性値を管理するテーブル。EAVパターンを使用して、柔軟な属性値の管理を実現。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|----------|----------|------|------|--------|
| requirement_id | INTEGER | NO | ID（主キー） | システム生成 |
| requirement_header_id | INTEGER | NO | 要件ヘッダーID（外部キー） | 履修要綱 |
| requirement_attribute_id | INTEGER | NO | 属性ID（外部キー） | 履修要綱 |
| text | TEXT | NO | 属性値 | 履修要綱 |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |
| updated_at | TIMESTAMP | YES | 更新日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | requirement_id | 主キー |
| idx_requirement_header | requirement_header_id | 要件ヘッダーIDでの検索用 |
| idx_requirement_attribute | requirement_attribute_id | 属性IDでの検索用 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| requirement_header_id | requirement_header(requirement_header_id) | CASCADE |
| requirement_attribute_id | requirement_attribute(requirement_attribute_id) | RESTRICT |

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
