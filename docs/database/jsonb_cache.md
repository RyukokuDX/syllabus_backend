---
title: JSONBキャッシュリスト仕様書
file_version: v2.5.1
project_version: v2.5.1
last_updated: 2025-07-04
---

# JSONBキャッシュリスト仕様書

- File Version: v2.5.1
- Project Version: v2.5.1
- Last Updated: 2025-07-04

[readmeへ](../../README.md) | [データベース構造定義へ](structure.md) | [設計ポリシーへ](policy.md) | [ER図へ](er.md)

## 目次

1. [概要](#概要)
2. [フィールド命名規則](#フィールド命名規則)
3. [キャッシュ対象テーブル](#キャッシュ対象テーブル)
4. [キャッシュ生成方針](#キャッシュ生成方針)
5. [キャッシュ更新戦略](#キャッシュ更新戦略)
6. [パフォーマンス考慮事項](#パフォーマンス考慮事項)
7. [実装ガイドライン](#実装ガイドライン)

## 概要

### 目的
- 複雑なJOINクエリのパフォーマンス向上
- アプリケーション層でのデータアクセス効率化
- リアルタイム性を重視しない集計・分析処理の高速化

## フィールド命名規則

### 基本方針
JSONBキャッシュのフィールド命名は、LLMがデータ構造を正確に理解できるよう、語尾による構造指標を一貫して使用する。

### 語尾による構造指標

| 構造 | 語尾 | 例 | 説明 |
|------|------|-----|------|
| 配列 | `一覧` | `教員一覧`, `教科書一覧` | 要素数0以上の繰り返し構造 |
| 単一値 | 名詞のまま、または`名`、`数`、`年度` | `科目名`, `単位数` | 固有の1つの値 |

### 命名規則の効果
- **クエリ精度向上**: `教員一覧[].氏名` のように正しいパスを推測
- **構造の明確化**: 配列か単一値かの曖昧さを排除
- **型推論の容易化**: JSON Schema生成にも役立つ
- **プロンプトのテンプレ化**: 「`〜一覧[].〜名` にアクセスせよ」など明示可能

## キャッシュ対象テーブル

### 主要テーブル
- **syllabus_master**: シラバスマスター情報
- **syllabus**: シラバス基本情報
- **subject_name**: 科目名マスター
- **syllabus_instructor**: シラバス担当教員
- **instructor**: 教員マスター
- **lecture_time**: 講義時間
- **syllabus_book**: シラバス書籍関連
- **book**: 書籍マスター
- **book_uncategorized**: 未分類書籍
- **syllabus_faculty**: シラバス学部課程関連
- **faculty**: 学部課程マスター
- **grading_criterion**: 成績評価基準
- **subject**: 履修要綱
- **class**: 科目区分マスター
- **subclass**: 科目小区分マスター
- **subject_attribute_value**: 科目属性値

## キャッシュ生成方針

### 基本方針
1. **LLMによるアクセス性重視** idやコードを利用しない, 自然言語による解析
1. **階層構造の活用**: 親子関係を明確に表現
1. **配列の活用**: 1対多の関係を配列として表現（1件でも必ず配列）

### 更新方式
1. **全量更新**: キャッシュ全体を再生成

## キャッシュ更新戦略

### 更新タイミング
- データベースの構造変更時
- 大量データの更新時
- パフォーマンス改善が必要な時

### 更新方法
- 既存キャッシュの削除
- 新規キャッシュの生成
- バージョン管理による段階的移行

## パフォーマンス考慮事項

### キャッシュサイズ
- JSONBデータの圧縮
- 不要なフィールドの除外
- インデックスの最適化

### クエリ最適化
- JSONB演算子の活用
- インデックス付きフィールドの活用
- 部分的なデータ取得

## 実装ガイドライン

### 配列フィールドの型保証とエラー防止（LLM向け）
- **配列フィールドは必ず配列型で格納すること**
  - 例：`json_agg(...)`で生成し、`COALESCE(..., '[]'::json)`で空配列を保証する
- **nullやスカラ値が混入すると、jsonb_array_elements等で「スカラから要素を取り出すことはできません」エラーが発生する**
- **キャッシュ生成時、全ての配列フィールドにCOALESCEを適用し、空配列を保証すること**
- **型チェック用のデバッグクエリを活用し、配列でない値が混入していないか定期的に検証すること**
  - 例：
    ```sql
    SELECT COUNT(*) FROM syllabus_cache WHERE cache_name = 'subject_syllabus_cache' AND jsonb_typeof(cache_data->'開講情報一覧') IS DISTINCT FROM 'array';
    ```
- **LLMによる自動クエリ生成時も、配列型であることを前提に展開処理を記述すること**

### 開発環境での利用
- 開発時は小規模データでのテスト
- 本番環境でのパフォーマンス検証
- 段階的なキャッシュ導入

### メンテナンス
- 定期的なキャッシュ更新
- データ整合性の確認
- パフォーマンス監視

## JSONBフィールドフォーマット

### サンプル構造
```json
{
  "科目名": "微分積分学I",
  "開講情報一覧": [
    {
      "年度": 2025,
      "シラバス一覧": [
        {
          "担当教員一覧": [
            { "氏名": "田中 太郎", "役割": "主担当" },
            { "氏名": "佐藤 花子", "役割": "副担当" }
          ],
          "対象学部課程一覧": ["理工学部", "先端理工学部"],
          "学期": "1Q",
          "講義時間一覧": [
            { "曜日": "月曜日", "時限": 1 },
            { "曜日": "月曜日", "時限": 2 }
          ],
          "単位数": 2,
          "教科書一覧": [
            { "書名": "微分積分学入門", "著者": "山田 数学", "ISBN": "978-4-1234-5678-9", "価格": 2500, "備考": "第3版を使用" }
          ],
          "教科書コメント": "買ってください",
          "参考書一覧": [
            { "書名": "大学数学の基礎", "著者": "鈴木 計算", "ISBN": "978-4-9876-5432-1", "価格": 1800, "備考": "参考程度" }
          ],
          "参考書コメント": "借りて下さい",
          "成績評価基準一覧": [
            { "項目": "定期試験", "割合": 70, "評価方法": "筆記試験", "備考": "中間試験30%、期末試験40%" },
            { "項目": "平常点", "割合": 30, "評価方法": "出席・課題提出", "備考": "毎回の課題提出を評価" }
          ],
          "成績評価コメント": "慈悲はない"
        }
      ]
    }
  ],
  "履修情報一覧": [
    {
      "年度": 2025,
      "履修要綱一覧": [
        {
          "学部課程": "理工学部",
          "科目区分": "専門基礎科目",
          "科目小区分": "数学",
          "必須度": "必修",
          "学修プログラム一覧": [1,2,3]
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

#### 開講情報一覧
- **年度**: シラバスの年度（syllabus_master.syllabus_year）
- **シラバス一覧**: 年度内のシラバス情報の配列（1件でも必ず配列）

##### シラバス詳細
- **担当教員一覧**: 教員情報の配列
  - **氏名**: 教員の氏名（instructor.name）
  - **役割**: 担当教員の役割（syllabus_instructor.role）
- **対象学部課程一覧**: 開講対象の学部課程の配列（syllabus_faculty.faculty_name）
- **学期**: 開講学期（syllabus.term）
- **講義時間一覧**: 講義時間情報の配列
  - **曜日**: 開講曜日（lecture_time.day_of_week）
  - **時限**: 開講時限（lecture_time.period）
- **単位数**: 単位数（syllabus.credits）
- **教科書一覧**: 教科書情報の配列（syllabus_book.role = "教科書" or book_uncategorized.role = "教科書"）
- **参考書一覧**: 参考書情報の配列（syllabus_book.role = "参考書" or book_uncategorized.role = "参考書"）
- **成績評価基準一覧**: 成績評価基準の配列

##### 書籍情報
- **書名**: 書籍タイトル（book.title or book_uncategorized.title）
- **著者**: 著者名（book.author or book_uncategorized.author）
- **ISBN**: ISBN番号（book.isbn or book_uncategorized.isbn）
- **価格**: 価格（book.price or book_uncategorized.price）

##### 成績評価
- **項目**: 評価項目（grading_criterion.criteria_type）
- **割合**: 評価比率（grading_criterion.ratio）
- **評価方法**: 評価方法の詳細（grading_criterion.criteria_description）
- **備考**: 備考情報（grading_criterion.note）

#### 履修情報一覧
- **年度**: 履修要綱の年度（subject.curriculum_year）
- **履修要綱一覧**: 履修要綱情報の配列

##### 履修要綱詳細
- **学部課程**: 開講学部・課程（faculty.faculty_name）
- **科目区分**: 科目区分（class.class_name）
- **科目小区分**: 科目小区分（subclass.subclass_name）
- **必須度**: 必修/選択区分（subject.requirement_type）
- **課程別エンティティ**: 課程別の詳細情報（subject_attribute_value.value where attribute_id = 課程別エンティティ）
    - 学習プログラム一覧はこのサンプル

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
                '氏名', i.name,
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
                '価格', b.price
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
                '価格', bu.price
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
                '価格', b.price
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
                '価格', bu.price
            ) as book_info
        FROM book_uncategorized bu
        WHERE bu.role = '参考書'
    ) combined_references
    GROUP BY syllabus_id
),
faculty_data AS (
    SELECT 
        sf.syllabus_id,
        json_agg(f.faculty_name) as faculties
    FROM syllabus_faculty sf
    JOIN faculty f ON sf.faculty_id = f.faculty_id
    GROUP BY sf.syllabus_id
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
),
syllabus_by_year AS (
    SELECT 
        sd.subject_name_id,
        sd.subject_name,
        sd.syllabus_year,
        json_agg(
            json_build_object(
                '担当教員一覧', COALESCE(id.instructors, '[]'::json),
                '対象学部課程一覧', COALESCE(fd.faculties, '[]'::json),
                '学期', sd.term,
                '講義時間一覧', COALESCE(ltd.lecture_times, '[]'::json),
                '単位数', sd.credits,
                '教科書一覧', COALESCE(td.textbooks, '[]'::json),
                '教科書コメント', sd.textbook_comment,
                '参考書一覧', COALESCE(rd.references, '[]'::json),
                '参考書コメント', sd.reference_comment,
                '成績評価基準一覧', COALESCE(gd.grading_criteria, '[]'::json),
                '成績評価コメント', sd.grading_comment
            )
        ) as syllabi
    FROM syllabus_data sd
    LEFT JOIN instructor_data id ON sd.syllabus_id = id.syllabus_id
    LEFT JOIN faculty_data fd ON sd.syllabus_id = fd.syllabus_id
    LEFT JOIN lecture_time_data ltd ON sd.syllabus_id = ltd.syllabus_id
    LEFT JOIN textbook_data td ON sd.syllabus_id = td.syllabus_id
    LEFT JOIN reference_data rd ON sd.syllabus_id = rd.syllabus_id
    LEFT JOIN grading_data gd ON sd.syllabus_id = gd.syllabus_id
    GROUP BY sd.subject_name_id, sd.subject_name, sd.syllabus_year
),
cache_data AS (
    SELECT 
        sby.subject_name_id,
        json_build_object(
            '科目名', sby.subject_name,
            '開講情報一覧', json_agg(
                json_build_object(
                    '年度', sby.syllabus_year,
                    'シラバス一覧', sby.syllabi
                )
            ),
            '履修情報一覧', json_agg(
                json_build_object(
                    '年度', subd.curriculum_year,
                    '履修要綱一覧', subd.subject_info
                )
            )
        ) as cache_data
    FROM syllabus_by_year sby
    LEFT JOIN subject_data subd ON sby.subject_name_id = subd.subject_name_id
    GROUP BY sby.subject_name_id, sby.subject_name
)
INSERT INTO syllabus_cache (cache_name, subject_name_id, cache_data, cache_version)
SELECT 
    'subject_syllabus_cache',
    cd.subject_name_id,
    cd.cache_data,
    'v2.3.0'
FROM cache_data cd;
```

### クエリ説明

#### 主要CTE（Common Table Expression）

1. **syllabus_data**: シラバス基本情報の取得
2. **instructor_data**: 担当教員情報の集約
3. **lecture_time_data**: 講義時間情報の集約
4. **textbook_data**: 教科書情報の集約（book + book_uncategorized）
5. **reference_data**: 参考書情報の集約（book + book_uncategorized）
6. **faculty_data**: 対象学部課程情報の集約（syllabus_faculty）
7. **grading_data**: 成績評価基準の集約
8. **subject_data**: 履修要綱情報の集約
9. **syllabus_by_year**: 年度別シラバス情報の集約
10. **cache_data**: 最終的なキャッシュデータの構築

#### 特徴

- **LEFT JOIN**: 関連データが存在しない場合でも基本情報を取得
- **COALESCE**: NULL値の適切な処理
- **json_agg**: 1対多の関係を配列として集約
- **json_build_object**: 構造化されたJSONオブジェクトの生成
- **二段階GROUP BY**: 年度別集約→科目名単位集約で重複を排除

## LLM向け構造概要

### データ構造の特徴

#### 配列フィールド（必ず配列形式）
- **開講情報一覧**: 年度別の開講情報の配列
- **シラバス一覧**: 各年度内のシラバス情報の配列（1件でも配列）
- **担当教員一覧**: 教員情報の配列
- **対象学部課程一覧**: 開講対象の学部課程名の配列（syllabus_facultyから取得）
- **講義時間一覧**: 講義時間情報の配列
- **教科書一覧**: 教科書情報の配列
- **参考書一覧**: 参考書情報の配列
- **成績評価基準一覧**: 成績評価基準の配列
- **履修情報一覧**: 年度別の履修情報の配列
- **履修要綱一覧**: 各年度内の履修要綱情報の配列

#### 単一値フィールド
- **科目名**: 文字列
- **年度**: 数値（年度）
- **氏名**: 文字列
- **役割**: 文字列
- **学期**: 文字列
- **単位数**: 数値
- **書名**: 文字列
- **著者**: 文字列
- **ISBN**: 文字列
- **価格**: 数値
- **備考**: 文字列
- **項目**: 文字列
- **割合**: 数値
- **評価方法**: 文字列
- **学部課程**: 文字列
- **科目区分**: 文字列
- **科目小区分**: 文字列
- **必須度**: 文字列
- **課程別エンティティ**: 文字列

#### 配列内オブジェクトフィールド
- **講義時間一覧内の曜日**: 文字列
- **講義時間一覧内の時限**: 数値

#### コメントフィールド
- **教科書コメント**: 文字列
- **参考書コメント**: 文字列
- **成績評価コメント**: 文字列

### データアクセスパターン

#### 科目検索
```json
// 科目名で検索
"科目名": "微分積分学I"

// 年度別の開講情報
"開講情報一覧": [
  {
    "年度": 2025,
    "シラバス一覧": [...]
  }
]
```

#### 教員検索
```json
// 担当教員情報
"担当教員一覧": [
  {
    "氏名": "田中 太郎",
    "役割": "主担当"
  }
]

// LLM用パス例
// 教員一覧[].氏名
// 教員一覧[].役割
```

#### 学部課程検索
```json
// 開講対象学部課程（シラバスレベル）
"対象学部課程一覧": ["理工学部", "先端理工学部"]

// 履修要綱の学部課程（履修情報レベル）
"学部課程": "理工学部"

// LLM用パス例
// 開講情報一覧[].シラバス一覧[].対象学部課程一覧[]
// 履修情報一覧[].履修要綱一覧[].学部課程

// 学部課程での科目検索例
// 理工学部で開講される科目を検索
"開講情報一覧": [
  {
    "シラバス一覧": [
      {
        "対象学部課程一覧": ["理工学部", "先端理工学部"]
      }
    ]
  }
]

// 特定学部課程の履修要綱を検索
"履修情報一覧": [
  {
    "履修要綱一覧": [
      {
        "学部課程": "理工学部",
        "科目区分": "専門基礎科目",
        "必須度": "必修"
      }
    ]
  }
]
```

#### 時間検索
```json
// 講義時間
"講義時間一覧": [
  { "曜日": "月曜日", "時限": 1 },
  { "曜日": "月曜日", "時限": 2 }
]

// LLM用パス例
// 講義時間一覧[].曜日
// 講義時間一覧[].時限
```

#### 書籍検索
```json
// 教科書・参考書
"教科書一覧": [
  {
    "書名": "微分積分学入門",
    "著者": "山田 数学",
    "ISBN": "978-4-1234-5678-9",
    "価格": 2500
  }
]

// LLM用パス例
// 教科書一覧[].書名
// 教科書一覧[].著者
// 教科書一覧[].価格
```

### 注意事項
- 配列フィールドは常に配列形式（空配列の場合も含む）
- 単一値フィールドは文字列または数値
- 年度情報は「開講情報一覧」と「履修情報一覧」で別々に管理
- 教員情報は「担当教員一覧」配列内のオブジェクトとして格納
- 講義時間情報は「講義時間一覧」配列内のオブジェクトとして格納（曜日・時限の組み合わせ）
- 書籍情報は「教科書一覧」「参考書一覧」配列内のオブジェクトとして格納
- 学部課程情報は「開講情報一覧」と「履修情報一覧」で異なるレベルで管理
  - 開講情報一覧: シラバスレベルで「対象学部課程一覧」として配列形式
  - 履修情報一覧: 履修要綱レベルで「学部課程」として単一値
- 課程別エンティティは履修要綱レベルでのみ存在し、設定されていない場合はフィールド自体が存在しない

[🔝 ページトップへ](#jsonbキャッシュリスト仕様書) 