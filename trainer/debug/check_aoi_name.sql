-- 青井先生の名前表記を確認するデバッグクエリ
SELECT DISTINCT
	教員->>'氏名' AS teacher_name,
	COUNT(*) AS count
FROM syllabus_cache
	JOIN LATERAL jsonb_array_elements(cache_data->'履修情報一覧') AS ri ON TRUE
	JOIN LATERAL jsonb_array_elements(ri->'履修要綱一覧') AS r ON TRUE
	JOIN LATERAL jsonb_array_elements(cache_data->'開講情報一覧') AS open ON TRUE
	JOIN LATERAL jsonb_array_elements(open->'シラバス一覧') AS syl ON TRUE
	JOIN LATERAL jsonb_array_elements(syl->'担当教員一覧') AS 教員 ON TRUE
WHERE cache_name = 'subject_syllabus_cache'
	AND open->>'年度' = '2025'
	AND 教員->>'役割' = '担当'
	AND (教員->>'氏名' LIKE '%青井%' OR 教員->>'氏名' LIKE '%あおい%' OR 教員->>'氏名' LIKE '%AOI%')
GROUP BY 教員->>'氏名'
ORDER BY teacher_name; 