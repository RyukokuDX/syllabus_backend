-- ---
-- order: 「特別研究」という科目名のレコードJSONをすべて書き出す
-- desc: syllabus_cacheから科目名が「特別研究」のレコードを抽出し、JSON形式で出力する
-- author: cursor
-- file_version: v1.0.0
-- project_version: v3.0.6
-- last_updated: 2025-07-10
-- response_id: check_tokubetu_kenkyu.json
-- ---

SELECT
	cache_data->>'科目名' AS subject_name,
	jsonb_pretty(cache_data) AS full_json
FROM syllabus_cache
WHERE cache_name = 'subject_syllabus_cache'
	AND cache_data->>'科目名' = '特別研究'
ORDER BY cache_data->>'科目名'; 