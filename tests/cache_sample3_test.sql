-- テスト1: 機械の専門応用科目を探す
SELECT
	cache_data->>'科目名' AS subject_name,
	cache_data->'履修情報' AS 履修情報
FROM syllabus_cache
WHERE cache_name = 'subject_syllabus_cache'
AND EXISTS (
	SELECT 1
	FROM jsonb_array_elements(cache_data->'履修情報') AS rj,
	     jsonb_array_elements(rj->'履修要綱') AS yk
	WHERE
		yk->>'科目区分' = '専門応用科目'
		AND yk->>'学部課程' LIKE '%電子%'
)
LIMIT 5; 