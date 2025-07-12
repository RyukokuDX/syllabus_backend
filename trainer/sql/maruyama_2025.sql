-- ---
-- order: 丸山先生の2025年の専門応用科目の担当科目一覧を科目名と対象課程のリストの形で表示する
-- desc: 丸山先生が2025年に担当する専門応用科目の科目名と対象学部課程一覧を一覧で取得する（ガイドライン準拠）。
-- author: 藤原和将
-- file_version: v3.0.1
-- project_version: v3.0.2
-- last_updated: 2025-07-09
-- response_id: maruyama_2025.json
-- ---

SELECT DISTINCT
	cache_data->>'科目名' AS subject_name,
	COALESCE(
		(SELECT string_agg(課程, ', ' ORDER BY 課程)
		FROM jsonb_array_elements_text(syl->'対象学部課程一覧') AS 課程
		), '未設定'
	) AS target_courses
FROM syllabus_cache
	JOIN LATERAL jsonb_array_elements(cache_data->'履修情報一覧') AS ri ON TRUE
	JOIN LATERAL jsonb_array_elements(ri->'履修要綱一覧') AS r ON TRUE
	JOIN LATERAL jsonb_array_elements(cache_data->'開講情報一覧') AS open ON TRUE
	JOIN LATERAL jsonb_array_elements(open->'シラバス一覧') AS syl ON TRUE
	JOIN LATERAL jsonb_array_elements(syl->'担当教員一覧') AS 教員 ON TRUE
WHERE cache_name = 'subject_syllabus_cache'
	AND open->>'年度' = '2025'
	AND r->>'科目小区分' = '専門応用科目'
	AND 教員->>'氏名' = '丸山 敦'
	AND 教員->>'役割' = '担当'
ORDER BY subject_name; 