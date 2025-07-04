-- File Version: v1.0.2
-- Project Version: v2.5.0
-- Last Updated: 2025-07-03

-- 数理の専門応用科目のうち、成績評価基準一覧に「レポート」を含まないものを抽出
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