-- class_note テーブルへのデータ挿入
INSERT INTO class_note (
    class_note
) VALUES
    ('農学部'),
    ('専攻科目'),
    ('農学研究科'),
    ('国際学部'),
    ('実践真宗学研究科'),
    ('政策学研究科'),
    ('法学部専攻科目'),
    ('政策学部'),
    ('経営学研究科'),
    ('心理学研究科'),
    ('理工学研究科'),
    ('短大')
ON CONFLICT (class_note) DO UPDATE SET
    updated_at = CURRENT_TIMESTAMP;
