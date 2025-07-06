-- 機械工学·ロボティクス課程の科目で使用する教科書の一覧と総額
-- File Version: v2.5.0
-- Project Version: v2.5.4
-- Last Updated: 2025-07-05

-- 教科書一覧（書名・著者・出版社が同じ場合は1冊のみ表示）
SELECT 書名, 著者, 出版社, MIN(価格) AS 価格
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
			AND requirement_info->>'学部課程' = '機械工学·ロボティクス課程'
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
GROUP BY 書名, 著者, 出版社
ORDER BY 書名;

-- 教科書総額
SELECT
	COALESCE(SUM((教科書->>'価格')::integer), 0) AS 教科書総額
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
		AND requirement_info->>'学部課程' = '機械工学·ロボティクス課程'
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
  AND 教科書->>'価格' ~ '^[0-9]+$'; 