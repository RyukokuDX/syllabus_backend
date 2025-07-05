-- 数理の必修で数学系の科目一覧
-- File Version: v1.0.0
-- Project Version: v2.3.3
-- Last Updated: 2025-07-02

SELECT DISTINCT
    cache_data->>'科目名' as 科目名,
    jsonb_array_elements(cache_data->'履修情報一覧') as 履修情報
FROM syllabus_cache 
WHERE cache_name = 'subject_syllabus_cache'
    AND cache_data @> '{
        "履修情報一覧": [{
            "履修要綱一覧": [{
                "学部課程": "数理",
                "必須度": "必修",
                "科目小区分": "数学"
            }]
        }]
    }'::jsonb
ORDER BY 科目名; 