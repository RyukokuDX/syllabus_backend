# シラバス情報データベース設計

## テーブル構成

### subject (科目キーと名前)
シラバス検索結果画面から抽出できる情報を纏めたもの
``` sql
CREATE TABLE subject (
    subject_code TEXT PRIMARY KEY,
    subject_name TEXT,                   -- 科目名
    subject_class TEXT,
    subject_subclass TEXT
)
```

### syllabus（シラバス情報）
```sql
CREATE TABLE syllabus (
   -- PKは科目コード
    subject_code TEXT PRIMARY KEY,

    -- 基本情報
    year INTEGER,                        -- 開講年度
    subtitle TEXT,                       -- サブタイトル
    faculty TEXT,                        -- 開講学部
    term TEXT,                           -- 開講学期
    grade_years TEXT,                    -- 対象学年
    campus TEXT,                         -- キャンパス
    credits INTEGER,                     -- 単位数
    remarks TEXT,                        -- 備考
    lecture_code TEXT,                   -- 開講コード

    -- 本文情報
    summary TEXT,                        -- 授業概要
    goals TEXT,                          -- 到達目標
    methods TEXT,                        -- 授業方法
    outside_study TEXT,                  -- 授業外学習
    prerequisites TEXT,                  -- 履修条件
    notes TEXT                           -- 備考
);
```

### syllabus_times（講義時間テーブル）
```sql
CREATE TABLE syllabus_times (
    id INTEGER PRIMARY KEY AUTOINCREMENT, -- 主キー
    syllabus_id TEXT,                     -- シラバスID（syllabus.subject_code）
    day_of_week TEXT,                     -- 開講曜日
    period TEXT,                          -- 開講時限
    FOREIGN KEY (syllabus_id) REFERENCES syllabus(subject_code) ON DELETE CASCADE
);
```

### instructors（教員テーブル）
```sql
CREATE TABLE instructors (
    id INTEGER PRIMARY KEY,               -- 主キー
    name TEXT NOT NULL,                   -- 教員名
    name_kana TEXT,                       -- 教員仮名名
    name_en TEXT,                         -- 教員名（英語）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### syllabus_instructors（シラバス-教員関連テーブル）
```sql
CREATE TABLE syllabus_instructors (
    id INTEGER PRIMARY KEY AUTOINCREMENT, -- 主キー
    syllabus_id TEXT,                     -- シラバスID
    instructor_id INTEGER,                -- 教員ID
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (syllabus_id) REFERENCES syllabus(subject_code) ON DELETE CASCADE,
    FOREIGN KEY (instructor_id) REFERENCES instructors(id) ON DELETE CASCADE
);
```

### lecture_sessions（講義計画テーブル）
```sql
CREATE TABLE lecture_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    syllabus_id TEXT,                     -- シラバスID
    session_number INTEGER,               -- 講義回数（1-30）
    instructor TEXT,                      -- 担当教員
    description TEXT,                     -- 内容
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (syllabus_id) REFERENCES syllabus(subject_code) ON DELETE CASCADE
);
```

### textbooks（教科書テーブル）
```sql
CREATE TABLE textbooks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    syllabus_id TEXT,                     -- シラバスID
    author TEXT,                          -- 著者
    title TEXT,                           -- タイトル
    publisher TEXT,                       -- 出版社
    price TEXT,                           -- 価格
    isbn TEXT,                            -- ISBN
    note TEXT,                            -- 備考
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (syllabus_id) REFERENCES syllabus(subject_code) ON DELETE CASCADE
);
```

### references（参考文献テーブル）
```sql
CREATE TABLE references (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    syllabus_id TEXT,                     -- シラバスID
    author TEXT,                          -- 著者
    title TEXT,                           -- タイトル
    publisher TEXT,                       -- 出版社
    price TEXT,                           -- 価格
    isbn TEXT,                            -- ISBN
    note TEXT,                            -- 備考
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (syllabus_id) REFERENCES syllabus(subject_code) ON DELETE CASCADE
);
```

### grading_criteria（成績評価基準テーブル）
```sql
CREATE TABLE grading_criteria (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    syllabus_id TEXT,                     -- シラバスID
    criteria_type TEXT,                   -- 評価種別（出席/小テスト/レポート/試験/その他）
    ratio TEXT,                           -- 評価比率
    note TEXT,                            -- 備考
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (syllabus_id) REFERENCES syllabus(subject_code) ON DELETE CASCADE
);
```

## インデックス

```sql
-- 基本情報のインデックス
CREATE INDEX idx_syllabus_year ON syllabus(year);
CREATE INDEX idx_syllabus_faculty ON syllabus(faculty);
CREATE INDEX idx_syllabus_term ON syllabus(term);
CREATE INDEX idx_syllabus_grade_years ON syllabus(grade_years);

