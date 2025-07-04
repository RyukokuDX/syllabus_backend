  -- すべての配列フィールドが実際に array 型か確認
SELECT key, jsonb_typeof(value)
FROM   syllabus_cache,
       jsonb_each(cache_data)
WHERE  key LIKE '%一覧'
  AND  jsonb_typeof(value) <> 'array';
