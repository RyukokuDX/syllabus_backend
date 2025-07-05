-- DBテーブル・カラムコメント（mcp用）
-- ==========================================
-- EAVカタログ（subject_attributeごとの全値一覧）
-- attribute_id: 1, attribute_name: 単位制限, description: 
-- attribute_id: 2, attribute_name: 学修プログラム, description: 
--   value: 1
--   value: 10
--   value: 12
--   value: 13
--   value: 14
--   value: 15
--   value: 16
--   value: 17
--   value: 18
--   value: 19
--   value: 2
--   value: 20
--   value: 21
--   value: 22
--   value: 23
--   value: 24
--   value: 25
--   value: 3
--   value: 4
--   value: 5
--   value: 6
--   value: 7
--   value: 8
--   value: 9
-- attribute_id: 3, attribute_name: 専門応用履修要件, description: 
--   value: 情報系
--   value: 数学系
-- attribute_id: 4, attribute_name: 履修制限, description: 
-- attribute_id: 5, attribute_name: 履修指導科目, description: 
--   value: TRUE
-- attribute_id: 6, attribute_name: 形態, description: 
--   value: 講義演習
--   value: 実験実習
-- attribute_id: 7, attribute_name: 応用化学分野, description: 
--   value: その他
--   value: 英語
--   value: 化学
--   value: 環境化学
--   value: 高分子化学
--   value: 材料科学
--   value: 実験・演習
--   value: 実験・実習
--   value: 数学
--   value: 生物学
--   value: 生物機能分子化学
--   value: 総合
--   value: 地学
--   value: 特別研究
--   value: 物理化学
--   value: 物理学
--   value: 分析化学
--   value: 無機化学
--   value: 有機化学
-- attribute_id: 8, attribute_name: 配当年次履修登録必須科目, description: 
--   value: TRUE
-- ==========================================
COMMENT ON TABLE class IS '科目の大区分を管理するテーブル。';
COMMENT ON COLUMN class.class_id IS 'クラスID（主キー）';
COMMENT ON COLUMN class.class_name IS 'クラス名';
COMMENT ON COLUMN class.created_at IS '作成日時';
COMMENT ON TABLE subclass IS '科目の小区分を管理するテーブル。';
COMMENT ON COLUMN subclass.subclass_id IS '小区分ID（主キー）';
COMMENT ON COLUMN subclass.subclass_name IS '小区分名';
COMMENT ON COLUMN subclass.created_at IS '作成日時';
COMMENT ON TABLE faculty IS '開講学部・課程を管理するテーブル。';
COMMENT ON COLUMN faculty.faculty_id IS '学部ID（主キー）';
COMMENT ON COLUMN faculty.faculty_name IS '学部・課程名';
COMMENT ON COLUMN faculty.created_at IS '作成日時';
COMMENT ON TABLE subject_name IS '科目名を管理するマスタテーブル。';
COMMENT ON COLUMN subject_name.subject_name_id IS '主キー';
COMMENT ON COLUMN subject_name.name IS '科目名';
COMMENT ON COLUMN subject_name.created_at IS '作成日時';
COMMENT ON TABLE instructor IS '教員の基本情報を管理するテーブル。';
COMMENT ON COLUMN instructor.instructor_id IS '教員ID（主キー）';
COMMENT ON COLUMN instructor.name IS '名前 (漢字かカナ)';
COMMENT ON COLUMN instructor.name_kana IS '名前（カナ）';
COMMENT ON COLUMN instructor.created_at IS '作成日時';
COMMENT ON TABLE syllabus_master IS 'シラバスコードと年度の組み合わせを管理するマスターテーブル。';
COMMENT ON COLUMN syllabus_master.syllabus_id IS 'シラバスID（主キー）';
COMMENT ON COLUMN syllabus_master.syllabus_code IS 'シラバス管理番号';
COMMENT ON COLUMN syllabus_master.syllabus_year IS 'シラバス年';
COMMENT ON COLUMN syllabus_master.created_at IS '作成日時';
COMMENT ON COLUMN syllabus_master.updated_at IS '更新日時';
COMMENT ON TABLE book IS '教科書・参考文献として使用される書籍の情報を管理するテーブル。著者情報はカンマ区切りの単一フィールドで管理。';
COMMENT ON COLUMN book.book_id IS '書籍ID（主キー）';
COMMENT ON COLUMN book.title IS '書籍タイトル';
COMMENT ON COLUMN book.author IS '著者名（カンマ区切り）';
COMMENT ON COLUMN book.publisher IS '出版社名';
COMMENT ON COLUMN book.price IS '価格（税抜）';
COMMENT ON COLUMN book.isbn IS 'ISBN番号';
COMMENT ON COLUMN book.created_at IS '作成日時';
COMMENT ON TABLE book_uncategorized IS '正規のbookテーブルに分類できない書籍情報（ISBNなし、不正ISBN、タイトル不一致、データ不足など）を管理するテーブル。';
COMMENT ON COLUMN book_uncategorized.id IS '主キー';
COMMENT ON COLUMN book_uncategorized.syllabus_id IS 'シラバスID（外部キー）';
COMMENT ON COLUMN book_uncategorized.title IS '書籍タイトル';
COMMENT ON COLUMN book_uncategorized.author IS '著者名';
COMMENT ON COLUMN book_uncategorized.publisher IS '出版社名';
COMMENT ON COLUMN book_uncategorized.price IS '価格（税抜）';
COMMENT ON COLUMN book_uncategorized.role IS '利用方法（教科書、参考書など）';
COMMENT ON COLUMN book_uncategorized.isbn IS 'ISBN番号（不正・未入力含む）';
COMMENT ON COLUMN book_uncategorized.categorization_status IS '未分類理由（ISBNなし、不正ISBN、タイトル不一致、データ不足など）';
COMMENT ON COLUMN book_uncategorized.created_at IS '作成日時';
COMMENT ON COLUMN book_uncategorized.updated_at IS '更新日時';
COMMENT ON TABLE syllabus IS '各科目のシラバス情報を管理するテーブル。Web Syllabusから取得される科目の詳細情報、授業内容、評価方法などを格納。';
COMMENT ON COLUMN syllabus.syllabus_id IS 'シラバスID（主キー、外部キー）';
COMMENT ON COLUMN syllabus.subject_name_id IS '科目名ID（外部キー）';
COMMENT ON COLUMN syllabus.subtitle IS '科目サブタイトル';
COMMENT ON COLUMN syllabus.term IS '開講学期';
COMMENT ON COLUMN syllabus.campus IS '開講キャンパス';
COMMENT ON COLUMN syllabus.credits IS '単位数';
COMMENT ON COLUMN syllabus.goals IS '目的';
COMMENT ON COLUMN syllabus.summary IS '授業概要';
COMMENT ON COLUMN syllabus.attainment IS '到達目標';
COMMENT ON COLUMN syllabus.methods IS '授業方法';
COMMENT ON COLUMN syllabus.outside_study IS '授業外学習';
COMMENT ON COLUMN syllabus.textbook_comment IS '教科書に関するコメント';
COMMENT ON COLUMN syllabus.reference_comment IS '参考文献に関するコメント';
COMMENT ON COLUMN syllabus.grading_comment IS '成績評価に関するコメント';
COMMENT ON COLUMN syllabus.advice IS '履修上の注意';
COMMENT ON COLUMN syllabus.created_at IS '作成日時';
COMMENT ON COLUMN syllabus.updated_at IS '更新日時';
COMMENT ON TABLE subject_grade IS '科目の履修可能学年を管理するテーブル。';
COMMENT ON COLUMN subject_grade.id IS '主キー';
COMMENT ON COLUMN subject_grade.syllabus_id IS 'シラバスID（外部キー）';
COMMENT ON COLUMN subject_grade.grade IS '履修可能学年';
COMMENT ON COLUMN subject_grade.created_at IS '作成日時';
COMMENT ON COLUMN subject_grade.updated_at IS '更新日時';
COMMENT ON TABLE lecture_time IS '各科目の開講時間情報を管理するテーブル。複数時限に対応。';
COMMENT ON COLUMN lecture_time.id IS 'ID（主キー）';
COMMENT ON COLUMN lecture_time.syllabus_id IS 'シラバスID（外部キー）';
COMMENT ON COLUMN lecture_time.day_of_week IS '曜日 or 集中';
COMMENT ON COLUMN lecture_time.period IS '時限';
COMMENT ON COLUMN lecture_time.created_at IS '作成日時';
COMMENT ON COLUMN lecture_time.updated_at IS '更新日時';
COMMENT ON TABLE lecture_session IS '各科目の講義回数ごとの情報を管理するテーブル。';
COMMENT ON COLUMN lecture_session.lecture_session_id IS '講義回数ID（主キー）';
COMMENT ON COLUMN lecture_session.syllabus_id IS 'シラバスID（外部キー）';
COMMENT ON COLUMN lecture_session.session_number IS '回数';
COMMENT ON COLUMN lecture_session.contents IS '学修内容';
COMMENT ON COLUMN lecture_session.other_info IS 'その他情報';
COMMENT ON COLUMN lecture_session.lecture_format IS '講義形式（対面、オンライン、ハイブリッド）';
COMMENT ON COLUMN lecture_session.created_at IS '作成日時';
COMMENT ON COLUMN lecture_session.updated_at IS '更新日時';
COMMENT ON TABLE lecture_session_irregular IS '不定形の講義回数情報を管理するテーブル。';
COMMENT ON COLUMN lecture_session_irregular.lecture_session_irregular_id IS '不定形講義回数ID（主キー）';
COMMENT ON COLUMN lecture_session_irregular.syllabus_id IS 'シラバスID（外部キー）';
COMMENT ON COLUMN lecture_session_irregular.session_pattern IS '回数パターン';
COMMENT ON COLUMN lecture_session_irregular.contents IS '学修内容';
COMMENT ON COLUMN lecture_session_irregular.other_info IS 'その他情報';
COMMENT ON COLUMN lecture_session_irregular.instructor IS '担当者名（生データ）';
COMMENT ON COLUMN lecture_session_irregular.error_message IS 'エラーメッセージ';
COMMENT ON COLUMN lecture_session_irregular.lecture_format IS '講義形式（対面、オンライン、ハイブリッド）';
COMMENT ON COLUMN lecture_session_irregular.created_at IS '作成日時';
COMMENT ON COLUMN lecture_session_irregular.updated_at IS '更新日時';
COMMENT ON TABLE syllabus_instructor IS 'シラバスと教員の関連を管理する中間テーブル。Web Syllabusから取得される教員の役割情報を格納。';
COMMENT ON COLUMN syllabus_instructor.id IS 'ID（主キー）';
COMMENT ON COLUMN syllabus_instructor.syllabus_id IS 'シラバスID（外部キー）';
COMMENT ON COLUMN syllabus_instructor.instructor_id IS '教員ID（外部キー）';
COMMENT ON COLUMN syllabus_instructor.role IS '役割';
COMMENT ON COLUMN syllabus_instructor.created_at IS '作成日時';
COMMENT ON COLUMN syllabus_instructor.updated_at IS '更新日時';
COMMENT ON TABLE lecture_session_instructor IS '講義回数ごとの担当者情報を管理するテーブル。Web Syllabusから取得される講義回数ごとの担当者情報を格納。';
COMMENT ON COLUMN lecture_session_instructor.id IS 'ID（主キー）';
COMMENT ON COLUMN lecture_session_instructor.lecture_session_id IS '講義回数ID（外部キー）';
COMMENT ON COLUMN lecture_session_instructor.instructor_id IS '担当者ID（外部キー）';
COMMENT ON COLUMN lecture_session_instructor.role IS '役割';
COMMENT ON COLUMN lecture_session_instructor.created_at IS '作成日時';
COMMENT ON COLUMN lecture_session_instructor.updated_at IS '更新日時';
COMMENT ON TABLE syllabus_book IS 'シラバスと教科書の関連を管理する中間テーブル。';
COMMENT ON COLUMN syllabus_book.id IS 'ID';
COMMENT ON COLUMN syllabus_book.syllabus_id IS 'シラバスID（外部キー）';
COMMENT ON COLUMN syllabus_book.book_id IS '書籍ID';
COMMENT ON COLUMN syllabus_book.role IS '利用方法(教科書, 参考書)';
COMMENT ON COLUMN syllabus_book.note IS '備考';
COMMENT ON COLUMN syllabus_book.created_at IS '作成日時';
COMMENT ON TABLE grading_criterion IS '成績評価の基準と比率を管理するテーブル。';
COMMENT ON COLUMN grading_criterion.id IS 'ID（主キー）';
COMMENT ON COLUMN grading_criterion.syllabus_id IS 'シラバスID（外部キー）';
COMMENT ON COLUMN grading_criterion.criteria_type IS '評価種別';
COMMENT ON COLUMN grading_criterion.criteria_description IS '評価基準の詳細説明';
COMMENT ON COLUMN grading_criterion.ratio IS '評価比率';
COMMENT ON COLUMN grading_criterion.note IS '備考';
COMMENT ON COLUMN grading_criterion.created_at IS '作成日時';
COMMENT ON TABLE subject_attribute IS '科目の属性を管理するマスターテーブル。';
COMMENT ON COLUMN subject_attribute.attribute_id IS '属性ID（主キー）';
COMMENT ON COLUMN subject_attribute.attribute_name IS '属性名';
COMMENT ON COLUMN subject_attribute.description IS '属性の説明';
COMMENT ON COLUMN subject_attribute.created_at IS '作成日時';
COMMENT ON TABLE subject IS '科目の基本情報を管理するテーブル。科目のマスターデータを格納。';
COMMENT ON COLUMN subject.subject_id IS 'ID（主キー）';
COMMENT ON COLUMN subject.subject_name_id IS '科目名ID（外部キー）';
COMMENT ON COLUMN subject.faculty_id IS '開講学部ID（外部キー）';
COMMENT ON COLUMN subject.curriculum_year IS '要綱年';
COMMENT ON COLUMN subject.class_id IS 'クラスID（外部キー）';
COMMENT ON COLUMN subject.subclass_id IS '小区分ID（外部キー）';
COMMENT ON COLUMN subject.requirement_type IS '必修/選択区分';
COMMENT ON COLUMN subject.created_at IS '作成日時';
COMMENT ON COLUMN subject.updated_at IS '更新日時';
COMMENT ON TABLE subject_attribute_value IS '科目の属性値を管理するテーブル。EAVパターンを使用して科目の属性値を格納。';
COMMENT ON COLUMN subject_attribute_value.id IS '主キー';
COMMENT ON COLUMN subject_attribute_value.subject_id IS '科目ID（外部キー）';
COMMENT ON COLUMN subject_attribute_value.attribute_id IS '属性ID（外部キー）';
COMMENT ON COLUMN subject_attribute_value.value IS '属性値';
COMMENT ON COLUMN subject_attribute_value.created_at IS '作成日時';
COMMENT ON COLUMN subject_attribute_value.updated_at IS '更新日時';
COMMENT ON TABLE syllabus_faculty IS 'シラバスと学部・課程の関連を管理する中間テーブル。シラバスがどの学部・課程で開講されるかを管理。';
COMMENT ON COLUMN syllabus_faculty.id IS 'ID（主キー）';
COMMENT ON COLUMN syllabus_faculty.syllabus_id IS 'シラバスID（外部キー）';
COMMENT ON COLUMN syllabus_faculty.faculty_id IS '学部・課程ID（外部キー）';
COMMENT ON COLUMN syllabus_faculty.created_at IS '作成日時';
COMMENT ON COLUMN syllabus_faculty.updated_at IS '更新日時';
COMMENT ON TABLE syllabus_study_system IS 'シラバスの系統的履修関係を管理するテーブル。科目間の履修順序や前提条件を表現。Web Syllabusの「履修条件」から取得される情報を格納。';
COMMENT ON COLUMN syllabus_study_system.id IS 'ID（主キー）';
COMMENT ON COLUMN syllabus_study_system.source_syllabus_id IS '引用元シラバスID（外部キー）';
COMMENT ON COLUMN syllabus_study_system.target IS '引用先科目';
COMMENT ON COLUMN syllabus_study_system.created_at IS '作成日時';
COMMENT ON COLUMN syllabus_study_system.updated_at IS '更新日時';