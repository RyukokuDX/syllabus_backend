import json
import os
from datetime import datetime
from pathlib import Path

def read_json_files(directory):
    """指定されたディレクトリ内のすべてのJSONファイルを読み込む"""
    data = []
    for file in Path(directory).glob('*.json'):
        with open(file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            data.append(json_data['content'])
    return data

def generate_sql_insert(table_name, records):
    """SQLのINSERT文を生成する"""
    if not records:
        return ""

    # カラム名を取得
    columns = records[0].keys()
    columns_str = ', '.join(columns)

    # VALUES句を生成
    values = []
    for record in records:
        values_list = []
        for column in columns:
            value = record[column]
            if value is None:
                values_list.append('NULL')
            elif isinstance(value, (int, float)):
                values_list.append(str(value))
            else:
                values_list.append(f"'{value}'")
        values.append(f"    ({', '.join(values_list)})")

    values_str = ',\n'.join(values)

<<<<<<< HEAD
    # ON CONFLICT句を生成
    update_columns = [col for col in columns if col not in ['subject_code', 'created_at']]
    update_str = ',\n    '.join([f"{col} = EXCLUDED.{col}" for col in update_columns])
=======
    # テーブルごとのON CONFLICT句を設定
    conflict_columns = {
        'subject': ['subject_code'],
        'syllabus': ['subject_code', 'year', 'term'],
        'syllabus_time': ['subject_code', 'day_of_week', 'period'],
        'instructor': ['instructor_code'],
        'syllabus_instructor': ['subject_code', 'instructor_code'],
        'lecture_session': ['subject_code', 'session_number'],
        'book': ['isbn'],
        'syllabus_textbook': ['subject_code', 'book_id'],
        'syllabus_reference': ['subject_code', 'book_id'],
        'grading_criterion': ['subject_code', 'criteria_type'],
        'syllabus_faculty': ['subject_code', 'faculty']
    }
    
    # 更新対象のカラムを設定
    update_columns = {
        'subject': [col for col in columns if col not in ['subject_code', 'created_at']],
        'syllabus': [col for col in columns if col not in ['subject_code', 'year', 'term', 'created_at']],
        'syllabus_time': [col for col in columns if col not in ['subject_code', 'day_of_week', 'period', 'created_at']],
        'instructor': [col for col in columns if col not in ['instructor_code', 'created_at']],
        'syllabus_instructor': [col for col in columns if col not in ['subject_code', 'instructor_code', 'created_at']],
        'lecture_session': [col for col in columns if col not in ['subject_code', 'session_number', 'created_at']],
        'book': [col for col in columns if col not in ['isbn', 'created_at']],
        'syllabus_textbook': [col for col in columns if col not in ['subject_code', 'book_id', 'created_at']],
        'syllabus_reference': [col for col in columns if col not in ['subject_code', 'book_id', 'created_at']],
        'grading_criterion': [col for col in columns if col not in ['subject_code', 'criteria_type', 'created_at']],
        'syllabus_faculty': [col for col in columns if col not in ['subject_code', 'faculty', 'created_at']]
    }

    # ON CONFLICT句を生成
    conflict_cols = conflict_columns.get(table_name, ['subject_code'])
    update_cols = update_columns.get(table_name, [col for col in columns if col not in ['subject_code', 'created_at']])
    
    conflict_str = ', '.join(conflict_cols)
    update_str = ',\n    '.join([f"{col} = EXCLUDED.{col}" for col in update_cols])
>>>>>>> fujiwara/feature/postgre
    update_str += ",\n    updated_at = CURRENT_TIMESTAMP"

    sql = f"""-- {table_name} テーブルへのデータ挿入
INSERT INTO {table_name} (
    {columns_str}
) VALUES
{values_str}
<<<<<<< HEAD
ON CONFLICT (subject_code) DO UPDATE SET
=======
ON CONFLICT ({conflict_str}) DO UPDATE SET
>>>>>>> fujiwara/feature/postgre
    {update_str};
"""
    return sql

def main():
    # プロジェクトルートからの相対パス
    project_root = Path(__file__).parent.parent.parent.parent
    
<<<<<<< HEAD
    # JSONファイルのディレクトリ
    json_dir = project_root / 'db' / 'updates' / 'subject' / 'add'
    
    # 出力先ディレクトリ
    output_dir = project_root / 'docker' / 'postgre' / 'init' / 'migrations'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # JSONデータを読み込む
    records = read_json_files(json_dir)
    
    # SQL生成
    sql = generate_sql_insert('subject', records)
    
    # ファイルに書き出し
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    output_file = output_dir / f'V{timestamp}__insert_subjects.sql'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(sql)
    
    print(f'Generated migration file: {output_file}')
=======
    # 処理対象のディレクトリとテーブル名のマッピング
    targets = [
        {
            'json_dir': project_root / 'updates' / 'subject' / 'add',
            'table_name': 'subject',
            'source': 'syllabus_search'
        },
        {
            'json_dir': project_root / 'updates' / 'syllabus' / 'add',
            'table_name': 'syllabus',
            'source': 'web_syllabus'
        },
        {
            'json_dir': project_root / 'updates' / 'syllabus_time' / 'add',
            'table_name': 'syllabus_time',
            'source': 'web_syllabus'
        },
        {
            'json_dir': project_root / 'updates' / 'instructor' / 'add',
            'table_name': 'instructor',
            'source': 'web_syllabus'
        },
        {
            'json_dir': project_root / 'updates' / 'syllabus_instructor' / 'add',
            'table_name': 'syllabus_instructor',
            'source': 'web_syllabus'
        },
        {
            'json_dir': project_root / 'updates' / 'lecture_session' / 'add',
            'table_name': 'lecture_session',
            'source': 'web_syllabus'
        },
        {
            'json_dir': project_root / 'updates' / 'book' / 'add',
            'table_name': 'book',
            'source': 'web_syllabus'
        },
        {
            'json_dir': project_root / 'updates' / 'syllabus_textbook' / 'add',
            'table_name': 'syllabus_textbook',
            'source': 'web_syllabus'
        },
        {
            'json_dir': project_root / 'updates' / 'syllabus_reference' / 'add',
            'table_name': 'syllabus_reference',
            'source': 'web_syllabus'
        },
        {
            'json_dir': project_root / 'updates' / 'grading_criterion' / 'add',
            'table_name': 'grading_criterion',
            'source': 'web_syllabus'
        },
        {
            'json_dir': project_root / 'updates' / 'syllabus_faculty' / 'add',
            'table_name': 'syllabus_faculty',
            'source': 'web_syllabus'
        }
    ]
    
    # 出力先ディレクトリ
    output_dir = project_root / 'docker' / 'postgresql' / 'init' / 'migrations'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for target in targets:
        if not target['json_dir'].exists():
            print(f"Skipping {target['json_dir']} as it doesn't exist")
            continue
            
        # JSONデータを読み込む
        records = read_json_files(target['json_dir'])
        if not records:
            print(f"No JSON files found in {target['json_dir']}")
            continue
        
        # SQL生成
        sql = generate_sql_insert(target['table_name'], records)
        
        # ファイルに書き出し
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        output_file = output_dir / f'V{timestamp}__insert_{target["table_name"]}s.sql'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(sql)
        
        # 使用したJSONファイルを移動
        registered_dir = project_root / 'updates' / target['table_name'] / 'registered' / output_file.stem
        registered_dir.mkdir(parents=True, exist_ok=True)
        
        for json_file in target['json_dir'].glob('*.json'):
            json_file.rename(registered_dir / json_file.name)
        
        print(f'Generated migration file: {output_file}')
        print(f'Moved JSON files to: {registered_dir}')
>>>>>>> fujiwara/feature/postgre

if __name__ == '__main__':
    main() 