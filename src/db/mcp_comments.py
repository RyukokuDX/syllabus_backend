# File Version: v3.0.0
# Project Version: v3.0.0
# Last Updated: 2025-07-08

"""
DBテーブル・カラムのコメントSQL（COMMENT ON ...）を生成し、
docker/postgresql/migrations_dev/Vyyyymmddhhmmss_insert_comments_for_mcp.sql
として出力するスクリプト。

- docs/database/structure.md を参照
- docker/postgresql/init/init.sql.template の現状DB構造に対応
"""

import re
import os
from pathlib import Path
from datetime import datetime
import csv
import sqlite3
import psycopg2

STRUCTURE_MD = Path('docs/database/structure.md')
INIT_SQL = Path('docker/postgresql/init/init.sql.template')
MIGRATIONS_DEV = Path('docker/postgresql/migrations_dev')

# テーブル名の正規化
TABLE_NAME_MAP = {
	'class': 'class',
	'subclass': 'subclass',
	'faculty': 'faculty',
	'subject_name': 'subject_name',
	'instructor': 'instructor',
	'book': 'book',
	'book_uncategorized': 'book_uncategorized',
	'syllabus_master': 'syllabus_master',
	'syllabus': 'syllabus',
	'subject_grade': 'subject_grade',
	'lecture_time': 'lecture_time',
	'lecture_session': 'lecture_session',
	'lecture_session_irregular': 'lecture_session_irregular',
	'syllabus_instructor': 'syllabus_instructor',
	'lecture_session_instructor': 'lecture_session_instructor',
	'syllabus_book': 'syllabus_book',
	'grading_criterion': 'grading_criterion',
	'subject_attribute': 'subject_attribute',
	'subject': 'subject',
	'subject_attribute_value': 'subject_attribute_value',
	'syllabus_faculty': 'syllabus_faculty',
	'syllabus_study_system': 'syllabus_study_system',
}

def parse_structure_md():
	"""
	structure.mdからテーブル・カラムの説明を抽出
	戻り値: {table: {desc: str, columns: {col: desc}}}
	"""
	table_info = {}
	with open(STRUCTURE_MD, encoding='utf-8') as f:
		lines = f.readlines()

	table = None
	col_mode = False
	for i, line in enumerate(lines):
		# テーブル名
		m = re.match(r'### ([a-zA-Z0-9_]+) ', line)
		if m:
			table = m.group(1)
			table_info[table] = {'desc': '', 'columns': {}}
			col_mode = False
			continue
		# テーブル概要
		if table and 'テーブル概要' in line:
			desc = lines[i+1].strip()
			table_info[table]['desc'] = desc
		# カラム定義
		if table and 'カラム定義' in line:
			col_mode = True
			col_start = i+3
			j = col_start
			while j < len(lines):
				if lines[j].startswith('|') and not lines[j].startswith('|---'):
					parts = [x.strip() for x in lines[j].strip().split('|')[1:-1]]
					if len(parts) >= 4:
						col, _, _, desc = parts[:4]
						table_info[table]['columns'][col] = desc
					j += 1
				else:
					break
			col_mode = False
	return table_info

def generate_comment_sql(table_info):
	"""
	COMMENT ON ... SQL生成
	"""
	sql = []
	for table, info in table_info.items():
		table_sql = f"COMMENT ON TABLE {table} IS '{info['desc']}';"
		sql.append(table_sql)
		for col, desc in info['columns'].items():
			col_sql = f"COMMENT ON COLUMN {table}.{col} IS '{desc}';"
			sql.append(col_sql)
	return '\n'.join(sql)

def export_attribute_catalog():
	"""
	subject_attributeテーブルのカタログCSVを出力
	"""
	# DB接続情報は環境や要件に応じて調整してください
	# ここではPostgreSQLではなくsqlite3例（必要に応じてpsycopg2等に変更）
	# 例: conn = psycopg2.connect(...)
	try:
		conn = sqlite3.connect('syllabus.db')  # 仮のDB名
		table = 'subject_attribute'
		cur = conn.cursor()
		cur.execute(f'SELECT attribute_id, attribute_name, description FROM {table}')
		rows = cur.fetchall()
		with open('mcp_attribute_catalog.csv', 'w', encoding='utf-8', newline='') as f:
			writer = csv.writer(f)
			writer.writerow(['attribute_id', 'attribute_name', 'description'])
			for row in rows:
				writer.writerow(row)
		print('EAVカタログCSV: mcp_attribute_catalog.csv を出力しました')
	finally:
		conn.close()

def export_eav_catalog_as_comment():
	"""
	EAVカタログ（subject_attributeごとに全subject_attribute_valueのユニークな値のみをSQLコメントとして出力）
	"""
	# DB接続情報は環境変数や設定ファイルから取得してください
	conn = psycopg2.connect(
		dbname='syllabus_db', user='postgres', password='postgres', host='localhost', port=5432
	)
	cur = conn.cursor()
	# 属性一覧取得
	cur.execute("SELECT attribute_id, attribute_name, COALESCE(description, '') FROM subject_attribute ORDER BY attribute_id")
	attributes = cur.fetchall()
	# 各属性ごとに値一覧取得
	lines = []
	lines.append('-- ==========================================')
	lines.append('-- EAVカタログ（subject_attributeごとの全値一覧）')
	for attr_id, attr_name, desc in attributes:
		lines.append(f"-- attribute_id: {attr_id}, attribute_name: {attr_name}, description: {desc}")
		cur.execute('''
			SELECT DISTINCT v.value
			FROM subject_attribute_value v
			WHERE v.attribute_id = %s
			ORDER BY v.value
		''', (attr_id,))
		for (value,) in cur.fetchall():
			if value is None:
				continue
			val = str(value).strip()
			if val == '' or val.lower() in {'なし', '不明', 'null', 'none'}:
				continue
			lines.append(f"--   value: {val}")
	lines.append('-- ==========================================')
	cur.close()
	conn.close()
	return '\n'.join(lines)

def main():
	table_info = parse_structure_md()
	sql = generate_comment_sql(table_info)
	# EAVカタログコメント生成
	eav_comment = export_eav_catalog_as_comment()
	# ファイル名生成
	dt = datetime.now().strftime('%Y%m%d%H%M%S')
	out_path = MIGRATIONS_DEV / f'V{dt}_insert_comments_for_mcp.sql'
	MIGRATIONS_DEV.mkdir(parents=True, exist_ok=True)
	with open(out_path, 'w', encoding='utf-8') as f:
		f.write('-- DBテーブル・カラムコメント（mcp用）\n')
		f.write(eav_comment + '\n')
		f.write(sql)
	print(f'コメントSQLを {out_path} に出力しました')

if __name__ == '__main__':
	main() 