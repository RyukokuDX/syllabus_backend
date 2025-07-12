-- 開講情報一覧の構造確認
SELECT 
    cache_data->>'科目名' as subject_name,
    jsonb_array_length(cache_data->'開講情報一覧') as open_count,
    cache_data->'開講情報一覧'->0 as first_open
FROM syllabus_cache 
WHERE cache_name = 'subject_syllabus_cache' 
LIMIT 3; 