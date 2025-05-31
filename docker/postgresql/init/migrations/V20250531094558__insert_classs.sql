-- class テーブルへのデータ挿入
INSERT INTO class (
    class_name, created_at
) VALUES
    ('専攻科目', '2025-05-29T13:42:09.283915'),
    ('教養教育科目', '2025-05-29T13:42:09.283915'),
    ('専攻科目', '2025-05-31T07:59:32.958691'),
    ('教養教育科目', '2025-05-31T07:59:32.958691')
ON CONFLICT (class_name) DO NOTHING;
