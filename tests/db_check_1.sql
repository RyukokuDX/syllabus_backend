-- 数理の科目で科目名が「情報基礎」の科目名、シラバスコード、シラバスID、開講曜日、時限を表示
-- File Version: v2.0.0
-- Project Version: v2.1.6
-- Last Updated: 2025-07-02

-- 数理の科目で科目名が「情報基礎」の基本情報と講義時間を取得
SELECT DISTINCT
    sn.name AS 科目名,
    sm.syllabus_code AS シラバスコード,
    sm.syllabus_id AS シラバスID,
    lt.day_of_week AS 開講曜日,
    lt.period AS 時限
FROM syllabus_master sm
JOIN syllabus s ON sm.syllabus_id = s.syllabus_id
JOIN subject_name sn ON s.subject_name_id = sn.subject_name_id
JOIN lecture_time lt ON sm.syllabus_id = lt.syllabus_id
JOIN syllabus_faculty sf ON sm.syllabus_id = sf.syllabus_id
JOIN faculty f ON sf.faculty_id = f.faculty_id
WHERE f.faculty_name LIKE '%数理%'
  AND sn.name LIKE '%情報基礎%'
ORDER BY sn.name, sm.syllabus_code, lt.day_of_week, lt.period;

-- JSONBキャッシュから数理の科目で科目名が「情報基礎」のデータを検索
SELECT 
    sc.subject_name_id,
    sc.cache_data->>'科目名' AS 科目名,
    sc.cache_data->'開講情報' AS 開講情報
FROM syllabus_cache sc
WHERE sc.cache_name = 'subject_syllabus_cache'
  AND sc.cache_data->>'科目名' LIKE '%情報基礎%'
  AND EXISTS (
    SELECT 1
    FROM jsonb_array_elements(sc.cache_data->'開講情報') AS opening_info
    CROSS JOIN jsonb_array_elements(opening_info->'シラバス') AS syllabus
    CROSS JOIN jsonb_array_elements_text(syllabus->'対象学部課程') AS faculty
    WHERE faculty LIKE '%数理%'
  )
ORDER BY sc.cache_data->>'科目名'; 