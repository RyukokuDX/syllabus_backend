-- 数理·情報科学課程の専門応用科目で火曜開講のものを表示
SELECT 
    sn.name AS 科目名,
    s.term AS 学期,
    s.campus AS キャンパス,
    s.credits AS 単位数,
    lt.day_of_week AS 曜日,
    lt.period AS 時限,
    f.faculty_name AS 課程名,
    c.class_name AS 科目区分,
    sc.subclass_name AS 科目小区分
FROM syllabus s
JOIN syllabus_master sm ON s.syllabus_id = sm.syllabus_id
JOIN subject_name sn ON s.subject_name_id = sn.subject_name_id
JOIN lecture_time lt ON sm.syllabus_id = lt.syllabus_id
JOIN subject sub ON sn.subject_name_id = sub.subject_name_id
JOIN faculty f ON sub.faculty_id = f.faculty_id
JOIN class c ON sub.class_id = c.class_id
LEFT JOIN subclass sc ON sub.subclass_id = sc.subclass_id
WHERE 
    f.faculty_name = '数理·情報科学課程'
    AND c.class_name = '専攻科目'
    AND sc.subclass_name = '専門応用科目'
    AND lt.day_of_week = '火'
    AND sm.syllabus_year = 2025
ORDER BY 
    lt.period, sn.name;

-- データベースの実際の値を確認するクエリ

-- 1. 課程名の一覧を確認
SELECT DISTINCT f.faculty_name AS 課程名
FROM faculty f
ORDER BY f.faculty_name;

-- 2. 科目区分の一覧を確認
SELECT DISTINCT c.class_name AS 科目区分
FROM class c
ORDER BY c.class_name;

-- 3. 科目小区分の一覧を確認
SELECT DISTINCT sc.subclass_name AS 科目小区分
FROM subclass sc
WHERE sc.subclass_name IS NOT NULL
ORDER BY sc.subclass_name;

-- 4. 曜日の一覧を確認
SELECT DISTINCT lt.day_of_week AS 曜日
FROM lecture_time lt
ORDER BY lt.day_of_week;

-- 5. 年度の一覧を確認
SELECT DISTINCT sm.syllabus_year AS 年度
FROM syllabus_master sm
ORDER BY sm.syllabus_year;
