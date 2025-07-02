-- 数理の科目で必修かつ期末試験がない科目を検索
-- File Version: v1.0.0
-- Project Version: v2.1.6
-- Last Updated: 2025-01-27

SELECT DISTINCT
    cache_data->>'科目名' AS 科目名,
    syllabus_lateral.syllabus->'担当' AS 担当講師,
    syllabus_lateral.syllabus->'対象学部課程' AS 対象学部,
    syllabus_lateral.syllabus->>'曜日' AS 開講曜日,
    syllabus_lateral.syllabus->'時限' AS 開講時限
FROM syllabus_cache,
LATERAL (
    SELECT rj
    FROM jsonb_array_elements(cache_data->'履修情報') AS rj
    WHERE jsonb_typeof(cache_data->'履修情報') = 'array'
) rj_lateral,
LATERAL (
    SELECT yk
    FROM jsonb_array_elements(rj_lateral.rj->'履修要綱') AS yk
    WHERE jsonb_typeof(rj_lateral.rj->'履修要綱') = 'array'
    AND yk->>'学部課程' LIKE '%数理%'
    AND yk->>'必須度' = '必修'
) yk_lateral,
LATERAL (
    SELECT kj
    FROM jsonb_array_elements(cache_data->'開講情報') AS kj
    WHERE jsonb_typeof(cache_data->'開講情報') = 'array'
) kj_lateral,
LATERAL (
    SELECT syllabus
    FROM jsonb_array_elements(kj_lateral.kj->'シラバス') AS syllabus
    WHERE jsonb_typeof(kj_lateral.kj->'シラバス') = 'array'
    AND EXISTS (
        SELECT 1
        FROM jsonb_array_elements_text(syllabus->'対象学部課程') AS faculty
        WHERE faculty LIKE '%数理%'
    )
    AND NOT EXISTS (
        SELECT 1
        FROM jsonb_array_elements(syllabus->'成績') AS grade
        WHERE jsonb_typeof(syllabus->'成績') = 'array'
        AND (
            grade->>'項目' LIKE '%期末%'
            OR grade->>'項目' LIKE '%期末試験%'
            OR grade->>'評価方法' LIKE '%期末%'
            OR grade->>'備考' LIKE '%期末%'
        )
    )
) syllabus_lateral
WHERE cache_name = 'subject_syllabus_cache'
ORDER BY 科目名;

-- 検索条件の説明:
-- 1. 学部課程に「数理」が含まれる科目
-- 2. 必須度が「必修」の科目
-- 3. 成績評価に「期末」という文字が含まれない科目
--    - 項目名、評価方法、備考のいずれにも期末試験の記載がない
