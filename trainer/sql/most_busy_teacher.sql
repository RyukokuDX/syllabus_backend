-- ---
-- order: 最も多くの講義を担当している先生を教えて
-- desc: 担当教員一覧から、最も多くの科目を担当している教員の氏名と担当科目数を一覧で取得する（ガイドライン準拠）。
-- author: 藤原和将
-- file_version: v3.0.1
-- project_version: v3.0.2
-- last_updated: 2025-07-09
-- response_id: most_busy_teacher.json
-- ---

SELECT
	教員->>'氏名' AS teacher_name,
	COUNT(DISTINCT cache_data->>'科目名') AS subject_count
FROM syllabus_cache
	JOIN LATERAL jsonb_array_elements(cache_data->'履修情報一覧') AS ri ON TRUE
	JOIN LATERAL jsonb_array_elements(ri->'履修要綱一覧') AS r ON TRUE
	JOIN LATERAL jsonb_array_elements(cache_data->'開講情報一覧') AS open ON TRUE
	JOIN LATERAL jsonb_array_elements(open->'シラバス一覧') AS syl ON TRUE
	JOIN LATERAL jsonb_array_elements(syl->'担当教員一覧') AS 教員 ON TRUE
WHERE cache_name = 'subject_syllabus_cache'
	AND 教員->>'役割' = '担当'
	AND 教員->>'氏名' IS NOT NULL
	AND 教員->>'氏名' != ''
GROUP BY 教員->>'氏名'
ORDER BY subject_count DESC, teacher_name
LIMIT 5; 