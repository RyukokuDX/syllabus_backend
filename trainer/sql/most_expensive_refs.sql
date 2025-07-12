-- ---
-- order: 課程別に最も高い参考書のリストを作成する
-- desc: 各課程で最も高い参考書の科目名、課程、参考書名、価格を一覧で取得する（ガイドライン準拠）。
-- author: 藤原和将
-- file_version: v3.0.1
-- project_version: v3.0.2
-- last_updated: 2025-07-09
-- response_id: most_expensive_refs.json
-- ---

WITH course_refs AS (
	SELECT DISTINCT
		cache_data->>'科目名' AS subject_name,
		課程,
		COALESCE(refbook->>'書名', '未設定') AS refbook_name,
		CAST(refbook->>'価格' AS INTEGER) AS price
	FROM syllabus_cache
		JOIN LATERAL jsonb_array_elements(cache_data->'履修情報一覧') AS ri ON TRUE
		JOIN LATERAL jsonb_array_elements(ri->'履修要綱一覧') AS r ON TRUE
		JOIN LATERAL jsonb_array_elements(cache_data->'開講情報一覧') AS open ON TRUE
		JOIN LATERAL jsonb_array_elements(open->'シラバス一覧') AS syl ON TRUE
		JOIN LATERAL jsonb_array_elements_text(syl->'対象学部課程一覧') AS 課程 ON TRUE
		JOIN LATERAL jsonb_array_elements(syl->'参考書一覧') AS refbook ON TRUE
	WHERE cache_name = 'subject_syllabus_cache'
		AND refbook->>'価格' IS NOT NULL
		AND refbook->>'価格' != ''
),
ranked_refs AS (
	SELECT 
		subject_name,
		課程,
		refbook_name,
		price,
		ROW_NUMBER() OVER (PARTITION BY 課程 ORDER BY price DESC) AS rank
	FROM course_refs
)
SELECT 
	subject_name,
	課程,
	refbook_name,
	price
FROM ranked_refs
WHERE rank = 1
ORDER BY 課程, price DESC; 