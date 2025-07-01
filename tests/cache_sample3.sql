SELECT
	subject_name,
	開講情報,
	履修情報
FROM (
	SELECT
		cache_data->>'科目名' AS subject_name,
		cache_data->'開講情報' AS 開講情報,
		cache_data->'履修情報' AS 履修情報
	FROM syllabus_cache
	WHERE cache_name = 'subject_syllabus_cache'
)
WHERE EXISTS (
	SELECT 1
	FROM jsonb_array_elements(履修情報) AS rj,
	     jsonb_array_elements(rj->'履修要綱') AS yk
	WHERE
		yk->>'学部課程' LIKE '%電子%'
);