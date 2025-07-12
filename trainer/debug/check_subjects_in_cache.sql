-- 正規化テーブルで最も高い本を使用している科目が、subjectテーブルに存在するかチェック
-- 1～4番目の本を使用している科目が現在開講されているか確認

WITH expensive_books_subjects AS (
	SELECT
		sn.name AS subject_name,
		sm.syllabus_year AS year,
		b.price
	FROM book b
	JOIN syllabus_book sb ON b.book_id = sb.book_id
	JOIN syllabus_master sm ON sb.syllabus_id = sm.syllabus_id
	JOIN syllabus s ON sm.syllabus_id = s.syllabus_id
	JOIN subject_name sn ON s.subject_name_id = sn.subject_name_id
	WHERE b.price IS NOT NULL
),
top_expensive_books AS (
	SELECT subject_name, year
	FROM (
		SELECT subject_name, year, price
		FROM expensive_books_subjects
		ORDER BY price DESC
		LIMIT 4
	) t
),
current_subjects AS (
	SELECT DISTINCT
		sn.name AS subject_name,
		sub.curriculum_year AS year
	FROM subject sub
	JOIN subject_name sn ON sub.subject_name_id = sn.subject_name_id
	WHERE sub.curriculum_year = 2025
)
SELECT 
	ebs.subject_name AS expensive_book_subject,
	ebs.year AS book_year,
	cs.subject_name AS current_subject,
	cs.year AS current_year,
	CASE 
		WHEN cs.subject_name IS NULL THEN '現在開講されていない'
		ELSE '現在開講されている'
	END AS status
FROM top_expensive_books ebs
LEFT JOIN current_subjects cs ON ebs.subject_name = cs.subject_name
ORDER BY ebs.subject_name; 