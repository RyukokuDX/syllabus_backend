-- 重複科目をシンプルに調査
SELECT
	cache_data->>'科目名' AS subject_name,
	open->>'年度' AS year,
	r->>'科目小区分' AS subject_type
FROM syllabus_cache
	JOIN LATERAL jsonb_array_elements(cache_data->'履修情報一覧') AS ri ON TRUE
	JOIN LATERAL jsonb_array_elements(ri->'履修要綱一覧') AS r ON TRUE
	JOIN LATERAL jsonb_array_elements(cache_data->'開講情報一覧') AS open ON TRUE
	JOIN LATERAL jsonb_array_elements(open->'シラバス一覧') AS syl ON TRUE
	JOIN LATERAL jsonb_array_elements(syl->'担当教員一覧') AS 教員 ON TRUE
WHERE cache_name = 'subject_syllabus_cache'
	AND 教員->>'氏名' = '丸山 敦'
	AND 教員->>'役割' = '担当'
	AND cache_data->>'科目名' IN ('情報基礎', '特別研究')
ORDER BY cache_data->>'科目名', open->>'年度', r->>'科目小区分'; 