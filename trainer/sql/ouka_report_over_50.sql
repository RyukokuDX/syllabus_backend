-- ---
-- order: 応用化学の専攻科目の選択科目で、レポートの評価割合が50%以上の科目名と教員名、レポート評価の割合の一覧を取得
-- desc: 応用化学の専攻科目の選択科目で、成績評価基準に「レポート」が含まれ、その割合が50%以上の科目の科目名、担当教員、レポート評価割合を一覧で取得する（ガイドライン準拠）。
-- author: 藤原和将
-- file_version: v1.0.2
-- project_version: v3.0.2
-- last_updated: 2025-07-09
-- response_id: ouka_report_over_50.json
-- ---

SELECT
	cache_data->>'科目名' AS subject_name,
	COALESCE(
		(SELECT string_agg(教員->>'氏名', ', ' ORDER BY 教員->>'氏名')
		FROM jsonb_array_elements(syl->'担当教員一覧') AS 教員
		WHERE 教員->>'役割' = '担当'
		), '未定'
	) AS instructors,
	SUM((g->>'割合')::integer) AS report_ratio
FROM syllabus_cache
	JOIN LATERAL jsonb_array_elements(cache_data->'履修情報一覧') AS ri ON TRUE
	JOIN LATERAL jsonb_array_elements(ri->'履修要綱一覧') AS r ON TRUE
	JOIN LATERAL jsonb_array_elements(cache_data->'開講情報一覧') AS open ON TRUE
	JOIN LATERAL jsonb_array_elements(open->'シラバス一覧') AS syl ON TRUE
	JOIN LATERAL jsonb_array_elements(syl->'成績評価基準一覧') AS g ON TRUE
WHERE cache_name = 'subject_syllabus_cache'
	AND r->>'学部課程' = '応用化学課程'
	AND r->>'科目区分' = '専攻科目'
	AND r->>'必須度' = '選択'
	AND syl->'対象学部課程一覧' @> '["応用化学課程"]'
	AND g->>'項目' LIKE '%レポート%'
GROUP BY cache_data->>'科目名', syl
HAVING SUM((g->>'割合')::integer) >= 50
ORDER BY report_ratio DESC, subject_name; 