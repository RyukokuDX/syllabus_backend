-- ========== 開発用データベースの作成 ==========

-- syllabus_dbをテンプレートとして使用して開発用データベースを作成
DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'syllabus_dev_db') THEN
    CREATE DATABASE syllabus_dev_db TEMPLATE syllabus_db;
  END IF;
END
$$;

-- ========== 権限付与 ==========

-- 接続切替（syllabus_dev_db）
\connect syllabus_dev_db

-- スキーマ権限
GRANT CONNECT ON DATABASE syllabus_dev_db TO dev_user, app_user;
GRANT USAGE ON SCHEMA public TO dev_user, app_user;
GRANT ALL PRIVILEGES ON SCHEMA public TO dev_user;

-- テーブルとシーケンスの権限
GRANT SELECT ON ALL TABLES IN SCHEMA public TO dev_user, app_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO dev_user, app_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO dev_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO dev_user;

-- デフォルト権限の設定
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT ON TABLES TO dev_user, app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT USAGE, SELECT ON SEQUENCES TO dev_user, app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT ALL PRIVILEGES ON TABLES TO dev_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT ALL PRIVILEGES ON SEQUENCES TO dev_user;

-- カタログ参照権限
GRANT SELECT ON pg_catalog.pg_tables TO dev_user, app_user;
GRANT SELECT ON information_schema.tables TO dev_user, app_user; \i /docker-entrypoint-initdb.d/migrations/V20250522111408__insert_class_notes.sql
\i /docker-entrypoint-initdb.d/migrations/V20250522111408__insert_classs.sql
\i /docker-entrypoint-initdb.d/migrations/V20250522111408__insert_subclasss.sql
\i /docker-entrypoint-initdb.d/migrations/V20250522111408__insert_subject_names.sql
-- \i /docker-entrypoint-initdb.d/migrations/V20250522171503__insert_subjects.sql
