# File Version: v2.0.0
# Project Version: v2.0.0
# Last Updated: 2025-06-30

import sys
import os

# �ץ������ȥ롼�Ȥ�ѥ����ɲ�
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

def test_imports():
    """����ݡ��ȤΥƥ���"""
    try:
        from src.db.database import SessionLocal
        print(" SessionLocal ����ݡ�������")
        
        from src.db.models import SyllabusMaster
        print(" SyllabusMaster ����ݡ�������")
        
        return True
    except Exception as e:
        print(f" ����ݡ��ȥ��顼: {str(e)}")
        return False

def test_db_connection():
    """�ǡ����١�����³�Υƥ���"""
    try:
        from src.db.database import SessionLocal
        
        session = SessionLocal()
        print(" �ǡ����١�����³����")
        
        # �ơ��֥뤬¸�ߤ��뤫�ƥ���
        result = session.execute("SELECT COUNT(*) FROM syllabus_master")
        count = result.scalar()
        print(f" syllabus_master�ơ��֥�¸�߳�ǧ: {count}��Υ쥳����")
        
        session.close()
        return True
    except Exception as e:
        print(f" �ǡ����١�����³���顼: {str(e)}")
        return False

def test_syllabus_master_query():
    """syllabus_master�ơ��֥�Υ�����ƥ���"""
    try:
        from src.db.database import SessionLocal
        from src.db.models import SyllabusMaster
        
        session = SessionLocal()
        
        # �������
        all_records = session.query(SyllabusMaster).all()
        print(f" syllabus_master�������: {len(all_records)}��")
        
        if all_records:
            # �ǽ�Υ쥳���ɤξܺ٤�ɽ��
            first_record = all_records[0]
            print(f"  �ǽ�Υ쥳����: ID={first_record.syllabus_id}, "
                  f"������={first_record.syllabus_code}, "
                  f"ǯ��={first_record.syllabus_year}")
        
        session.close()
        return True
    except Exception as e:
        print(f" syllabus_master�����ꥨ�顼: {str(e)}")
        return False

def test_get_syllabus_master_id():
    """get_syllabus_master_id_from_db�ؿ��Υƥ���"""
    try:
        from utils import get_db_connection, get_syllabus_master_id_from_db
        
        session = get_db_connection()
        print(" get_db_connection����")
        
        # �ƥ����ѤΥ������¸�ߤ��ʤ������ɡ�
        result = get_syllabus_master_id_from_db(session, "TEST001", 2025)
        print(f" get_syllabus_master_id_from_db�¹�: {result}")
        
        session.close()
        return True
    except Exception as e:
        print(f" get_syllabus_master_id_from_db���顼: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== �ǡ����١�����³�ƥ��� ===")
    
    # 1. ����ݡ��ȥƥ���
    print("\n1. ����ݡ��ȥƥ���")
    if not test_imports():
        sys.exit(1)
    
    # 2. �ǡ����١�����³�ƥ���
    print("\n2. �ǡ����١�����³�ƥ���")
    if not test_db_connection():
        sys.exit(1)
    
    # 3. syllabus_master������ƥ���
    print("\n3. syllabus_master������ƥ���")
    if not test_syllabus_master_query():
        sys.exit(1)
    
    # 4. �ؿ��ƥ���
    print("\n4. �ؿ��ƥ���")
    if not test_get_syllabus_master_id():
        sys.exit(1)
    
    print("\n=== ���ƤΥƥ��Ȥ��������ޤ��� ===") 