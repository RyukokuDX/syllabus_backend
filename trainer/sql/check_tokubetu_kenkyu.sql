-- 特別研究のレコードJSONをすべて書き出す
SELECT
	cache_data->>'科目名' AS subject_name,
	jsonb_pretty(cache_data) AS full_json
FROM syllabus_cache
WHERE cache_name = 'subject_syllabus_cache'
	AND cache_data->>'科目名' = '特別研究'
ORDER BY cache_data->>'科目名'; 