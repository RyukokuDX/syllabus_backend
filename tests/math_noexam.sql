-- 数理の科目の選択必修科目のうち、試験がないものの教科名と担当教員の一覧
-- File Version: v1.1.0
-- Project Version: v2.2.3
-- Last Updated: 2025-07-02

SELECT DISTINCT
	cache_data->>'科目名' as 教科名,
	instructor->>'氏名' as 担当教員
FROM syllabus_cache
	CROSS JOIN LATERAL (
		SELECT opening_info
		FROM jsonb_array_elements(cache_data->'開講情報一覧') as opening_info
		WHERE jsonb_typeof(opening_info) = 'object'
	) as opening
	CROSS JOIN LATERAL (
		SELECT syllabus
		FROM jsonb_array_elements(opening.opening_info->'シラバス一覧') as syllabus
		WHERE jsonb_typeof(syllabus) = 'object'
	) as syl
	CROSS JOIN LATERAL (
		SELECT instructor
		FROM jsonb_array_elements(syl.syllabus->'担当教員一覧') as instructor
		WHERE jsonb_typeof(instructor) = 'object'
	) as instructor
WHERE cache_name = 'subject_syllabus_cache'
  -- 履修要綱で数理の必修科目
  AND EXISTS (
    SELECT 1
    FROM jsonb_array_elements(cache_data->'履修情報一覧') as curriculum_info,
         jsonb_array_elements(curriculum_info->'履修要綱一覧') as requirement_info
    WHERE requirement_info->>'学部課程' LIKE '%数理%'
      AND requirement_info->>'必須度' = '必修'
  )
  -- シラバスで数理の学部課程に開講
  AND EXISTS (
    SELECT 1
    FROM jsonb_array_elements(syl.syllabus->'対象学部課程一覧') as faculty
    WHERE faculty::text LIKE '%数理%'
  )
  AND (
    -- 成績評価基準一覧が空の場合（試験がない）
    jsonb_array_length(syl.syllabus->'成績評価基準一覧') = 0
    OR
    -- 成績評価基準一覧に「試験」を含む項目がない場合
    NOT EXISTS (
      SELECT 1 
      FROM jsonb_array_elements(syl.syllabus->'成績評価基準一覧') as criteria
      WHERE criteria->>'項目' LIKE '%試験%'
    )
  )
  -- 数学系の科目（科目区分または科目小区分に「数学」または「数理」を含む）
  AND EXISTS (
    SELECT 1
    FROM jsonb_array_elements(cache_data->'履修情報一覧') as curriculum_info,
         jsonb_array_elements(curriculum_info->'履修要綱一覧') as requirement_info
    WHERE (
      requirement_info->>'科目区分' LIKE '%数学%'
      OR requirement_info->>'科目区分' LIKE '%数理%'
      OR requirement_info->>'科目小区分' LIKE '%数学%'
      OR requirement_info->>'科目小区分' LIKE '%数理%'
    )
  )
ORDER BY 教科名, 担当教員;