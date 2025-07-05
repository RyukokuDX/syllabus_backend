# File Version: v2.6.0
# Project Version: v2.6.0
# Last Updated: 2025-07-05

import sys
import os

# プロジェクトルートをパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

def test_imports():
    """インポートのテスト"""
    try:
        from src.db.database import SessionLocal
        print(" SessionLocal インポート成功")
        
        from src.db.models import SyllabusMaster
        print(" SyllabusMaster インポート成功")
        
        return True
    except Exception as e:
        print(f" インポートエラー: {str(e)}")
        return False

def test_db_connection():
    """データベース接続のテスト"""
    try:
        from src.db.database import SessionLocal
        
        session = SessionLocal()
        print(" データベース接続成功")
        
        # テーブルが存在するかテスト
        result = session.execute("SELECT COUNT(*) FROM syllabus_master")
        count = result.scalar()
        print(f" syllabus_masterテーブル存在確認: {count}件のレコード")
        
        session.close()
        return True
    except Exception as e:
        print(f" データベース接続エラー: {str(e)}")
        return False

def test_syllabus_master_query():
    """syllabus_masterテーブルのクエリテスト"""
    try:
        from src.db.database import SessionLocal
        from src.db.models import SyllabusMaster
        
        session = SessionLocal()
        
        # 全件取得
        all_records = session.query(SyllabusMaster).all()
        print(f" syllabus_master全件取得: {len(all_records)}件")
        
        if all_records:
            # 最初のレコードの詳細を表示
            first_record = all_records[0]
            print(f"  最初のレコード: ID={first_record.syllabus_id}, "
                  f"コード={first_record.syllabus_code}, "
                  f"年度={first_record.syllabus_year}")
        
        session.close()
        return True
    except Exception as e:
        print(f" syllabus_masterクエリエラー: {str(e)}")
        return False

def test_get_syllabus_master_id():
    """get_syllabus_master_id_from_db関数のテスト"""
    try:
        from utils import get_db_connection, get_syllabus_master_id_from_db
        
        session = get_db_connection()
        print(" get_db_connection成功")
        
        # テスト用のクエリ（存在しないコード）
        result = get_syllabus_master_id_from_db(session, "TEST001", 2025)
        print(f" get_syllabus_master_id_from_db実行: {result}")
        
        session.close()
        return True
    except Exception as e:
        print(f" get_syllabus_master_id_from_dbエラー: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== データベース接続テスト ===")
    
    # 1. インポートテスト
    print("\n1. インポートテスト")
    if not test_imports():
        sys.exit(1)
    
    # 2. データベース接続テスト
    print("\n2. データベース接続テスト")
    if not test_db_connection():
        sys.exit(1)
    
    # 3. syllabus_masterクエリテスト
    print("\n3. syllabus_masterクエリテスト")
    if not test_syllabus_master_query():
        sys.exit(1)
    
    # 4. 関数テスト
    print("\n4. 関数テスト")
    if not test_get_syllabus_master_id():
        sys.exit(1)
    
    print("\n=== 全てのテストが成功しました ===") 