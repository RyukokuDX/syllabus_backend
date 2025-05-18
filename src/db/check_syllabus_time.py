import sqlite3
import sys

def check_syllabus_time(subject_code):
    conn = sqlite3.connect('db/syllabus.db')
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT subject_code, day_of_week, period, created_at FROM syllabus_time WHERE subject_code = ?",
            (subject_code,)
        )
        rows = cursor.fetchall()

        if not rows:
            print(f"No records found for subject_code: {subject_code}")
            return

        print(f"\nFound {len(rows)} records for subject_code: {subject_code}")
        print("\nDay of week: 1=Monday, 2=Tuesday, 3=Wednesday, 4=Thursday, 5=Friday, 6=Saturday, 7=Sunday")
        print("\nRecords:")
        for row in rows:
            print(f"Subject Code: {row[0]}")
            print(f"Day of Week: {row[1]}")
            print(f"Period: {row[2]}")
            print(f"Created At: {row[3]}")
            print("-" * 50)

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        conn.close()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python check_syllabus_time.py <subject_code>")
        sys.exit(1)
    
    subject_code = sys.argv[1]
    check_syllabus_time(subject_code) 