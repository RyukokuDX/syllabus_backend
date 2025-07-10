-- 最も高い本の値段を検索するデバッグクエリ（正規化テーブル使用）
-- structure.mdを参考にして、bookテーブルから最も高い価格を検索

SELECT 
	book_id,
	title,
	author,
	price,
	isbn
FROM book
WHERE price IS NOT NULL
ORDER BY price DESC
LIMIT 5; 