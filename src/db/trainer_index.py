#!/usr/bin/env python3
# File Version: v1.0.2
# Project Version: v3.0.2
# Last Updated: 2025-07-09
"""
docs/doc.mdガイドライン準拠でtrainer_index.mdを生成
"""
import os
import re
import glob
import csv
from pathlib import Path
from datetime import date

TRAINER_SQL_DIR = Path('trainer/sql')
TRAINER_RESP_DIR = Path('trainer/response')
INDEX_MD = Path('docs/trainer_index.md')

PROJECT_VERSION = 'v3.0.1'
FILE_VERSION = 'v1.0.1'
TODAY = date.today().isoformat()

# YAML front matter風コメントを抽出
def parse_sql_meta(sql_path):
	meta = {}
	with open(sql_path, encoding='utf-8') as f:
		lines = f.readlines()
		if not lines or not lines[0].strip().startswith('-- ---'):
			return meta
		for line in lines[1:]:
			if line.strip().startswith('-- ---'):
				break
			m = re.match(r'--\s*([a-zA-Z0-9_]+):\s*(.*)', line)
			if m:
				key, value = m.group(1), m.group(2)
				meta[key] = value
	return meta

def count_tsv_rows(tsv_path):
	try:
		with open(tsv_path, encoding='utf-8') as f:
			reader = csv.reader(f, delimiter='\t')
			rows = list(reader)
			return max(0, len(rows)-1)  # ヘッダ除く
	except Exception:
		return 0

def main():
	rows = []
	for sql_file in sorted(TRAINER_SQL_DIR.glob('*.sql')):
		meta = parse_sql_meta(sql_file)
		order = meta.get('order', '')
		desc = meta.get('desc', '')
		response_id = meta.get('response_id', '')
		if response_id.endswith('.json'):
			resp_file = TRAINER_RESP_DIR / response_id.replace('.json', '.tsv')
		elif response_id.endswith('.tsv'):
			resp_file = TRAINER_RESP_DIR / response_id
		else:
			resp_file = TRAINER_RESP_DIR / (sql_file.stem + '.tsv')
		resp_link = f'[📄]({resp_file.as_posix()})' if resp_file.exists() else '-'
		resp_count = count_tsv_rows(resp_file) if resp_file.exists() else '-'
		rows.append({
			'order': order,
			'sql': f'[📄]({sql_file.as_posix()})',
			'response': resp_link,
			'count': resp_count,
			'desc': desc
		})

	with open(INDEX_MD, 'w', encoding='utf-8') as f:
		# YAML Front Matter
		f.write('---\n')
		f.write('title: トレーニングデータインデックス\n')
		f.write(f'file_version: {FILE_VERSION}\n')
		f.write(f'project_version: {PROJECT_VERSION}\n')
		f.write(f'last_updated: {TODAY}\n')
		f.write('---\n\n')

		# タイトル・バージョン情報
		f.write('# トレーニングデータインデックス\n\n')
		f.write(f'- File Version: {FILE_VERSION}\n')
		f.write(f'- Project Version: {PROJECT_VERSION}\n')
		f.write(f'- Last Updated: {TODAY}\n\n')

		# 関連ドキュメントへのリンク
		f.write('[ドキュメント作成ガイドラインへ](./doc.md)\n\n')

		# 目次
		f.write('## 目次\n')
		f.write('1. [概要](#概要)\n')
		f.write('2. [トレーニングデータ一覧](#トレーニングデータ一覧)\n')
		f.write('3. [ページトップへ](#トレーニングデータインデックス)\n\n')

		# 概要
		f.write('## 概要\n')
		f.write('本ドキュメントは、trainerディレクトリ配下の学習データ用SQL・レスポンスファイルの対応関係を一覧化したものです。\n')
		f.write('SQLファイルのYAML front matterコメントからorderやdesc等を抽出し、対応するレスポンスファイルの有無・件数も自動集計しています。\n\n')

		# 一覧
		f.write('## トレーニングデータ一覧\n\n')
		f.write('| order（自然言語クエリ） | SQLファイル | レスポンス |\n')
		f.write('|------------------------|------------|-----------|\n')
		for r in rows:
			f.write(f"| {r['order']} | {r['sql']} | {r['response']} |\n")

		# ページトップリンク
		f.write('\n[🔝 ページトップへ](#トレーニングデータインデックス)\n')

if __name__ == '__main__':
	main() 