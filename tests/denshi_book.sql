-- 電子情報通信課程の科目の教科書をすべて表示するクエリ
-- subject_syllabus_cacheのJSONBキャッシュを利用（jsonb_cache.md仕様準拠）

WITH denshi_subjects AS (
    -- 電子情報通信課程の科目を抽出
    SELECT 
        sc.subject_name_id,
        sc.cache_data->>'科目名' as subject_name,
        sc.cache_data
    FROM syllabus_cache sc
    WHERE EXISTS (
        SELECT 1
        FROM jsonb_array_elements(sc.cache_data->'履修情報') as year_info
        CROSS JOIN jsonb_array_elements(
            CASE 
                WHEN year_info->'履修要綱' IS NOT NULL AND jsonb_typeof(year_info->'履修要綱') = 'array'
                THEN year_info->'履修要綱'
                ELSE '[]'::jsonb
            END
        ) as curriculum
        WHERE curriculum->>'学部課程' = '電子情報通信課程'
    )
),
syllabus_textbooks AS (
    -- 各シラバスの教科書情報を展開
    SELECT 
        ds.subject_name_id,
        ds.subject_name,
        year_info->>'年' as syllabus_year,
        syllabus->>'学期' as term,
        syllabus->>'単位' as credits,
        textbook
    FROM denshi_subjects ds
    CROSS JOIN jsonb_array_elements(ds.cache_data->'開講情報') as year_info
    CROSS JOIN jsonb_array_elements(year_info->'シラバス') as syllabus
    CROSS JOIN jsonb_array_elements(
        CASE 
            WHEN syllabus->'教科書' IS NOT NULL AND jsonb_typeof(syllabus->'教科書') = 'array'
            THEN syllabus->'教科書'
            ELSE '[]'::jsonb
        END
    ) as textbook
    WHERE syllabus->'教科書' IS NOT NULL 
    AND jsonb_typeof(syllabus->'教科書') = 'array'
    AND jsonb_array_length(syllabus->'教科書') > 0
)
SELECT 
    subject_name_id,
    subject_name,
    syllabus_year,
    term,
    credits,
    textbook->>'書名' as book_title,
    textbook->>'著者' as author,
    textbook->>'ISBN' as isbn,
    textbook->>'値段' as price
FROM syllabus_textbooks
ORDER BY 
    subject_name_id,
    syllabus_year,
    book_title; 