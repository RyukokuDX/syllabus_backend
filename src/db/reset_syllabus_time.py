import sqlite3
import os
import json
from glob import glob
from datetime import datetime

def reset_syllabus_time():
    # データベースに接続
    conn = sqlite3.connect('db/syllabus.db')
    cursor = conn.cursor()

    try:
        # syllabus_timeテーブルのレコードを削除
        print("Deleting all records from syllabus_time table...")
        cursor.execute("DELETE FROM syllabus_time;")
        conn.commit()
        print("All records deleted successfully.")

        # 新しいデータを登録
        print("\nInserting new records...")
        json_files = glob("db/updates/syllabus_time/add/*.json")
        for file_path in json_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                content = data['content']
                
                # 時限のリストを処理
                for period in content['periods']:
                    cursor.execute(
                        "INSERT INTO syllabus_time (subject_code, day_of_week, period, created_at) VALUES (?, ?, ?, ?)",
                        (content['subject_code'], content['day_of_week'], period, content['created_at'])
                    )
            
            print(f"Processed: {os.path.basename(file_path)}")
        
        conn.commit()
        print("\nAll records inserted successfully.")

    except Exception as e:
        print(f"Error: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    reset_syllabus_time() 