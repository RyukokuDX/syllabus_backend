-- 知能の専門応用科目で使用する教科書の冊数と総額（@math_text.sql準拠・修正版）
SELECT 
	COUNT(DISTINCT 書名) AS textbook_count,
	COALESCE(SUM(価格::integer), 0) AS total_textbook_price
FROM (
	SELECT
		教科書->>'書名' AS 書名,
		教科書->>'著者' AS 著者,
		教科書->>'出版社' AS 出版社,
		教科書->>'価格' AS 価格
	FROM syllabus_cache
	CROSS JOIN LATERAL (
		SELECT curriculum_info
		FROM jsonb_array_elements(cache_data->'履修情報一覧') AS curriculum_info
		WHERE jsonb_typeof(curriculum_info) = 'object'
	) AS cur
	CROSS JOIN LATERAL (
		SELECT requirement_info
		FROM jsonb_array_elements(cur.curriculum_info->'履修要綱一覧') AS requirement_info
		WHERE jsonb_typeof(requirement_info) = 'object'
			AND (requirement_info->>'科目小区分' = '専門応用科目')
			AND (requirement_info->>'学部課程' LIKE '%知能%')
	) AS req
	CROSS JOIN LATERAL (
		SELECT open_info
		FROM jsonb_array_elements(cache_data->'開講情報一覧') AS open_info
		WHERE jsonb_typeof(open_info) = 'object'
	) AS open
	CROSS JOIN LATERAL (
		SELECT syl_info
		FROM jsonb_array_elements(open.open_info->'シラバス一覧') AS syl_info
		WHERE jsonb_typeof(syl_info) = 'object'
	) AS syl
	CROSS JOIN LATERAL (
		SELECT 教科書
		FROM jsonb_array_elements(syl.syl_info->'教科書一覧') AS 教科書
		WHERE jsonb_typeof(教科書) = 'object'
	) AS 教科書
	WHERE cache_name = 'subject_syllabus_cache'
) t
WHERE 価格 ~ '^[0-9]+$'; 