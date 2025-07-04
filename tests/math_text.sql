SELECT DISTINCT
	cache_data->>'科目名' AS 科目名,
	curriculum_info AS 履修情報,
	requirement_info AS 履修要綱
FROM syllabus_cache
	CROSS JOIN LATERAL (
		SELECT curriculum_info
		FROM jsonb_array_elements(cache_data->'履修情報一覧') AS curriculum_info
		WHERE jsonb_typeof(curriculum_info) = 'object'
	) AS cur
	CROSS JOIN LATERAL (
		SELECT requirement_info
		FROM jsonb_array_elements(cur.curriculum_info->'履修要綱一覧') AS requirement_info
		WHERE jsonb_typeof(requirement_info) = 'object'
	) AS req
WHERE cache_name = 'subject_syllabus_cache'
  AND (
    requirement_info->>'専門応用履修要件' = '数学系'
  )
ORDER BY 科目名;