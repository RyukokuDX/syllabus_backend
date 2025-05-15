# シラバス情報データベース設計

[readmeへ](../README.md)

## テーブル構成

### subject（科目基本情報）

#### テーブル概要
科目の基本情報を管理するテーブル。シラバス検索画面から取得される科目のマスターデータを格納。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|---------|---------|------|------|--------|
| subject_code | TEXT | NO | 科目コード | シラバス検索画面 |
| name | TEXT | NO | 科目名 | シラバス検索画面 |
| class_name | TEXT | YES | 科目区分 | シラバス検索画面 |
| subclass_name | TEXT | YES | 科目小区分 | シラバス検索画面 |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |
| updated_at | TIMESTAMP | YES | 更新日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | subject_code | 主キー |
| idx_subject_name | name | 科目名での検索用 |
| idx_subject_class | class_name | クラス名での検索用 |

### syllabus（シラバス情報）

#### テーブル概要
各科目のシラバス情報を管理するテーブル。Web Syllabusから取得される科目の詳細情報、授業内容、評価方法などを格納。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|---------|---------|------|------|--------|
| subject_code | TEXT | NO | 科目コード | Web Syllabus |
| year | INTEGER | NO | 開講年度 | Web Syllabus |
| subtitle | TEXT | YES | 科目サブタイトル | Web Syllabus |
| faculty | TEXT | NO | 開講学部/課程 | Web Syllabus |
| term | TEXT | NO | 開講学期 | Web Syllabus |
| grade_years | TEXT | NO | 対象学年 | Web Syllabus |
| campus | TEXT | NO | 開講キャンパス | Web Syllabus |
| credits | INTEGER | NO | 単位数 | Web Syllabus |
| lecture_code | TEXT | NO | 開講コード | Web Syllabus |
| summary | TEXT | YES | 授業概要 | Web Syllabus |
| goals | TEXT | YES | 到達目標 | Web Syllabus |
| methods | TEXT | YES | 授業方法 | Web Syllabus |
| outside_study | TEXT | YES | 授業外学習 | Web Syllabus |
| prerequisites | TEXT | YES | 履修条件 | Web Syllabus |
| notes | TEXT | YES | 履修上の注意 | Web Syllabus |
| remarks | TEXT | YES | その他備考 | Web Syllabus |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |
| updated_at | TIMESTAMP | YES | 更新日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | subject_code | 主キー |
| idx_syllabus_year | year | 開講年度での検索用 |
| idx_syllabus_faculty | faculty | 開講学部での検索用 |
| idx_syllabus_term | term | 開講学期での検索用 |
| idx_syllabus_grade_years | grade_years | 対象学年での検索用 |
| idx_syllabus_campus | campus | 開講キャンパスでの検索用 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| subject_code | subject(subject_code) | CASCADE |

### syllabus_time（講義時間）

#### テーブル概要
各科目の開講時間情報を管理するテーブル。複数時限に対応。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|---------|---------|------|------|--------|
| id | INTEGER | NO | ID | システム生成 |
| syllabus_id | TEXT | NO | シラバスID | Web Syllabus |
| day_of_week | TEXT | NO | 曜日 | Web Syllabus |
| period | TEXT | NO | 時限 | Web Syllabus |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | id | 主キー |
| idx_syllabus_time_day_period | (day_of_week, period) | 曜日・時限での検索用 |
| idx_syllabus_time_syllabus | syllabus_id | シラバスIDでの検索用 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| syllabus_id | syllabus(subject_code) | CASCADE |

### instructor（教員）

#### テーブル概要
教員の基本情報を管理するテーブル。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|---------|---------|------|------|--------|
| id | INTEGER | NO | 教員ID | システム生成 |
| name | TEXT | NO | 氏名 | Web Syllabus |
| name_kana | TEXT | NO | 氏名（カナ） | Web Syllabus |
| name_en | TEXT | YES | 氏名（英語） | Web Syllabus |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |
| updated_at | TIMESTAMP | YES | 更新日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | id | 主キー |
| idx_instructor_name | name | 氏名での検索用 |
| idx_instructor_name_kana | name_kana | カナ氏名での検索用 |

### syllabus_instructor（シラバス-教員関連）

