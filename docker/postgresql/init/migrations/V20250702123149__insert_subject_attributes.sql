-- subject_attribute テーブルへのデータ挿入
INSERT INTO subject_attribute (
    created_at, description, attribute_name
) VALUES
    ('2025-07-02T12:31:32.046671', NULL, '単位制限'),
    ('2025-07-02T12:31:32.049942', NULL, '学修プログラム'),
    ('2025-07-02T12:31:32.053245', NULL, '専門応用履修要件'),
    ('2025-07-02T12:31:32.046540', NULL, '履修制限'),
    ('2025-07-02T12:31:32.053246', NULL, '履修指導科目'),
    ('2025-07-02T12:31:32.060047', NULL, '形態'),
    ('2025-07-02T12:31:32.049923', NULL, '応用化学分野'),
    ('2025-07-02T12:31:32.053227', NULL, '配当年次履修登録必須科目')
ON CONFLICT (attribute_name) DO UPDATE SET attribute_name = EXCLUDED.attribute_name, description = EXCLUDED.description;
