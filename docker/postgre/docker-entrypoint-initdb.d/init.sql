-- アプリケーションユーザーとデータベースの作成
CREATE USER :app_user WITH PASSWORD :'app_password';
GRANT ALL PRIVILEGES ON DATABASE :postgres_db TO :app_user;

-- 拡張機能の有効化
CREATE EXTENSION IF NOT EXISTS "uuid-ossp"; 