-- File Version: v1.0.0
-- Project Version: v3.0.0
-- Last Updated: 2025-07-08
-- 指定した科目名でsubject_syllabus_cacheから情報を検索

SELECT *
FROM syllabus_cache
WHERE cache_name = 'subject_syllabus_cache'
  AND cache_data->>'科目名' = 'CGとVR'; 