#### テーブル概要
シラバスと教員の関連を管理する中間テーブル。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|---------|---------|------|------|--------|
| id | INTEGER | NO | ID | システム生成 |
| syllabus_id | TEXT | NO | シラバスID | Web Syllabus |
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
| syllabus_id | syllabus(subject_code) | CASCADE |
| instructor_id | instructor(id) | CASCADE |

### lecture_session（講義計画）

#### テーブル概要
各回の講義内容を管理するテーブル。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|---------|---------|------|------|--------|
| id | INTEGER | NO | ID | システム生成 |
| syllabus_id | TEXT | NO | シラバスID | Web Syllabus |
| session_number | INTEGER | NO | 回数 | Web Syllabus |
| instructor_id | INTEGER | YES | 担当教員ID | Web Syllabus |
| description | TEXT | NO | 内容 | Web Syllabus |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | id | 主キー |
| idx_lecture_session_syllabus_num | (syllabus_id, session_number) | シラバスID・回数での検索用 |
| idx_lecture_session_instructor | instructor_id | 担当教員での検索用 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| syllabus_id | syllabus(subject_code) | CASCADE |
| instructor_id | instructor(id) | SET NULL |

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

### syllabus_textbook（シラバス-教科書関連）

#### テーブル概要
シラバスと教科書の関連を管理する中間テーブル。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|---------|---------|------|------|--------|
| id | INTEGER | NO | ID | システム生成 |
| syllabus_id | TEXT | NO | シラバスID | Web Syllabus |
| book_id | INTEGER | NO | 書籍ID | Web Syllabus |
| note | TEXT | YES | 備考 | Web Syllabus |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | id | 主キー |
| idx_syllabus_textbook_syllabus | syllabus_id | シラバスIDでの検索用 |
| idx_syllabus_textbook_book | book_id | 書籍IDでの検索用 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| syllabus_id | syllabus(subject_code) | CASCADE |
| book_id | book(id) | CASCADE |

### syllabus_reference（シラバス-参考文献関連）

#### テーブル概要
シラバスと参考文献の関連を管理する中間テーブル。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|---------|---------|------|------|--------|
| id | INTEGER | NO | ID | システム生成 |
| syllabus_id | TEXT | NO | シラバスID | Web Syllabus |
| book_id | INTEGER | NO | 書籍ID | Web Syllabus |
| note | TEXT | YES | 備考 | Web Syllabus |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | id | 主キー |
| idx_syllabus_reference_syllabus | syllabus_id | シラバスIDでの検索用 |
| idx_syllabus_reference_book | book_id | 書籍IDでの検索用 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| syllabus_id | syllabus(subject_code) | CASCADE |
| book_id | book(id) | CASCADE |

### grading_criterion（成績評価基準）

#### テーブル概要
成績評価の基準と比率を管理するテーブル。

#### カラム定義
| カラム名 | データ型 | NULL | 説明 | 情報源 |
|---------|---------|------|------|--------|
| id | INTEGER | NO | ID | システム生成 |
| syllabus_id | TEXT | NO | シラバスID | Web Syllabus |
| criteria_type | TEXT | NO | 評価種別 | Web Syllabus |
| ratio | INTEGER | NO | 評価比率（%） | Web Syllabus |
| note | TEXT | YES | 備考 | Web Syllabus |
| created_at | TIMESTAMP | NO | 作成日時 | システム生成 |

#### インデックス
| インデックス名 | カラム | 説明 |
|---------------|--------|------|
| PRIMARY KEY | id | 主キー |
| idx_grading_criterion_type | criteria_type | 評価種別での検索用 |
| idx_grading_criterion_syllabus_type | (syllabus_id, criteria_type) | シラバスID・評価種別での検索用 |

#### 外部キー制約
| 参照元 | 参照先 | 削除時の動作 |
|--------|--------|-------------|
| syllabus_id | syllabus(subject_code) | CASCADE |

## データソースと更新ポリシー

### データソースの種類

#### 1. シラバス検索画面
- シラバスの検索画面を整形したものをクロール

#### 2. webシラバス
- シラバス管理コードから生成したurlのページを解析

#### 3. メディアセンターcsv
-　メディアセンターからコモンズが取得しているcsv

[ページトップへ](#シラバス情報データベース設計)