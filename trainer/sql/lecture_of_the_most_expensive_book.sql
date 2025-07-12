-- ---
-- order: 登録されている最も高い本を利用している科目情報を抽出する
-- desc: 全教科書・参考書の中で最も高い価格の本を使用している科目の詳細情報を一覧で取得する（ガイドライン準拠）。
-- author: 藤原和将
-- file_version: v3.0.1
-- project_version: v3.0.2
-- last_updated: 2025-07-09
-- response_id: lecture_of_the_most_expensive_book.json
-- ---

WITH all_books AS (
	SELECT DISTINCT
		cache_data->>'科目名' AS subject_name,
		'教科書' AS book_type,
		COALESCE(textbook->>'書名', '未設定') AS book_name,
		CAST(textbook->>'価格' AS INTEGER) AS price,
		textbook->>'著者' AS author,
		textbook->>'ISBN' AS isbn
	FROM syllabus_cache
		JOIN LATERAL jsonb_array_elements(cache_data->'履修情報一覧') AS ri ON TRUE
		JOIN LATERAL jsonb_array_elements(ri->'履修要綱一覧') AS r ON TRUE
		JOIN LATERAL jsonb_array_elements(cache_data->'開講情報一覧') AS open ON TRUE
		JOIN LATERAL jsonb_array_elements(open->'シラバス一覧') AS syl ON TRUE
		JOIN LATERAL jsonb_array_elements(syl->'教科書一覧') AS textbook ON TRUE
	WHERE cache_name = 'subject_syllabus_cache'
		AND textbook->>'価格' IS NOT NULL
		AND textbook->>'価格' != ''
	
	UNION ALL
	
	SELECT DISTINCT
		cache_data->>'科目名' AS subject_name,
		'参考書' AS book_type,
		COALESCE(refbook->>'書名', '未設定') AS book_name,
		CAST(refbook->>'価格' AS INTEGER) AS price,
		refbook->>'著者' AS author,
		refbook->>'ISBN' AS isbn
	FROM syllabus_cache
		JOIN LATERAL jsonb_array_elements(cache_data->'履修情報一覧') AS ri ON TRUE
		JOIN LATERAL jsonb_array_elements(ri->'履修要綱一覧') AS r ON TRUE
		JOIN LATERAL jsonb_array_elements(cache_data->'開講情報一覧') AS open ON TRUE
		JOIN LATERAL jsonb_array_elements(open->'シラバス一覧') AS syl ON TRUE
		JOIN LATERAL jsonb_array_elements(syl->'参考書一覧') AS refbook ON TRUE
	WHERE cache_name = 'subject_syllabus_cache'
		AND refbook->>'価格' IS NOT NULL
		AND refbook->>'価格' != ''
),
max_price AS (
	SELECT MAX(price) AS max_price
	FROM all_books
),
most_expensive_books AS (
	SELECT 
		subject_name,
		book_type,
		book_name,
		price,
		author,
		isbn
	FROM all_books, max_price
	WHERE price = max_price
)
SELECT 
	subject_name,
	book_type,
	book_name,
	price,
	author,
	isbn
FROM most_expensive_books
ORDER BY subject_name, book_type; 
 