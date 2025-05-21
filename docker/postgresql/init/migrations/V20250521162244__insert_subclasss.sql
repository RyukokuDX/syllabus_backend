-- subclass テーブルへのデータ挿入
INSERT INTO subclass (
    subclass_name, created_at, updated_at
) VALUES
    ('英語', '2025-05-21T16:22:35.144380', NULL),
    ('人文科学系', '2025-05-21T16:22:35.144380', NULL),
    ('自然科学系', '2025-05-21T16:22:35.144380', NULL),
    ('スポーツ科学系', '2025-05-21T16:22:35.144380', NULL),
    ('社会科学系', '2025-05-21T16:22:35.144380', NULL),
    ('初修外国語', '2025-05-21T16:22:35.144380', NULL),
    ('コース科目', '2025-05-21T16:22:35.144380', NULL),
    ('保護課程科目', '2025-05-21T16:22:35.144380', NULL)
ON CONFLICT (subclass_name) DO UPDATE SET
    updated_at = EXCLUDED.updated_at,
    updated_at = CURRENT_TIMESTAMP;
