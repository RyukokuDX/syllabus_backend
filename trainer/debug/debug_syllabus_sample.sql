SELECT
	cache_data->>'科目名' as subject_name,
	syl
FROM syllabus_cache
	JOIN LATERAL jsonb_array_elements(cache_data->'開講情報一覧') AS open ON TRUE
	JOIN LATERAL jsonb_array_elements(open->'シラバス一覧') AS syl ON TRUE
WHERE cache_name = 'subject_syllabus_cache'
	AND syl->'対象学部課程一覧' @> '["機械工学·ロボティクス課程"]'
LIMIT 5; 