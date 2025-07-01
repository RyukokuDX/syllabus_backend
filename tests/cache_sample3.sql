SELECT
	subject_name,
	book_lateral.book->>'書名' AS 書籍名,
	book_lateral.book->>'値段' AS 値段
FROM (
	SELECT
		cache_data->>'科目名' AS subject_name,
		cache_data->'開講情報' AS 開講情報,
		cache_data->'履修情報' AS 履修情報
	FROM syllabus_cache
	WHERE cache_name = 'subject_syllabus_cache'
) t,
LATERAL (
	SELECT rj
	FROM jsonb_array_elements(履修情報) AS rj
	WHERE jsonb_typeof(履修情報) = 'array'
) rj_lateral,
LATERAL (
	SELECT yk
	FROM jsonb_array_elements(rj_lateral.rj->'履修要綱') AS yk
	WHERE jsonb_typeof(rj_lateral.rj->'履修要綱') = 'array'
) yk_lateral,
LATERAL (
	SELECT kj
	FROM jsonb_array_elements(開講情報) AS kj
	WHERE jsonb_typeof(開講情報) = 'array'
) kj_lateral,
LATERAL (
	SELECT syllabus
	FROM jsonb_array_elements((kj_lateral.kj->'シラバス')) AS syllabus
	WHERE jsonb_typeof(kj_lateral.kj->'シラバス') = 'array'
) syllabus_lateral,
LATERAL (
	SELECT book
	FROM jsonb_array_elements((syllabus_lateral.syllabus->'参考書')) AS book
	WHERE jsonb_typeof(syllabus_lateral.syllabus->'参考書') = 'array'
	AND (book->>'値段') ~ '^[0-9]+$'
	AND (book->>'値段')::int >= 3000
) book_lateral
WHERE yk_lateral.yk->>'学部課程' LIKE '%電子%';