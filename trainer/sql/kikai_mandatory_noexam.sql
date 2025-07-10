-- ---
-- order: 機械の必修科目のうち、期末試験がない科目の科目名一覧を取得
-- desc: 機械の必修科目で、成績評価基準に「期末試験」が含まれない科目名を一覧で取得する（ガイドライン準拠）。
-- author: 藤原和将
-- file_version: v3.0.1
-- project_version: v3.0.2
-- last_updated: 2025-07-09
-- response_id: kikai_mandatory_noexam.json
-- ---

SELECT
	cache_data->>'科目名' AS subject_name,
	r->>'必須度' AS mandatory_level,
	COALESCE(
		(SELECT string_agg(教員->>'氏名', ', ' ORDER BY 教員->>'氏名')
		FROM jsonb_array_elements(syl->'担当教員一覧') AS 教員
		WHERE 教員->>'役割' = '担当'
		), '未定'
	) AS instructors
FROM syllabus_cache
	JOIN LATERAL jsonb_array_elements(cache_data->'履修情報一覧') AS ri ON TRUE
	JOIN LATERAL jsonb_array_elements(ri->'履修要綱一覧') AS r ON TRUE
	JOIN LATERAL jsonb_array_elements(cache_data->'開講情報一覧') AS open ON TRUE
	JOIN LATERAL jsonb_array_elements(open->'シラバス一覧') AS syl ON TRUE
WHERE cache_name = 'subject_syllabus_cache'
	AND r->>'学部課程' LIKE '%機械%'
	AND r->>'必須度' = '必修'
	AND syl->'対象学部課程一覧' @> '["機械工学·ロボティクス課程"]'
	AND NOT EXISTS (
		SELECT 1
		FROM jsonb_array_elements(syl->'成績評価基準一覧') AS g
		WHERE g->>'項目' LIKE '%期末試験%'
	)
ORDER BY subject_name; 