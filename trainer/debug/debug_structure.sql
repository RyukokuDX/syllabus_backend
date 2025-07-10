-- データ構造確認用SQL
SELECT 
    cache_data->>'科目名' as subject_name,
    jsonb_array_length(cache_data->'履修情報一覧') as ri_count,
    cache_data->'履修情報一覧'->0 as first_ri
FROM syllabus_cache 
WHERE cache_name = 'subject_syllabus_cache' 
LIMIT 3; 