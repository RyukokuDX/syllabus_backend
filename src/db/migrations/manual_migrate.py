#!/usr/bin/env python3
import os
import sys
import psycopg2
from typing import List, Optional
from pathlib import Path
from datetime import datetime

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
    migration_files = sorted([
        f for f in migrations_dir.glob("*.sql")
        if f.name.startswith("V") and f.name.endswith(".sql")
    ])
    
    # マイグレーションファイルの存在確認
    if not migration_files:
        raise FileNotFoundError("マイグレーションファイルが見つかりません")
    
    # マイグレーションファイルの順序を確認
    for i, file in enumerate(migration_files):
        try:
            version = int(file.name[1:].split("__")[0])
            if i > 0:
                prev_version = int(migration_files[i-1].name[1:].split("__")[0])
                if version <= prev_version:
                    raise ValueError(f"マイグレーションファイルの順序が不正です: {file.name}")
        except ValueError as e:
            raise ValueError(f"マイグレーションファイル名の形式が不正です: {file.name}") from e
    
    return migration_files

def execute_migration(conn: psycopg2.extensions.connection, migration_file: Path) -> None:
    """マイグレーションファイルを実行"""
    start_time = datetime.now()
    print(f"[{start_time.strftime('%Y-%m-%d %H:%M:%S')}] 実行開始: {migration_file.name}")
    
    try:
        with conn.cursor() as cur:
            # ファイルの内容を読み込んで実行
            with open(migration_file, "r", encoding="utf-8") as f:
                sql = f.read()
                cur.execute(sql)
        
        conn.commit()
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        print(f"[{end_time.strftime('%Y-%m-%d %H:%M:%S')}] 完了: {migration_file.name} (所要時間: {duration:.2f}秒)")
    
    except psycopg2.Error as e:
        conn.rollback()
        raise RuntimeError(f"マイグレーション実行エラー ({migration_file.name}): {str(e)}") from e
    except Exception as e:
        conn.rollback()
        raise RuntimeError(f"予期せぬエラー ({migration_file.name}): {str(e)}") from e

def main(database: Optional[str] = None) -> None:
    """メイン処理"""
    start_time = datetime.now()
    print(f"[{start_time.strftime('%Y-%m-%d %H:%M:%S')}] マイグレーション開始")
    
    # マイグレーションファイルのディレクトリを取得
    migrations_dir = Path(__file__).parent

    try:
        # マイグレーションファイルを取得
        migration_files = get_migration_files(migrations_dir)
        
        # データベースに接続
        conn = get_connection(database) if database else get_connection()
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] データベース '{conn.info.dbname}' に接続しました")

        # 各マイグレーションファイルを実行
        for migration_file in migration_files:
            execute_migration(conn, migration_file)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        print(f"[{end_time.strftime('%Y-%m-%d %H:%M:%S')}] 全てのマイグレーションが完了しました (所要時間: {duration:.2f}秒)")

    except FileNotFoundError as e:
        print(f"エラー: {str(e)}")
        sys.exit(1)
    except ValueError as e:
        print(f"エラー: {str(e)}")
        sys.exit(1)
    except psycopg2.Error as e:
        print(f"データベース接続エラー: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"予期せぬエラー: {str(e)}")
        sys.exit(1)
    finally:
        if 'conn' in locals():
            conn.close()
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] データベース接続を終了しました")

if __name__ == "__main__":
    # コマンドライン引数からデータベース名を取得（オプション）
    database = sys.argv[1] if len(sys.argv) > 1 else None
    main(database) 