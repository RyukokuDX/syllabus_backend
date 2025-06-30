-- class テーブルへのデータ挿入
INSERT INTO class (
    class_name, created_at
) VALUES
    ('専攻科目', '2025-06-19T21:30:01.131051'),
    ('教養教育科目', '2025-06-19T21:30:01.131051')
ON CONFLICT (class_name) DO UPDATE SET class_name = EXCLUDED.class_name;
