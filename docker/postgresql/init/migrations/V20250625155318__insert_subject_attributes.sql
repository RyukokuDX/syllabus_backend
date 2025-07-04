-- subject_attribute テーブルへのデータ挿入
INSERT INTO subject_attribute (
    created_at, description, attribute_name
) VALUES
    ('2025-06-25T13:54:58.354491', NULL, '単位制限'),
    ('2025-06-25T13:54:58.357624', NULL, '学修プログラム'),
    ('2025-06-25T13:54:58.360715', NULL, '専門応用履修要件'),
    ('2025-06-25T13:54:58.354465', NULL, '履修制限'),
    ('2025-06-25T13:54:58.360716', NULL, '履修指導科目'),
    ('2025-06-25T13:54:58.366203', NULL, '形態'),
    ('2025-06-25T13:54:58.357615', NULL, '応用化学分野'),
    ('2025-06-25T13:54:58.360704', NULL, '配当年次履修登録必須科目')
ON CONFLICT (attribute_name) DO UPDATE SET attribute_name = EXCLUDED.attribute_name, description = EXCLUDED.description;
