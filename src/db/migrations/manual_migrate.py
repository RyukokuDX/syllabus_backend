#!/usr/bin/env python3
import os
import sys
import psycopg2
from typing import List, Optional
from pathlib import Path

def get_connection(database: str = "master_db") -> psycopg2.extensions.connection:
    """データベースへの接続を取得"""
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        database=database,
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres")
    )

def get_migration_files(migrations_dir: Path) -> List[Path]:
    """マイグレーションファイルを取得"""
    return sorted([
        f for f in migrations_dir.glob("*.sql")
        if f.name.startswith("V") and f.name.endswith(".sql")
    ])

def execute_migration(conn: psycopg2.extensions.connection, migration_file: Path) -> None:
    """マイグレーションファイルを実行"""
    print(f"実行中: {migration_file.name}")
    
    with conn.cursor() as cur:
        # ファイルの内容を読み込んで実行
        with open(migration_file, "r", encoding="utf-8") as f:
            sql = f.read()
            cur.execute(sql)
    
    conn.commit()
    print(f"完了: {migration_file.name}")

def main(database: Optional[str] = None) -> None:
    """メイン処理"""
    # マイグレーションファイルのディレクトリを取得
    migrations_dir = Path(__file__).parent

    # マイグレーションファイルを取得
    migration_files = get_migration_files(migrations_dir)
    if not migration_files:
        print("マイグレーションファイルが見つかりません")
        sys.exit(1)

    # データベースに接続
    try:
        conn = get_connection(database) if database else get_connection()
    except psycopg2.Error as e:
        print(f"データベース接続エラー: {e}")
        sys.exit(1)

    print(f"データベース '{conn.info.dbname}' に接続しました")

    try:
        # 各マイグレーションファイルを実行
        for migration_file in migration_files:
            try:
                execute_migration(conn, migration_file)
            except psycopg2.Error as e:
                print(f"マイグレーションエラー ({migration_file.name}): {e}")
                conn.rollback()
                sys.exit(1)

        print("全てのマイグレーションが完了しました")

    finally:
        conn.close()

if __name__ == "__main__":
    # コマンドライン引数からデータベース名を取得（オプション）
    database = sys.argv[1] if len(sys.argv) > 1 else None
    main(database) 