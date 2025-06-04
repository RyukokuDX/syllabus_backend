-- ========== 開発用データベースの作成 ==========

-- syllabus_dbが作成されるまで待機
DO $$
BEGIN
    WHILE NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'syllabus_db') LOOP
        PERFORM pg_sleep(1);
    END LOOP;
END
$$;

-- 既存の開発用データベースを削除
DROP DATABASE IF EXISTS syllabus_dev_db;

-- 開発用データベースの作成
CREATE DATABASE syllabus_dev_db WITH TEMPLATE syllabus_db;

-- ========== 権限付与 ==========

-- 開発用データベースへの権限付与
GRANT ALL PRIVILEGES ON DATABASE syllabus_dev_db TO dev_user;
GRANT ALL PRIVILEGES ON DATABASE syllabus_dev_db TO app_user;

-- 開発用データベースのスキーマ権限付与
\c syllabus_dev_db
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
GRANT USAGE ON SCHEMA public TO app_user;\i /docker-entrypoint-initdb.d/migrations/V20250604105720__insert_subject_names.sql
\i /docker-entrypoint-initdb.d/migrations/V20250604105720__insert_syllabus_masters.sql
\i /docker-entrypoint-initdb.d/migrations/V20250604112913__insert_instructors.sql
