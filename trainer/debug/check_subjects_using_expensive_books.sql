-- 正規化テーブルで最も高い本（1～4番目）を利用している科目名を調べる
-- structure.mdを参考にして、bookテーブルとsyllabus_book、syllabus_master、subject_nameテーブルを結合

WITH expensive_books AS (
	SELECT 
		book_id,
		title,
		price,
		isbn
	FROM book
	WHERE price IS NOT NULL
	ORDER BY price DESC
	LIMIT 4
)
SELECT 
	eb.title AS book_title,
	eb.price AS book_price,
	eb.isbn AS book_isbn,
	sb.role AS book_role,
	sn.name AS subject_name,
	sm.syllabus_year AS year
FROM expensive_books eb
JOIN syllabus_book sb ON eb.book_id = sb.book_id
JOIN syllabus_master sm ON sb.syllabus_id = sm.syllabus_id
JOIN syllabus s ON sm.syllabus_id = s.syllabus_id
JOIN subject_name sn ON s.subject_name_id = sn.subject_name_id
ORDER BY eb.price DESC, sn.name; 