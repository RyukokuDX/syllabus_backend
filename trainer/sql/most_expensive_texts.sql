-- ---
-- order: 課程別に最も高い教科書のリストを作成する
-- desc: 各課程で最も高い教科書の科目名、課程、教科書名、価格を一覧で取得する（ガイドライン準拠）。
-- author: 藤原和将
-- file_version: v3.0.1
-- project_version: v3.0.2
-- last_updated: 2025-07-09
-- response_id: most_expensive_texts.json
-- ---

WITH course_textbooks AS (
	SELECT DISTINCT
		cache_data->>'科目名' AS subject_name,
		課程,
		COALESCE(textbook->>'書名', '未設定') AS textbook_name,
		CAST(textbook->>'価格' AS INTEGER) AS price
	FROM syllabus_cache
		JOIN LATERAL jsonb_array_elements(cache_data->'履修情報一覧') AS ri ON TRUE
		JOIN LATERAL jsonb_array_elements(ri->'履修要綱一覧') AS r ON TRUE
		JOIN LATERAL jsonb_array_elements(cache_data->'開講情報一覧') AS open ON TRUE
		JOIN LATERAL jsonb_array_elements(open->'シラバス一覧') AS syl ON TRUE
		JOIN LATERAL jsonb_array_elements_text(syl->'対象学部課程一覧') AS 課程 ON TRUE
		JOIN LATERAL jsonb_array_elements(syl->'教科書一覧') AS textbook ON TRUE
	WHERE cache_name = 'subject_syllabus_cache'
		AND textbook->>'価格' IS NOT NULL
		AND textbook->>'価格' != ''
),
ranked_textbooks AS (
	SELECT 
		subject_name,
		課程,
		textbook_name,
		price,
		ROW_NUMBER() OVER (PARTITION BY 課程 ORDER BY price DESC) AS rank
	FROM course_textbooks
)
SELECT 
	subject_name,
	課程,
	textbook_name,
	price
FROM ranked_textbooks
WHERE rank = 1
ORDER BY 課程, price DESC; 