-- 電子の科目で、教科書の料金が2000円以下（教科書なしも含む）、かつ選択科目の一覧
-- File Version: v1.0.0
-- Project Version: v2.2.3
-- Last Updated: 2025-07-02

SELECT DISTINCT
	cache_data->>'科目名' as 教科名,
	instructor->>'氏名' as 担当教員,
	book->>'書名' as 教科書名,
	book->>'価格' as 教科書価格
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
	LEFT JOIN LATERAL (
		SELECT book
		FROM jsonb_array_elements(syl.syllabus->'教科書一覧') as book
		WHERE jsonb_typeof(book) = 'object'
		LIMIT 1
	) as book ON TRUE
WHERE cache_name = 'subject_syllabus_cache'
  -- 履修要綱で電子の選択科目
  AND EXISTS (
    SELECT 1
    FROM jsonb_array_elements(cache_data->'履修情報一覧') as curriculum_info,
         jsonb_array_elements(curriculum_info->'履修要綱一覧') as requirement_info
    WHERE requirement_info->>'学部課程' LIKE '%電子%'
      AND requirement_info->>'必須度' = '選択'
  )
  -- 教科書が2000円以下または教科書が存在しない場合
  AND (
    book->>'価格' IS NULL
    OR
    (book->>'価格')::int <= 2000
  )
ORDER BY 教科名, 担当教員; 