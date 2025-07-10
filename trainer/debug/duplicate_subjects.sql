-- 科目名が重複する原因を調査
-- 丸山先生の科目で重複を詳しく確認
SELECT
	cache_data->>'科目名' AS subject_name,
	COUNT(*) as duplicate_count,
	jsonb_agg(DISTINCT open->>'年度') as years,
	jsonb_agg(DISTINCT r->>'科目小区分') as subject_types,
	jsonb_agg(DISTINCT syl->'対象学部課程一覧') as target_courses
FROM syllabus_cache
	JOIN LATERAL jsonb_array_elements(cache_data->'履修情報一覧') AS ri ON TRUE
	JOIN LATERAL jsonb_array_elements(ri->'履修要綱一覧') AS r ON TRUE
	JOIN LATERAL jsonb_array_elements(cache_data->'開講情報一覧') AS open ON TRUE
	JOIN LATERAL jsonb_array_elements(open->'シラバス一覧') AS syl ON TRUE
	JOIN LATERAL jsonb_array_elements(syl->'担当教員一覧') AS 教員 ON TRUE
WHERE cache_name = 'subject_syllabus_cache'
	AND 教員->>'氏名' = '丸山 敦'
	AND 教員->>'役割' = '担当'
GROUP BY cache_data->>'科目名'
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC, subject_name; 