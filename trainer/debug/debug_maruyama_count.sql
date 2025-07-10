-- 丸山先生の科目数をmost_busy_teacherと同じ方法でカウント
SELECT
	教員->>'氏名' AS teacher_name,
	COUNT(DISTINCT cache_data->>'科目名') AS subject_count
FROM syllabus_cache
	JOIN LATERAL jsonb_array_elements(cache_data->'開講情報一覧') AS open ON TRUE
	JOIN LATERAL jsonb_array_elements(open->'シラバス一覧') AS syl ON TRUE
	JOIN LATERAL jsonb_array_elements(syl->'担当教員一覧') AS 教員 ON TRUE
WHERE cache_name = 'subject_syllabus_cache'
	AND 教員->>'役割' = '担当'
	AND 教員->>'氏名' IS NOT NULL
	AND 教員->>'氏名' != ''
	AND 教員->>'氏名' = '丸山 敦'
GROUP BY 教員->>'氏名'; 