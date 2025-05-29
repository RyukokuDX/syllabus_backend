-- subclass テーブルへのデータ挿入
INSERT INTO subclass (
    subclass_name
) VALUES
    ('自然科学系'),
    ('スポーツ科学系'),
    ('英語'),
    ('人文科学系'),
    ('社会科学系'),
    ('初修外国語'),
    ('コース科目'),
    ('保護課程科目')
ON CONFLICT (subclass_name) DO UPDATE SET
    updated_at = CURRENT_TIMESTAMP;
