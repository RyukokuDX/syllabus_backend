# データベース構造定義

[readmeへ](../../README.md) | [設計ポリシーへ](policy.md) | [ER図へ](er.md)

## 目次

### テーブル構成
1. [class 科目区分](#class-科目区分)
2. [subclass 科目小区分](#subclass-科目小区分)
3. [class_note 科目区分の備考](#class_note-科目区分の備考)
4. [subject_name 科目名マスタ](#subject_name-科目名マスタ)
5. [subject 科目基本情報](#subject-科目基本情報)
6. [faculty 開講学部・課程](#faculty-開講学部課程)
7. [instructor 教員](#instructor-教員)
8. [criteria 評価種別マスタ](#criteria-評価種別マスタ)
9. [book 書籍](#book-書籍)
10. [syllabus シラバス情報](#syllabus-シラバス情報)
11. [syllabus_faculty シラバス学部課程関連](#syllabus_faculty-シラバス学部課程関連)
12. [lecture_session 講義時間](#lecture_session-講義時間)
13. [syllabus_instructor シラバス教員関連](#syllabus_instructor-シラバス教員関連)
14. [syllabus_book シラバス教科書関連](#syllabus_book-シラバス教科書関連)
15. [grading_criterion 成績評価基準](#grading_criterion-成績評価基準)
16. [subject_requirement 科目要綱関連](#subject_requirement-科目要綱関連)
17. [subject_program 科目学習プログラム関連](#subject_program-科目学習プログラム関連)
18. [requirement 科目要件属性](#requirement-科目要件属性)

## 更新履歴

| 日付 | バージョン | 更新者 | 内容 |
|------|------------|--------|------|
| 2025-05-19 | 1.0.0 | 藤原 | 初版作成 |
| 2025-05-20 | 1.1.0 | 藤原 | テーブル名・カラム名の統一（subject_code → syllabus_code） |
| 2025-05-20 | 1.1.1 | 藤原 | requirementテーブルの主キーをrequirement_codeに修正 |
| 2025-05-20 | 1.1.2 | 藤原 | インデックス名の統一、外部キー制約の整理 |
| 2025-05-21 | 1.1.3 | 藤原 | 正規化を強化。facultyテーブルをsubjectテーブルの直後に移動、目次・本文順序修正 |

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

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| - | - | - |

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

### subject 科目基本情報

#### テーブル概要
科目の基本情報を管理するテーブル。シラバス検索画面から取得される科目のマスターデータを格納。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|----------|----------|------|------|--------|
| syllabus_code | TEXT | NO | シラバス管理番号 | シラバス検索画面 |
| subject_name_id | TEXT | NO | 科目名 | シラバス検索画面 |
| class_id | INTEGER | NO | クラスID（外部キー） | シラバス検索画面 |
| subclass_id | INTEGER | YES | 小区分ID（外部キー） | シラバス検索画面 |
| class_note_id | INTEGER | YES | 備考ID（外部キー） | シラバス検索画面 |
| lecture_code | TEXT | YES | 開講コード | シラバス検索画面 |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |
| updated_at | TIMESTAMP | YES | 更新日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | syllabus_code | 主キー |
| idx_subject_name | name | 科目名での検索用 |
| idx_subject_class | class_name | クラス名での検索用 |

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
| idx_instructor_name | name | 氏名での検索用 |
| idx_instructor_name_kana | name_kana | カナ氏名での検索用 |

### criteria 評価種別マスタ

#### テーブル概要
成績評価の種別を管理するマスタテーブル。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|----------|----------|------|------|--------|
| criteria_id | INTEGER | NO | 評価種別ID（主キー） | システム生成 |
| criteria_type | TEXT | NO | 評価種別（ユニーク） | シラバス検索画面 |
| description | TEXT | YES | 説明 | web syllabus |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | criteria_id | 主キー |
| UNIQUE | criteria_type | 種別の一意性 |

### book 書籍

#### テーブル概要
教科書・参考文献として使用される書籍の情報を管理するテーブル。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|----------|----------|------|------|--------|
| id | INTEGER | NO | 書籍ID | システム生成 |
| author | TEXT | YES | 著者名 | Web Syllabus |
| title | TEXT | NO | 書籍タイトル | Web Syllabus |
| publisher | TEXT | YES | 出版社名 | Web Syllabus |
| price | INTEGER | YES | 価格（税抜） | Web Syllabus |
| isbn | TEXT | YES | ISBN番号 | Web Syllabus |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |
| updated_at | TIMESTAMP | YES | 更新日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | id | 主キー |
| UNIQUE | isbn | ISBN番号の一意性 |
| idx_book_title | title | 書籍タイトルでの検索用 |
| idx_book_author | author | 著者名での検索用 |

### syllabus シラバス情報

#### テーブル概要
各科目のシラバス情報を管理するテーブル。Web Syllabusから取得される科目の詳細情報、授業内容、評価方法などを格納。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|----------|----------|------|------|--------|
| syllabus_code | TEXT | NO | シラバス管理番号 | Web Syllabus |
| subject_name_id | INTEGER | NO | 科目名ID（外部キー） | Web Syllabus |
| year | INTEGER | NO | 開講年度 | Web Syllabus |
| subtitle | TEXT | YES | 科目サブタイトル | Web Syllabus |
| term | TEXT | NO | 開講学期 | Web Syllabus |
| grade_b1 | BOOLEAN | NO | 学部1年履修可能 | Web Syllabus |
| grade_b2 | BOOLEAN | NO | 学部2年履修可能 | Web Syllabus |
| grade_b3 | BOOLEAN | NO | 学部3年履修可能 | Web Syllabus |
| grade_b4 | BOOLEAN | NO | 学部4年履修可能 | Web Syllabus |
| grade_m1 | BOOLEAN | NO | 修士1年履修可能 | Web Syllabus |
| grade_m2 | BOOLEAN | NO | 修士2年履修可能 | Web Syllabus |
| grade_d1 | BOOLEAN | NO | 博士1年履修可能 | Web Syllabus |
| grade_d2 | BOOLEAN | NO | 博士2年履修可能 | Web Syllabus |
| grade_d3 | BOOLEAN | NO | 博士3年履修可能 | Web Syllabus |
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
| idx_syllabus_year | year | 開講年度での検索用 |
| idx_syllabus_term | term | 開講学期での検索用 |
| idx_syllabus_grades | (grade_b1, grade_b2, grade_b3, grade_b4, grade_m1, grade_m2, grade_d1, grade_d2, grade_d3) | 学年での複合検索用 |
| idx_syllabus_campus | campus | 開講キャンパスでの検索用 |
| idx_syllabus_subject_name | subject_name_id | 科目名IDでの検索用 |


#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--ubject_name_id---|------_name--ubject_name_idRESTRICT
| syllabus_code | subject(syllabus_code) | CASCADE |
syllabus_faculty シラバス学部課程関連
### lecture_session（講義時間）

シラバスと学部・課程の関連要中間1つのシラバスがの学部・課程で開講される場合
各科目の開講時間情報を管理するテーブル。複数時限に対応。

#### カラム定義
| カラム名 | デ-ー-タ型 | NULL | 説明 | 情報源 |
|---------|---------|-主キー---|------|--------|
| id | INTEGER | NO | ID | システム生成 |（外部キー）シラバス検索画面
| faculty_if_we TIEGERNYINT | 学部ID（外部キー） | シラバス検索画面labus |
| period | TINYINT | NO | 時限 | Web Syllabus |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMsyllabus_faculty_syllabus | syllabus_code | シラバス管理番号
| idx_day_peri_faculty_facultyod faculty_id | 学部ID| 曜日・時限での検索用 |
| idx_lecture_session_syllabus | syllabus_code | シラバス管理番号での検索用 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| faculty_id | faculty(faculty_id) | CASCADE |
[目次へ戻る](#目次)
lecture_session 講義時間
### instructor（教員）

各科目の開講時間テーブル概要複数時限に対応。
教員の基本情報を管理するテーブル。

#### カラム定義
| カラム名 | デ-ー-タ型 | NULL | 説明 | 情報源 |
|------IN|-GER---|----ID----|
| s員番号 | シ_cod | TEXT | NO | 苗シラバス管理番号| Web Syllabus |
| day_of_weekEXT | NO |NO | 曜日llabus |
| period| TEINYIN | YNO | 時限| Web Syllabus |
| first_name_kana | TEXT | YES | 名前（カナ） | Web Syllabus |
| updated_at | TIMESTAMP | YES | 更新日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--|
| PRIMlecture_session_day_period | (day_of_week, period) | 曜日・時限 主キー |
| idx_lecture_session_syllabus | syllabus_code | シラバス管理番号
| idx_instructor_name_kana | name_kana | カナ氏名での検索用 |
#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| syllabus_code | syllabus(syllabus_code) | CASCADE |
[目次へ戻る](#目次)
 
### syllabus_instructor（シラバス-教員関連）

#### テーブル概要
シラバスと教員の関連を管理する中間テーブル。

#### カラム定義
| カラム名 | デ-ー-タ型 | NULL | 説明 | 情報源 |
|---------|---------|------|------|--------|
| id | INTEGER | NO | ID | システム生成 |
| syllabus_coid TEINXTGER NO | シラバス管理番号 | Web Syllabus |
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
| syllabus_code | subject(syllabus_code) | CASCADE |
| instructor_code | instructor(instructor_code) | CASCADE |
llabus |QUE | isb 教科書
### syllabus_book（シラバス-書籍関連）

#### テーブル概要
シラバスと教科書の関連を管理する中間テーブル。

#### カラム定義
| カラム名 | デ-ー-タ型 | NULL | 説明 | 情報源 |
|---------|---------|------|------|--------|
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
| idx_syllabus_textbook_subject | syllabus_code | シラバス管理番号での検索用 |
| idx_syllabus_textbook_book | book_id | 書籍IDでの検索用 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| syllabus_code | subject(syllabus_code) | CASCADE |
| book_id | book(id) | CASCADE |
 
### grading_criterion（成績評価基準）

#### テーブル概要
成績評価の基準と比率を管理するテーブル。

#### カラム定義
| カラム名 | デ-ー-タ型 | NULL | 説明 | 情報源 |
|---------|---------|------|------|--------|
| id | INTEGER | NO | ID | システム生成 |シラバス検索画面
| syllabus_id | INTEGER | NO | シラバスID（外部キーシラバス検索画面
| criteria_type | TEXT | NO | 評価種別：小シラバス検索画面験、'レポ'：レポート、'他'：その他、'自由'：自由記載） | Web Syllabus |
| ratio | INTEGER | YES | 評シラバス検索画面の場合はNULL | Web Syllabus |
| note | TEXT | YES | 備考 | Web Syllabus |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | id | 主キーcri riaidID
| idx_grading_criterion_type | ccrireriaria_type | 評価種別での検索用 |id
| idx_grading_criterion_subject_type | (syllabus_code, criteria_type) | シラバス管理番号・評価種別での検索用 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| criteria_id | TRAINT check_gradiid) | RESTRICT |
[目次へ戻る](#目次)
ubject_requirement 科目要綱
### syllabus_faculty（シラバス-学部/課程関連）

科目と要綱
シラバスと開講学部/課程の関連を管理する中間テーブル。1つの科目が複数の学部/課程で開講される場合に対応。

#### カラム定義
| カラム名 | デ-ー-タ型 | NULL | 説明 | 情報源 |
|---------|---------|------|------|--------|
| id | INTEGER | NO | ID | システム生成 |履修要綱
| requirement_code | TEXT| NO | シ要綱コード | 履修要綱 |
| faculty | VARCHAR(60) | NO | 開講学部/課程 | Web Syllabus |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMAubject_requirement_syllabus
| idx_subject_requirement_requirement | requirement_code | 要綱コード シラバス管理番号での検索用 |
| idx_syllabus_faculty_faculty | faculty | 学部/課程での検索用 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
|---------|---------|subject_nam(requinclri_rarde) | CASCADE|
| updated_at | TIMESTAMP | YES | 更新日時 | システム生成 |
 subjecrequimcq学習プログラム
### subject_requirement（科目-要綱関連）

###学習プログラムテーブル概要。1つの科目が複数の学習プログラムに属する場合に対応
科目と要綱の関連を管理する中間テーブル。

#### カラム定義
| カラム名 | デ-ー-タ型 | NULL | 説明 | 情報源 |
|---------|---------|------|------|--------|
| id | INTEGER | NO | ID | システム生成 |
| programde | TEXT | NO | シラバ学習プログラム理番号 | 履修要綱 |
| requirement_code | TEXT | NO | 要綱コード | 履修要綱 |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY program_subject
| idx_subject_program_program | program| シラバス管理プログラムでの検索用 |
| idx_subject_requirement_requirement | requirement_code | 要綱コードでの検索用 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|

#### requirement（科目履修ガイド）

#### テーブル概要
履修要綱から取得される科目ごとの履修要件、制限事項、属性、および学習プログラムの関連を管理するテーブル。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|---------|---------|------|------|--------|
| requirement_id | INTEGER | NO | 要綱番号 | システム生成 |
| requirement_year | INTEGER | NO | 要項年 | 履修要綱 |
| faculty_id | INTEGER | NO | 要項学部・課程 | 履修要綱 |
| subject_id | INTEGER | NO | 科目名ID | 履修要綱 |
| requirement_type | TEXT | NO | 必要度（必修/選必/選択） | 履修要綱 |
| applied_science_available | BOOLEAN | NO | 応用科学課程履修可否 | 履修要綱 |
| graduation_credit_limit | BOOLEAN | NO | 卒業要件単位認定上限の有無 | 履修要綱 |
| year_restriction | BOOLEAN | NO | 配当年次制限の有無 | 履修要綱 |
| first_year_only | BOOLEAN | NO | 低学年制限_1年目のみの有無 | 履修要綱 |
| up_to_second_year | BOOLEAN | NO | 低学年制限_2年目までの有無 | 履修要綱 |
| guidance_required | BOOLEAN | NO | 履修指導科目の有無 | 履修要綱 |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |
| updated_at | TIMESTAMP | YES | 更新日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | subject_code | 主キー |
| idx_guide_requirement | requirement_type | 必要度での検索用 |
| idx_guide_restrictions | (applied_science_available, graduation_credit_limit, year_restriction) | 制限条件での検索用 |
| idx_guide_programs | program_codes | 学習プログラムでの検索用（GINインデックス） |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| subject_code | subject(subject_code) | CASCADE |

[目次へ戻る](#目次)


### subject_program（科目-学習プログラム関連）

##の要件と属性
科目と学習プログラムの関連を管理する中間テーブル。1つの科目が複数の学習プログラムに属する場合に対応。

#### カラム定義
| カラム名 | デ-ー-タ型 | NULL | 説明 | 情報源 |
|---------|---------|------|------|--------|
| id | INTEGER | NO | ID | システム生成 |
| requirement_ID | INTEGER | NO |要綱番号 | 履修要綱 |
| program_id | INTEGER | NO | 学習プログラム番号 | 履修要綱 |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMrequirement_syllabus
| idx_requirement_requirement | requirements_code |要綱管理番号での検索用 |
| idx_subject_program_program | program_code | プログラムコードでの検索用 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| requirement_code | requirement(requirement_code) | CASCADE |
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
