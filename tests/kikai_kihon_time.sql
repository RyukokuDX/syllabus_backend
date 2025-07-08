-- 機械工学·ロボティクス課程の専門基礎科目で、1,2限のものの科目名の一覧（jsonb_cache.md準拠）
-- File Version: v2.0.0
-- Project Version: v2.5.4
-- Last Updated: 2025-07-05

SELECT DISTINCT
	cache_data->>'科目名' AS 科目名
FROM syllabus_cache
WHERE cache_name = 'subject_syllabus_cache'
  -- 履修情報一覧→履修要綱一覧→科目小区分 = '専門基礎科目'
  AND EXISTS (
    SELECT 1
    FROM jsonb_array_elements(cache_data->'履修情報一覧') AS curriculum_info,
         jsonb_array_elements(curriculum_info->'履修要綱一覧') AS requirement_info
    WHERE requirement_info->>'科目小区分' = '専門基礎科目'
  )
  -- 開講情報一覧→シラバス一覧→対象学部課程一覧に'機械工学·ロボティクス課程'を含み、同じシラバスの講義時間一覧に時限1,2が含まれる
  AND EXISTS (
    SELECT 1
    FROM jsonb_array_elements(cache_data->'開講情報一覧') AS opening_info,
         jsonb_array_elements(opening_info->'シラバス一覧') AS syllabus
    WHERE EXISTS (
      SELECT 1
      FROM jsonb_array_elements(syllabus->'対象学部課程一覧') AS faculty
      WHERE faculty::text LIKE '%機械工学·ロボティクス課程%'
    )
    AND EXISTS (
      SELECT 1
      FROM jsonb_array_elements(syllabus->'講義時間一覧') AS time
      WHERE (time->>'時限')::int IN (1,2)
    )
  )
ORDER BY 科目名; 