-- 教員情報のインデックス
CREATE INDEX idx_instructors_name ON instructors(name);
CREATE INDEX idx_instructors_name_kana ON instructors(name_kana);

-- 関連テーブルのインデックス
CREATE INDEX idx_syllabus_instructors_syllabus ON syllabus_instructors(syllabus_id);
CREATE INDEX idx_syllabus_instructors_instructor ON syllabus_instructors(instructor_id);

-- 講義時間のインデックス
CREATE INDEX idx_syllabus_times_syllabus ON syllabus_times(syllabus_id);
CREATE INDEX idx_syllabus_times_day ON syllabus_times(day_of_week);
CREATE INDEX idx_syllabus_times_period ON syllabus_times(period);

-- 講義計画のインデックス
CREATE INDEX idx_lecture_sessions_syllabus ON lecture_sessions(syllabus_id);
CREATE INDEX idx_lecture_sessions_number ON lecture_sessions(session_number);

-- 教科書のインデックス
CREATE INDEX idx_textbooks_syllabus ON textbooks(syllabus_id);
CREATE INDEX idx_textbooks_isbn ON textbooks(isbn);

-- 参考文献のインデックス
CREATE INDEX idx_references_syllabus ON references(syllabus_id);
CREATE INDEX idx_references_isbn ON references(isbn);

-- 成績評価基準のインデックス
CREATE INDEX idx_grading_criteria_syllabus ON grading_criteria(syllabus_id);
CREATE INDEX idx_grading_criteria_type ON grading_criteria(criteria_type);
```

## 補足
このテーブル設計では、以下の特徴があります：

1. **基本情報**
   - 科目の基本情報（年度、科目名、学部など）
   - 教員情報は別テーブルで管理
   - 講義時間は別テーブルで管理（複数時限に対応）
   - 講義計画は別テーブルで管理（30回まで対応可能）
   - 教科書・参考文献は別テーブルで管理（件数制限なし）
   - 成績評価基準は別テーブルで管理（評価項目の追加・変更が容易）

2. **教員情報の管理**
   - `instructors`テーブルで教員の基本情報を管理
   - `syllabus_instructors`テーブルでシラバスと教員の関連を管理
   - 1つのシラバスに複数の教員を割り当て可能

3. **講義時間の管理**
   - `syllabus_times`テーブルで講義の曜日・時限を管理
   - 1つのシラバスに複数の曜日・時限を割り当て可能

4. **講義計画の管理**
   - `lecture_sessions`テーブルで講義計画を管理
   - 回数制限なく拡張可能（デフォルトで30回まで対応）
   - 各回の担当教員と内容を記録

5. **教科書・参考文献の管理**
   - `textbooks`テーブルで教科書情報を管理
   - `references`テーブルで参考文献情報を管理
   - 件数制限なく登録可能
   - ISBN等での検索に対応

6. **詳細情報**
   - 授業概要、目標、方法
   - 成績評価の詳細（各項目の比率と備考）

7. **インデックス**
   - 検索頻度の高い項目にインデックスを設定
   - 年度、学部、学期、学年での検索を最適化
   - 教員名での検索を最適化
   - 講義時間での検索を最適化
   - 講義計画での検索を最適化
   - 教科書・参考文献のISBNでの検索を最適化

## Tips: インデックスの使い方

### 1. インデックスの目的
- 検索の高速化
- データの一意性の保証
- 外部キー制約のサポート

### 2. インデックスを設定すべき項目
- 検索条件として頻繁に使用されるカラム
- 外部キーとして使用されるカラム
- 一意性を保証する必要があるカラム

### 3. インデックスの注意点
- インデックスは検索を高速化するが、INSERT/UPDATE/DELETEの処理を遅くする
- インデックスはストレージ容量を消費する
- 複合インデックスは、左側のカラムから順に使用される

### 4. 本設計でのインデックス例
```sql
-- 基本情報の検索用
CREATE INDEX idx_syllabus_year ON syllabus(year);
CREATE INDEX idx_syllabus_faculty ON syllabus(faculty);
CREATE INDEX idx_syllabus_term ON syllabus(term);
CREATE INDEX idx_syllabus_grade_years ON syllabus(grade_years);

