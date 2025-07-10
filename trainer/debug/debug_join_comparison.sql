-- JOINの有無による違いを比較
-- 1. 履修情報一覧をJOINしない場合（most_busy_teacherと同じ）
SELECT 'JOINなし' as method, COUNT(DISTINCT cache_data->>'科目名') AS subject_count
FROM syllabus_cache
	JOIN LATERAL jsonb_array_elements(cache_data->'開講情報一覧') AS open ON TRUE
	JOIN LATERAL jsonb_array_elements(open->'シラバス一覧') AS syl ON TRUE
	JOIN LATERAL jsonb_array_elements(syl->'担当教員一覧') AS 教員 ON TRUE
WHERE cache_name = 'subject_syllabus_cache'
	AND 教員->>'氏名' = '丸山 敦'
	AND 教員->>'役割' = '担当'

UNION ALL

-- 2. 履修情報一覧をJOINする場合（maruyama系と同じ）
SELECT 'JOINあり' as method, COUNT(DISTINCT cache_data->>'科目名') AS subject_count
FROM syllabus_cache
	JOIN LATERAL jsonb_array_elements(cache_data->'履修情報一覧') AS ri ON TRUE
	JOIN LATERAL jsonb_array_elements(ri->'履修要綱一覧') AS r ON TRUE
	JOIN LATERAL jsonb_array_elements(cache_data->'開講情報一覧') AS open ON TRUE
	JOIN LATERAL jsonb_array_elements(open->'シラバス一覧') AS syl ON TRUE
	JOIN LATERAL jsonb_array_elements(syl->'担当教員一覧') AS 教員 ON TRUE
WHERE cache_name = 'subject_syllabus_cache'
	AND 教員->>'氏名' = '丸山 敦'
	AND 教員->>'役割' = '担当'; 