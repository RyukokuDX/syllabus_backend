-- 知能情報メディア課程の専門基礎科目のうち、期末試験がないものを表示
SELECT DISTINCT
    sn.name AS 科目名,
    s.term AS 学期,
    s.campus AS キャンパス,
    s.credits AS 単位数,
    STRING_AGG(DISTINCT gc.criteria_type, ', ' ORDER BY gc.criteria_type) AS 評価方法,
    REPLACE(REPLACE(s.grading_comment, E'\n', ' '), E'\r', ' ') AS 成績評価コメント
FROM syllabus s
JOIN syllabus_master sm ON s.syllabus_id = sm.syllabus_id
JOIN subject_name sn ON s.subject_name_id = sn.subject_name_id
JOIN subject sub ON sn.subject_name_id = sub.subject_name_id
JOIN faculty f ON sub.faculty_id = f.faculty_id
JOIN class c ON sub.class_id = c.class_id
LEFT JOIN subclass sc ON sub.subclass_id = sc.subclass_id
LEFT JOIN grading_criterion gc ON sm.syllabus_id = gc.syllabus_id
WHERE 
    f.faculty_name = '知能情報メディア課程'
    AND c.class_name = '専攻科目'
    AND sc.subclass_name = '専門基礎科目'
    AND sm.syllabus_year = 2025
    AND s.grading_comment IS NOT NULL
    AND s.grading_comment != ''
    AND NOT EXISTS (
        SELECT 1 
        FROM grading_criterion gc2 
        WHERE gc2.syllabus_id = sm.syllabus_id 
        AND (gc2.criteria_type LIKE '%期末%' 
             OR gc2.criteria_type LIKE '%定期試験%'
             OR gc2.criteria_type LIKE '%試験%')
    )
GROUP BY 
    sn.name, s.term, s.campus, s.credits, s.grading_comment
ORDER BY 
    sn.name;
