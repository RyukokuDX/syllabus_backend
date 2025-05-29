-- ========== 開発用データベースの作成 ==========

-- 開発用データベースの作成
CREATE DATABASE syllabus_db_dev WITH TEMPLATE syllabus_db;

-- ========== 権限付与 ==========

-- 開発用データベースへの権限付与
GRANT ALL PRIVILEGES ON DATABASE syllabus_db_dev TO dev_user;
GRANT ALL PRIVILEGES ON DATABASE syllabus_db_dev TO app_user;

-- 開発用データベースのスキーマ権限付与
\c syllabus_db_dev
GRANT ALL ON SCHEMA public TO dev_user;
GRANT ALL ON SCHEMA public TO app_user;

-- 開発用データベースのテーブル・シーケンス権限付与
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO dev_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO app_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO dev_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO app_user;

-- 開発用データベースのデフォルト権限設定
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO dev_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO dev_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO app_user;

-- 開発用データベースのカタログ参照権限付与
GRANT USAGE ON SCHEMA public TO dev_user;
GRANT USAGE ON SCHEMA public TO app_user; \i /docker-entrypoint-initdb.d/migrations/V20250522111408__insert_class_notes.sql
\i /docker-entrypoint-initdb.d/migrations/V20250522111408__insert_classs.sql
\i /docker-entrypoint-initdb.d/migrations/V20250522111408__insert_subclasss.sql
\i /docker-entrypoint-initdb.d/migrations/V20250522111408__insert_subject_names.sql
