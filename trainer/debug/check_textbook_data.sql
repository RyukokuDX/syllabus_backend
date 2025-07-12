-- 教科書データの状況を確認するデバッグクエリ
SELECT 
	COUNT(*) AS total_subjects,
	COUNT(CASE WHEN syl->'教科書一覧' IS NOT NULL THEN 1 END) AS subjects_with_textbooks,
	COUNT(CASE WHEN textbook->>'価格' IS NOT NULL AND textbook->>'価格' != '' THEN 1 END) AS textbooks_with_price,
	COUNT(CASE WHEN textbook->>'教科書名' IS NOT NULL AND textbook->>'教科書名' != '' THEN 1 END) AS textbooks_with_name
FROM syllabus_cache
	JOIN LATERAL jsonb_array_elements(cache_data->'履修情報一覧') AS ri ON TRUE
	JOIN LATERAL jsonb_array_elements(ri->'履修要綱一覧') AS r ON TRUE
	JOIN LATERAL jsonb_array_elements(cache_data->'開講情報一覧') AS open ON TRUE
	JOIN LATERAL jsonb_array_elements(open->'シラバス一覧') AS syl ON TRUE
	LEFT JOIN LATERAL jsonb_array_elements(syl->'教科書一覧') AS textbook ON TRUE
WHERE cache_name = 'subject_syllabus_cache'; 