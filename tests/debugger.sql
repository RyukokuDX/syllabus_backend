SELECT COUNT(*) AS not_array_count
FROM syllabus_cache
WHERE cache_name = 'subject_syllabus_cache'
  AND (
    jsonb_typeof(cache_data->'開講情報一覧') IS DISTINCT FROM 'array'
    OR jsonb_typeof(cache_data->'開講情報一覧'->0->'シラバス一覧') IS DISTINCT FROM 'array'
    OR jsonb_typeof(cache_data->'開講情報一覧'->0->'シラバス一覧'->0->'担当教員一覧') IS DISTINCT FROM 'array'
  );