-- 教員情報の検索用
CREATE INDEX idx_instructors_name ON instructors(name);
CREATE INDEX idx_instructors_name_kana ON instructors(name_kana);

-- 関連テーブルの検索用
CREATE INDEX idx_syllabus_instructors_syllabus ON syllabus_instructors(syllabus_id);
CREATE INDEX idx_syllabus_instructors_instructor ON syllabus_instructors(instructor_id);

-- 講義時間の検索用
CREATE INDEX idx_syllabus_times_syllabus ON syllabus_times(syllabus_id);
CREATE INDEX idx_syllabus_times_day ON syllabus_times(day_of_week);
CREATE INDEX idx_syllabus_times_period ON syllabus_times(period);

-- 講義計画の検索用
CREATE INDEX idx_lecture_sessions_syllabus ON lecture_sessions(syllabus_id);
CREATE INDEX idx_lecture_sessions_number ON lecture_sessions(session_number);
```

### 5. インデックスの使用例
```sql
-- 年度と学部で検索（両方のインデックスが使用可能）
SELECT * FROM syllabus 
WHERE year = 2024 AND faculty = '情報学部';

-- 教員名で検索（name_kanaのインデックスが使用可能）
SELECT * FROM instructors 
WHERE name_kana LIKE 'ヤマダ%';

-- 教員の担当科目を検索（関連テーブルのインデックスが使用可能）
SELECT s.* 
FROM syllabus s
JOIN syllabus_instructors si ON s.subject_code = si.syllabus_id
WHERE si.instructor_id = 1;

-- 特定の曜日・時限の講義を検索
SELECT s.* 
FROM syllabus s
JOIN syllabus_times st ON s.subject_code = st.syllabus_id
WHERE st.day_of_week = '月' AND st.period = '1';

-- 特定の講義回の内容を検索
SELECT s.subject_name, ls.* 
FROM syllabus s
JOIN lecture_sessions ls ON s.subject_code = ls.syllabus_id
WHERE ls.session_number = 1;

-- 特定の教員が担当する講義回を検索
SELECT s.subject_name, ls.* 
FROM syllabus s
JOIN lecture_sessions ls ON s.subject_code = ls.syllabus_id
WHERE ls.instructor LIKE '%山田%';

-- ISBNで教科書を検索
SELECT s.subject_name, t.* 
FROM syllabus s
JOIN textbooks t ON s.subject_code = t.syllabus_id
WHERE t.isbn = '978-4-XXXX-XXXX-X';

-- 特定の出版社の参考文献を検索
SELECT s.subject_name, r.* 
FROM syllabus s
JOIN references r ON s.subject_code = r.syllabus_id
WHERE r.publisher LIKE '%出版社名%';

-- 特定の評価種別の科目を検索
SELECT s.subject_name, gc.* 
FROM syllabus s
JOIN grading_criteria gc ON s.subject_code = gc.syllabus_id
WHERE gc.criteria_type = '出席';

-- 評価比率が高い順に科目を検索
SELECT s.subject_name, gc.criteria_type, gc.ratio
FROM syllabus s
JOIN grading_criteria gc ON s.subject_code = gc.syllabus_id
WHERE gc.criteria_type = 'レポート'
ORDER BY gc.ratio DESC;
```