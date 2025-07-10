-- JSONBキャッシュで最も高い本が正規化テーブルと異なる理由を調査
-- 正規化テーブルの上位5件の本がJSONBキャッシュに存在するかチェック

WITH expensive_books AS (
	SELECT 
		title,
		price,
		isbn
	FROM book
	WHERE price IS NOT NULL
	ORDER BY price DESC
	LIMIT 5
),
cache_books AS (
	SELECT DISTINCT
		textbook->>'書名' AS title,
		CAST(textbook->>'価格' AS INTEGER) AS price,
		textbook->>'ISBN' AS isbn,
		'教科書' AS book_type
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
		refbook->>'書名' AS title,
		CAST(refbook->>'価格' AS INTEGER) AS price,
		refbook->>'ISBN' AS isbn,
		'参考書' AS book_type
	FROM syllabus_cache
		JOIN LATERAL jsonb_array_elements(cache_data->'履修情報一覧') AS ri ON TRUE
		JOIN LATERAL jsonb_array_elements(ri->'履修要綱一覧') AS r ON TRUE
		JOIN LATERAL jsonb_array_elements(cache_data->'開講情報一覧') AS open ON TRUE
		JOIN LATERAL jsonb_array_elements(open->'シラバス一覧') AS syl ON TRUE
		JOIN LATERAL jsonb_array_elements(syl->'参考書一覧') AS refbook ON TRUE
	WHERE cache_name = 'subject_syllabus_cache'
		AND refbook->>'価格' IS NOT NULL
		AND refbook->>'価格' != ''
)
SELECT 
	eb.title AS normalized_title,
	eb.price AS normalized_price,
	eb.isbn AS normalized_isbn,
	cb.title AS cache_title,
	cb.price AS cache_price,
	cb.isbn AS cache_isbn,
	cb.book_type,
	CASE 
		WHEN cb.title IS NULL THEN 'JSONBキャッシュに存在しない'
		ELSE 'JSONBキャッシュに存在'
	END AS status
FROM expensive_books eb
LEFT JOIN cache_books cb ON eb.isbn = cb.isbn OR eb.title = cb.title
ORDER BY eb.price DESC; 