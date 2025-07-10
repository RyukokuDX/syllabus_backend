-- ---
-- order: 科目名に「結晶学入門」を含む全レコードの詳細をJSON形式で抽出する
-- desc: 科目名に「結晶学入門」を含む科目のcache_data全体をJSON形式で一覧で取得する（サンプル準拠）。
-- author: 藤原和将
-- file_version: v3.0.1
-- project_version: v3.0.2
-- last_updated: 2025-07-09
-- response_id: kessyou_kougaku_full.json
-- ---

SELECT
	jsonb_pretty(cache_data) AS result
FROM syllabus_cache
WHERE cache_name = 'subject_syllabus_cache'
	AND cache_data->>'科目名' LIKE '%結晶学入門%'
ORDER BY cache_data->>'科目名'; 