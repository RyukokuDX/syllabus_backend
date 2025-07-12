-- ---
-- order: 数理の専門応用科目のうち、成績評価基準一覧に「レポート」を含まないものを抽出
-- desc: 数理の専門応用科目で、成績評価基準に「レポート」が含まれない科目名を一覧で取得する。出力は必ずカラム名付きオブジェクト配列（例：[{"subject_name": "..."}, ...]）形式のJSONとする（ガイドライン準拠）。
-- author: 藤原和将
-- file_version: v2.5.2
-- project_version: v2.5.2
-- last_updated: 2025-07-09
-- response_id: math_noreport.json
-- ---

SELECT
	cache_data->>'科目名' AS subject_name
FROM syllabus_cache
WHERE cache_name = 'subject_syllabus_cache'
	AND EXISTS (
		SELECT 1
		FROM jsonb_array_elements(cache_data->'履修情報一覧') AS ri
		CROSS JOIN LATERAL jsonb_array_elements(ri->'履修要綱一覧') AS r
		WHERE r->>'学部課程' LIKE '%数理%'
			AND r->>'科目小区分' = '専門応用科目'
	)
	AND NOT EXISTS (
		SELECT 1
		FROM jsonb_array_elements(cache_data->'開講情報一覧') AS open
		CROSS JOIN LATERAL jsonb_array_elements(open->'シラバス一覧') AS syl
		CROSS JOIN LATERAL jsonb_array_elements(syl->'成績評価基準一覧') AS g
		WHERE g->>'項目' LIKE '%レポート%'
	)
ORDER BY subject_name; 