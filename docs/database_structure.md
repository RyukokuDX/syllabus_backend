# シラバス情報データベース設計

[readmeへ](../README.md)

## 目次

### テーブル構成
1. [subject（科目基本情報）](#subject科目基本情報)
2. [syllabus（シラバス情報）](#syllabusシラバス情報)
3. [syllabus_time（講義時間）](#syllabus_time講義時間)
4. [instructor（教員）](#instructor教員)
5. [syllabus_instructor（シラバス-教員関連）](#syllabus_instructorシラバス-教員関連)
6. [lecture_session（講義計画）](#lecture_session講義計画)
7. [book（書籍）](#book書籍)
8. [syllabus_textbook（シラバス-教科書関連）](#syllabus_textbookシラバス-教科書関連)
9. [syllabus_reference（シラバス-参考文献関連）](#syllabus_referenceシラバス-参考文献関連)
10. [grading_criterion（成績評価基準）](#grading_criterion成績評価基準)
11. [syllabus_faculty（シラバス-学部/課程関連）](#syllabus_facultyシラバス-学部課程関連)
12. [subject_requirement（科目要件・属性）](#subject_requirement科目要件属性)
13. [subject_program（科目-学習プログラム関連）](#subject_program科目-学習プログラム関連)

### [データソースと更新ポリシー](#データソースと更新ポリシー)

## テーブル構成

### subject（科目基本情報）

#### テーブル概要
科目の基本情報を管理するテーブル。シラバス検索画面から取得される科目のマスターデータを格納。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|---------|---------|------|------|--------|
| subject_code | TEXT | NO | シラバス管理番号 | シラバス検索画面 |
| name | TEXT | NO | 科目名 | シラバス検索画面 |
| class_name | TEXT | NO | 科目区分 | シラバス検索画面 |
| subclass_name | TEXT | YES | 科目小区分 | シラバス検索画面 |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |
| updated_at | TIMESTAMP | YES | 更新日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | subject_code | 主キー |
| idx_subject_name | name | 科目名での検索用 |
| idx_subject_class | class_name | クラス名での検索用 |

[目次へ戻る](#目次)

### syllabus（シラバス情報）

#### テーブル概要
各科目のシラバス情報を管理するテーブル。Web Syllabusから取得される科目の詳細情報、授業内容、評価方法などを格納。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|---------|---------|------|------|--------|
| subject_code | TEXT | NO | シラバス管理番号 | Web Syllabus |
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
| campus | VARCHAR(6) | NO | 開講キャンパス | Web Syllabus |
| credits | TINYINT | NO | 単位数 | Web Syllabus |
| lecture_code | TEXT | NO | 開講コード | Web Syllabus |
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
| PRIMARY KEY | subject_code | 主キー |
| idx_syllabus_year | year | 開講年度での検索用 |
| idx_syllabus_term | term | 開講学期での検索用 |
| idx_syllabus_grades | (grade_b1, grade_b2, grade_b3, grade_b4, grade_m1, grade_m2, grade_d1, grade_d2, grade_d3) | 学年での複合検索用 |
| idx_syllabus_campus | campus | 開講キャンパスでの検索用 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| subject_code | subject(subject_code) | CASCADE |

[目次へ戻る](#目次)

### syllabus_time（講義時間）

#### テーブル概要
各科目の開講時間情報を管理するテーブル。複数時限に対応。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|---------|---------|------|------|--------|
| id | INTEGER | NO | ID | システム生成 |
| subject_code | TEXT | NO | シラバス管理番号 | Web Syllabus |
| day_of_week | TEXT | NO | 曜日 | Web Syllabus |
| period | TEXT | NO | 時限 | Web Syllabus |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | id | 主キー |
| idx_syllabus_time_day_period | (day_of_week, period) | 曜日・時限での検索用 |
| idx_syllabus_time_subject | subject_code | シラバス管理番号での検索用 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| subject_code | subject(subject_code) | CASCADE |

[目次へ戻る](#目次)

### instructor（教員）

#### テーブル概要
教員の基本情報を管理するテーブル。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|---------|---------|------|------|--------|
| instructor_code | TEXT | NO | 教職員番号 | Web Syllabus |
| name | TEXT | NO | 氏名 | Web Syllabus |
| name_kana | TEXT | YES | 氏名（カナ） | Web Syllabus |
| name_en | TEXT | YES | 氏名（英語） | Web Syllabus |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |
| updated_at | TIMESTAMP | YES | 更新日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | instructor_code | 主キー |
| idx_instructor_name | name | 氏名での検索用 |
| idx_instructor_name_kana | name_kana | カナ氏名での検索用 |

[目次へ戻る](#目次)

### syllabus_instructor（シラバス-教員関連）

#### テーブル概要
シラバスと教員の関連を管理する中間テーブル。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|---------|---------|------|------|--------|
| id | INTEGER | NO | ID | システム生成 |
| subject_code | TEXT | NO | シラバス管理番号 | Web Syllabus |
| instructor_code | TEXT | NO | 教職員番号 | Web Syllabus |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | id | 主キー |
| idx_syllabus_instructor_subject | subject_code | シラバス管理番号での検索用 |
| idx_syllabus_instructor_instructor | instructor_code | 教職員番号での検索用 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| subject_code | subject(subject_code) | CASCADE |
| instructor_code | instructor(instructor_code) | CASCADE |

[目次へ戻る](#目次)

### lecture_session（講義計画）

#### テーブル概要
各回の講義内容を管理するテーブル。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|---------|---------|------|------|--------|
| id | INTEGER | NO | ID | システム生成 |
| subject_code | TEXT | NO | シラバス管理番号 | Web Syllabus |
| session_number | INTEGER | NO | 回数 | Web Syllabus |
| description | TEXT | NO | 内容 | Web Syllabus |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | id | 主キー |
| idx_lecture_session_subject_num | (subject_code, session_number) | シラバス管理番号・回数での検索用 |
| idx_lecture_session_instructor | instructor_code | 担当教員での検索用 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| subject_code | subject(subject_code) | CASCADE |
| instructor_code | instructor(instructor_code) | SET NULL |

[目次へ戻る](#目次)

### book（書籍）

#### テーブル概要
教科書・参考文献として使用される書籍の情報を管理するテーブル。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|---------|---------|------|------|--------|
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

[目次へ戻る](#目次)

### syllabus_textbook（シラバス-教科書関連）

#### テーブル概要
シラバスと教科書の関連を管理する中間テーブル。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|---------|---------|------|------|--------|
| id | INTEGER | NO | ID | システム生成 |
| subject_code | TEXT | NO | シラバス管理番号 | Web Syllabus |
| book_id | INTEGER | NO | 書籍ID | Web Syllabus |
| note | TEXT | YES | 備考 | Web Syllabus |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | id | 主キー |
| idx_syllabus_textbook_subject | subject_code | シラバス管理番号での検索用 |
| idx_syllabus_textbook_book | book_id | 書籍IDでの検索用 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| subject_code | subject(subject_code) | CASCADE |
| book_id | book(id) | CASCADE |

[目次へ戻る](#目次)

### syllabus_reference（シラバス-参考文献関連）

#### テーブル概要
シラバスと参考文献の関連を管理する中間テーブル。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|---------|---------|------|------|--------|
| id | INTEGER | NO | ID | システム生成 |
| subject_code | TEXT | NO | シラバス管理番号 | Web Syllabus |
| book_id | INTEGER | NO | 書籍ID | Web Syllabus |
| note | TEXT | YES | 備考 | Web Syllabus |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | id | 主キー |
| idx_syllabus_reference_subject | subject_code | シラバス管理番号での検索用 |
| idx_syllabus_reference_book | book_id | 書籍IDでの検索用 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| subject_code | subject(subject_code) | CASCADE |
| book_id | book(id) | CASCADE |

[目次へ戻る](#目次)

### grading_criterion（成績評価基準）

#### テーブル概要
成績評価の基準と比率を管理するテーブル。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|---------|---------|------|------|--------|
| id | INTEGER | NO | ID | システム生成 |
| subject_code | TEXT | NO | シラバス管理番号 | Web Syllabus |
| criteria_type | VARCHAR(4) | NO | 評価種別（'平常'：平常点、'小テ'：小テスト、'定期'：定期試験、'レポ'：レポート、'他'：その他、'自由'：自由記載） | Web Syllabus |
| ratio | TINYINT | YES | 評価比率（%） ※自由記載の場合はNULL | Web Syllabus |
| note | TEXT | YES | 備考 | Web Syllabus |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |

#### 制約
- criteria_typeは以下のいずれかの値のみ許可：
  - '平常'：平常点
  - '小テ'：小テスト
  - '定期'：定期試験
  - 'レポ'：レポート
  - '他'：その他
  - '自由'：自由記載（この場合、ratioはNULLとなり、noteのみ使用）

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | id | 主キー |
| idx_grading_criterion_type | criteria_type | 評価種別での検索用 |
| idx_grading_criterion_subject_type | (subject_code, criteria_type) | シラバス管理番号・評価種別での検索用 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| subject_code | subject(subject_code) | CASCADE |

[目次へ戻る](#目次)

### syllabus_faculty（シラバス-学部/課程関連）

#### テーブル概要
シラバスと開講学部/課程の関連を管理する中間テーブル。1つの科目が複数の学部/課程で開講される場合に対応。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|---------|---------|------|------|--------|
| id | INTEGER | NO | ID | システム生成 |
| subject_code | TEXT | NO | シラバス管理番号 | Web Syllabus |
| faculty | VARCHAR(60) | NO | 開講学部/課程 | Web Syllabus |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | id | 主キー |
| idx_syllabus_faculty_subject | subject_code | シラバス管理番号での検索用 |
| idx_syllabus_faculty_faculty | faculty | 学部/課程での検索用 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| subject_code | subject(subject_code) | CASCADE |

[目次へ戻る](#目次)

### subject_requirement（科目要件・属性）

#### テーブル概要
履修要綱から取得される科目ごとの履修要件、制限事項、および属性を管理するテーブル。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|---------|---------|------|------|--------|
| subject_code | TEXT | NO | シラバス管理番号 | 履修要綱 |
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
| idx_requirement_type | requirement_type | 必要度での検索用 |
| idx_requirement_restrictions | (applied_science_available, graduation_credit_limit, year_restriction) | 制限条件での検索用 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| subject_code | subject(subject_code) | CASCADE |

[目次へ戻る](#目次)

### subject_program（科目-学習プログラム関連）

#### テーブル概要
科目と学習プログラムの関連を管理する中間テーブル。1つの科目が複数の学習プログラムに属する場合に対応。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|---------|---------|------|------|--------|
| id | INTEGER | NO | ID | システム生成 |
| subject_code | TEXT | NO | シラバス管理番号 | 履修要綱 |
| program_code | TEXT | NO | 学習プログラムコード | 履修要綱 |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | id | 主キー |
| idx_subject_program_subject | subject_code | シラバス管理番号での検索用 |
| idx_subject_program_program | program_code | プログラムコードでの検索用 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| subject_code | subject(subject_code) | CASCADE |

[目次へ戻る](#目次)

## データソースと更新ポリシー

### データソースの種類

#### 1. シラバス検索画面
- シラバスの検索画面を整形したものをクロール

#### 2. webシラバス
- シラバス管理コードから生成したurlのページを解析

#### 3. メディアセンターcsv
-　メディアセンターからコモンズが取得しているcsv

[目次へ戻る](#目次)