-- 丸山先生の全担当科目を確認
SELECT
	cache_data->>'科目名' AS subject_name,
	r->>'科目小区分' AS subject_type,
	open->>'年度' AS year
FROM syllabus_cache
	JOIN LATERAL jsonb_array_elements(cache_data->'履修情報一覧') AS ri ON TRUE
	JOIN LATERAL jsonb_array_elements(ri->'履修要綱一覧') AS r ON TRUE
	JOIN LATERAL jsonb_array_elements(cache_data->'開講情報一覧') AS open ON TRUE
	JOIN LATERAL jsonb_array_elements(open->'シラバス一覧') AS syl ON TRUE
	JOIN LATERAL jsonb_array_elements(syl->'担当教員一覧') AS 教員 ON TRUE
WHERE cache_name = 'subject_syllabus_cache'
	AND 教員->>'氏名' = '丸山 敦'
	AND 教員->>'役割' = '担当'
ORDER BY subject_name, year, subject_type; 