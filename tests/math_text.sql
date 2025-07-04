-- File Version: v1.0.0
-- Project Version: v2.5.2
-- Last Updated: 2025-07-04
SELECT DISTINCT
  書名,
  著者,
  出版社,
  価格,
  NULL AS 総額
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
    AND (requirement_info->>'専門応用履修要件' = '数学系')
    AND (requirement_info->>'学部課程' = '数理·情報科学課程')
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
;

-- 価格合計（数値変換できるもののみ）
SELECT SUM(価格::integer) AS 価格合計
FROM (
	SELECT DISTINCT
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
		AND (requirement_info->>'専門応用履修要件' = '数学系')
		AND (requirement_info->>'学部課程' = '数理·情報科学課程')
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