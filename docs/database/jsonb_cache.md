---
title: JSONBキャッシュリスト仕様書
file_version: v2.0.2
project_version: v2.0.4
last_updated: 2025-07-01
---

# JSONBキャッシュリスト仕様書

- File Version: v2.0.2
- Project Version: v2.0.4
- Last Updated: 2025-07-01

[readmeへ](../../README.md) | [データベース構造定義へ](structure.md) | [設計ポリシーへ](policy.md) | [ER図へ](er.md)

## 目次

1. [概要](#概要)
2. [キャッシュ対象テーブル](#キャッシュ対象テーブル)
3. [キャッシュ生成方針](#キャッシュ生成方針)
4. [キャッシュ更新戦略](#キャッシュ更新戦略)
5. [パフォーマンス考慮事項](#パフォーマンス考慮事項)
6. [実装ガイドライン](#実装ガイドライン)

## 目的
- 複雑なJOINクエリのパフォーマンス向上
- アプリケーション層でのデータアクセス効率化
- リアルタイム性を重視しない集計・分析処理の高速化

## キャッシュ生成方針

### 基本方針
1. **LLMによるアクセス性重視** idやコードを利用しない, 自然言語による解析
1. **階層構造の活用**: 親子関係を明確に表現
1. **配列の活用**: 1対多の関係を配列として表現

### 更新方式
1. **全量更新**: キャッシュ全体を再生成

## JSONBフィールドフォーマット

### サンプル構造
```json
{
  "科目名": "微分積分学I",
  "開講情報": [
    {
      "年": 2025,
      "シラバス": [
        {
          "担当": [
            {
              "教員名": "田中 太郎",
              "役割": "主担当"
            },
            {
              "教員名": "佐藤 花子",
              "役割": "副担当"
            }
          ],
          "学期": "1Q",
          "曜日": "月曜日",
          "時限": [1,2],
          "単位": 2,
          "教科書": [
            {
              "書名": "微分積分学入門",
              "著者": "山田 数学",
              "ISBN": "978-4-1234-5678-9",
              "値段": 2500,
              "備考": "第3版を使用"
            }
          ],
          "教科書コメント": "買ってください",
          "参考書": [
            {
              "書名": "大学数学の基礎",
              "著者": "鈴木 計算",
              "ISBN": "978-4-9876-5432-1",
              "値段": 1800,
              "備考": "参考程度"
            }
          ],
          "参考書コメント": "借りて下さい",
          "成績": [
            {
              "項目": "定期試験",
              "割合": 70,
              "評価方法": "筆記試験",
              "備考": "中間試験30%、期末試験40%"
            },
            {
              "項目": "平常点",
              "割合": 30,
              "評価方法": "出席・課題提出",
              "備考": "毎回の課題提出を評価"
            }
          ],
          "成績コメント": "慈悲はない"
        }
      ]
    }
  ],
  "履修情報": [
    {
      "年": 2025,
      "履修要綱": [
        {
          "学部課程": "理工学部",
          "科目区分": "専門基礎科目",
          "科目小区分": "数学",
          "必須度": "必修",
          "学修プログラム": [1,2,3]
        },
        {
          "学部課程": "先端理工学部",
          "科目区分": "専門基礎科目",
          "科目小区分": "数学",
          "必須度": "選択",
          "課程別エンティティ": "情報工学科"
        }
      ]
    }
  ]
}
```

### フィールド説明

#### 基本情報
- **科目名**: 科目の正式名称（subject_name.name）

#### 開講情報
- **年**: シラバスの年度（syllabus_master.syllabus_year）
- **シラバス**: 年度内のシラバス情報の配列

##### シラバス詳細
- **担当**: 教員情報の配列
  - **教員名**: 教員の氏名（instructor.name）
  - **役割**: 担当教員の役割（syllabus_instructor.role）
- **学期**: 開講学期（syllabus.term）
- **曜日**: 開講曜日（lecture_time.day_of_week）
- **時限**: 開講時限（lecture_time.period）
- **単位**: 単位数（syllabus.credits）
- **教科書**: 教科書情報の配列（syllabus_book.role = "教科書" or book_uncategorized.role = "教科書"）
- **参考書**: 参考書情報の配列（syllabus_book.role = "参考書" or book_uncategorized.role = "参考書"）
- **成績**: 成績評価基準の配列

##### 書籍情報
- **書名**: 書籍タイトル（book.title or book_uncategorized.title）
- **著者**: 著者名（book.author or book_uncategorized.author）
- **ISBN**: ISBN番号（book.isbn or book_uncategorized.isbn）
- **値段**: 価格（book.price or book_uncategorized.price）
- **備考**: 備考情報（syllabus_book.noteのみ、book_uncategorizedには備考フィールドなし）

##### 成績評価
- **項目**: 評価項目（grading_criterion.criteria_type）
- **割合**: 評価比率（grading_criterion.ratio）
- **評価方法**: 評価方法の詳細（grading_criterion.criteria_description）
- **備考**: 備考情報（grading_criterion.note）

#### 履修情報
- **年**: 履修要綱の年度（subject.curriculum_year）
- **履修要綱**: 履修要綱情報の配列

##### 履修要綱詳細
- **学部課程**: 開講学部・課程（faculty.faculty_name）
- **科目区分**: 科目区分（class.class_name）
- **科目小区分**: 科目小区分（subclass.subclass_name）
- **必須度**: 必修/選択区分（subject.requirement_type）
- **課程別エンティティ**: 課程別の詳細情報（subject_attribute_value.value where attribute_id = 課程別エンティティ）
    - 学習プログラムはこのサンプル

### 生成Querry

#### subject_syllabus_cache

```sql
WITH syllabus_data AS (
    SELECT 
        sm.syllabus_id,
        sm.syllabus_code,
        sm.syllabus_year,
        s.subject_name_id,
        sn.name as subject_name,
        s.subtitle,
        s.term,
        s.campus,
        s.credits,
        s.goals,
        s.summary,
        s.attainment,
        s.methods,
        s.outside_study,
        s.textbook_comment,
        s.reference_comment,
        s.grading_comment,
        s.advice
    FROM syllabus_master sm
    JOIN syllabus s ON sm.syllabus_id = s.syllabus_id
    JOIN subject_name sn ON s.subject_name_id = sn.subject_name_id
),
instructor_data AS (
    SELECT 
        si.syllabus_id,
        json_agg(
            json_build_object(
                '教員名', i.name,
                '役割', COALESCE(si.role, '担当')
            )
        ) as instructors
    FROM syllabus_instructor si
    JOIN instructor i ON si.instructor_id = i.instructor_id
    GROUP BY si.syllabus_id
),
lecture_time_data AS (
    SELECT 
        lt.syllabus_id,
        json_agg(
            json_build_object(
                '曜日', lt.day_of_week,
                '時限', lt.period
            )
        ) as lecture_times,
        json_agg(lt.period) as periods
    FROM lecture_time lt
    GROUP BY lt.syllabus_id
),
textbook_data AS (
    SELECT 
        syllabus_id,
        json_agg(book_info) as textbooks
    FROM (
        -- syllabus_bookから教科書を取得
        SELECT 
            sb.syllabus_id,
            json_build_object(
                '書名', b.title,
                '著者', b.author,
                'ISBN', b.isbn,
                '値段', b.price,
                '備考', sb.note
            ) as book_info
        FROM syllabus_book sb
        JOIN book b ON sb.book_id = b.book_id
        WHERE sb.role = '教科書'
        
        UNION ALL
        
        -- book_uncategorizedから教科書を取得
        SELECT 
            bu.syllabus_id,
            json_build_object(
                '書名', bu.title,
                '著者', bu.author,
                'ISBN', bu.isbn,
                '値段', bu.price
            ) as book_info
        FROM book_uncategorized bu
        WHERE bu.role = '教科書'
    ) combined_textbooks
    GROUP BY syllabus_id
),
reference_data AS (
    SELECT 
        syllabus_id,
        json_agg(book_info) as references
    FROM (
        -- syllabus_bookから参考書を取得
        SELECT 
            sb.syllabus_id,
            json_build_object(
                '書名', b.title,
                '著者', b.author,
                'ISBN', b.isbn,
                '値段', b.price,
                '備考', sb.note
            ) as book_info
        FROM syllabus_book sb
        JOIN book b ON sb.book_id = b.book_id
        WHERE sb.role = '参考書'
        
        UNION ALL
        
        -- book_uncategorizedから参考書を取得
        SELECT 
            bu.syllabus_id,
            json_build_object(
                '書名', bu.title,
                '著者', bu.author,
                'ISBN', bu.isbn,
                '値段', bu.price
            ) as book_info
        FROM book_uncategorized bu
        WHERE bu.role = '参考書'
    ) combined_references
    GROUP BY syllabus_id
),
grading_data AS (
    SELECT 
        gc.syllabus_id,
        json_agg(
            json_build_object(
                '項目', gc.criteria_type,
                '割合', gc.ratio,
                '評価方法', gc.criteria_description,
                '備考', gc.note
            )
        ) as grading_criteria
    FROM grading_criterion gc
    GROUP BY gc.syllabus_id
),
subject_data AS (
    SELECT 
        sub.subject_name_id,
        sub.curriculum_year,
        json_agg(
            json_build_object(
                '学部課程', f.faculty_name,
                '科目区分', c.class_name,
                '科目小区分', COALESCE(sc.subclass_name, ''),
                '必須度', sub.requirement_type,
                '課程別エンティティ', sav.value
            )
        ) as subject_info
    FROM subject sub
    JOIN faculty f ON sub.faculty_id = f.faculty_id
    JOIN class c ON sub.class_id = c.class_id
    LEFT JOIN subclass sc ON sub.subclass_id = sc.subclass_id
    LEFT JOIN subject_attribute_value sav ON sub.subject_id = sav.subject_id
    LEFT JOIN subject_attribute sa ON sav.attribute_id = sa.attribute_id
        AND sa.attribute_name = '課程別エンティティ'
    GROUP BY sub.subject_name_id, sub.curriculum_year
)
SELECT 
    json_build_object(
        '科目名', sd.subject_name,
        '開講情報', json_agg(
            json_build_object(
                '年', sd.syllabus_year,
                'シラバス', json_build_object(
                    '担当', COALESCE(id.instructors, '[]'::json),
                    '学期', sd.term,
                    '曜日', COALESCE(ltd.lecture_times->0->>'曜日', ''),
                    '時限', COALESCE(ltd.periods, '[]'::json),
                    '単位', sd.credits,
                    '教科書', COALESCE(td.textbooks, '[]'::json),
                    '教科書コメント', sd.textbook_comment,
                    '参考書', COALESCE(rd.references, '[]'::json),
                    '参考書コメント', sd.reference_comment,
                    '成績', COALESCE(gd.grading_criteria, '[]'::json),
                    '成績コメント', sd.grading_comment
                )
            )
        ),
        '履修情報', json_agg(
            json_build_object(
                '年', subd.curriculum_year,
                '履修要綱', subd.subject_info
            )
        )
    ) as cache_data
FROM syllabus_data sd
LEFT JOIN instructor_data id ON sd.syllabus_id = id.syllabus_id
LEFT JOIN lecture_time_data ltd ON sd.syllabus_id = ltd.syllabus_id
LEFT JOIN textbook_data td ON sd.syllabus_id = td.syllabus_id
LEFT JOIN reference_data rd ON sd.syllabus_id = rd.syllabus_id
LEFT JOIN grading_data gd ON sd.syllabus_id = gd.syllabus_id
LEFT JOIN subject_data subd ON sd.subject_name_id = subd.subject_name_id
GROUP BY sd.subject_name_id, sd.subject_name;
```

### クエリ説明

#### 主要CTE（Common Table Expression）

1. **syllabus_data**: シラバス基本情報の取得
2. **instructor_data**: 担当教員情報の集約
3. **lecture_time_data**: 講義時間情報の集約
4. **textbook_data**: 教科書情報の集約（book + book_uncategorized）
5. **reference_data**: 参考書情報の集約（book + book_uncategorized）
6. **grading_data**: 成績評価基準の集約
7. **subject_data**: 履修要綱情報の集約

#### 特徴

- **LEFT JOIN**: 関連データが存在しない場合でも基本情報を取得
- **COALESCE**: NULL値の適切な処理
- **json_agg**: 1対多の関係を配列として集約
- **json_build_object**: 構造化されたJSONオブジェクトの生成
- **GROUP BY**: 科目名単位でのデータ集約

[🔝 ページトップへ](#jsonbキャッシュリスト仕様書) 