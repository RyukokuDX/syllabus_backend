-- キャッシュデータの構造を詳しく確認
SELECT 
	cache_data->>'科目名' AS subject_name,
	jsonb_typeof(cache_data->'開講情報') AS 開講情報_type,
	jsonb_typeof(cache_data->'履修情報') AS 履修情報_type,
	jsonb_typeof((cache_data->'開講情報'->0)) AS 開講情報要素_type,
	jsonb_typeof((cache_data->'履修情報'->0)) AS 履修情報要素_type,
	jsonb_typeof((cache_data->'履修情報'->0->'履修要綱')) AS 履修要綱_type,
	cache_data->'開講情報'->0 AS 開講情報要素_sample,
	cache_data->'履修情報'->0 AS 履修情報要素_sample
FROM syllabus_cache 
WHERE cache_name = 'subject_syllabus_cache' 
LIMIT 1; 