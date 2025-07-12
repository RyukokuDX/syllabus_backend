-- ---
-- order: 2025年度の知能情報メディア課程で教科書が指定されていない科目名一覧を取得
-- desc: 2025年度、知能情報メディア課程において、開講情報の教科書一覧が空配列またはnullの科目名を抽出する
-- author: cursor
-- file_version: v1.0.0
-- project_version: v3.0.6
-- last_updated: 2025-07-10
-- response_id: no_textbook_2025_chinou.json
-- ---

SELECT
	cache_data->>'科目名' AS 科目名
FROM
	syllabus_cache
WHERE
	cache_name = 'subject_syllabus_cache'
	AND EXISTS (
		SELECT 1
		FROM jsonb_array_elements(cache_data->'履修情報一覧') AS r
		JOIN LATERAL jsonb_array_elements(r->'履修要綱一覧') AS y ON TRUE
		WHERE y->>'学部課程' = '知能情報メディア課程'
			AND r->>'年度' = '2025'
	)
	AND EXISTS (
		SELECT 1
		FROM jsonb_array_elements(cache_data->'開講情報一覧') AS k
		JOIN LATERAL jsonb_array_elements(k->'シラバス一覧') AS s ON TRUE
		WHERE k->>'年度' = '2025'
			AND (
				s->'教科書一覧' IS NULL
				OR jsonb_typeof(s->'教科書一覧') = 'array' AND jsonb_array_length(s->'教科書一覧') = 0
			)
	)
; 