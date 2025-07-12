-- ---
-- order: 知能の専門応用科目で使用する教科書の冊数と総額を取得
-- desc: 知能の専門応用科目で使用されている教科書の冊数と総額を集計し、カラム名付きオブジェクト配列（例：[{"textbook_count": 0, "total_textbook_price": 0}]）形式のJSONで出力する（ガイドライン準拠）。
-- author: 藤原和将
-- file_version: v2.5.2
-- project_version: v2.5.2
-- last_updated: 2025-07-09
-- response_id: chinou_book.json
-- ---

SELECT
	COUNT(DISTINCT 教科書->>'書名') AS textbook_count,
	COALESCE(SUM((教科書->>'価格')::integer), 0) AS total_textbook_price
FROM syllabus_cache
	JOIN LATERAL jsonb_array_elements(cache_data->'履修情報一覧') AS ri ON TRUE
	JOIN LATERAL jsonb_array_elements(ri->'履修要綱一覧') AS r ON TRUE
	JOIN LATERAL jsonb_array_elements(cache_data->'開講情報一覧') AS open ON TRUE
	JOIN LATERAL jsonb_array_elements(open->'シラバス一覧') AS syl ON TRUE
	JOIN LATERAL jsonb_array_elements(syl->'教科書一覧') AS 教科書 ON TRUE
WHERE cache_name = 'subject_syllabus_cache'
	AND r->>'学部課程' LIKE '%知能%'
	AND r->>'科目小区分' = '専門応用科目'
	AND 教科書->>'価格' ~ '^[0-9]+$'; 