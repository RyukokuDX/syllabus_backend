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

    # ON CONFLICT句を生成
    update_columns = [col for col in columns if col not in ['subject_code', 'created_at']]
    update_str = ',\n    '.join([f"{col} = EXCLUDED.{col}" for col in update_columns])
    update_str += ",\n    updated_at = CURRENT_TIMESTAMP"

    sql = f"""-- {table_name} テーブルへのデータ挿入
INSERT INTO {table_name} (
    {columns_str}
) VALUES
{values_str}
ON CONFLICT (subject_code) DO UPDATE SET
    {update_str};
"""
    return sql

def main():
    # プロジェクトルートからの相対パス
    project_root = Path(__file__).parent.parent.parent.parent
    
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

if __name__ == '__main__':
    main() 