#!/usr/bin/env python3
# File Version: v2.7.0
# Project Version: v2.7.0
# Last Updated: 2025-07-06
"""
SQLファイルからWHERE句のjsonb条件を日本語で意訳し、YAMLツリーとして出力するスクリプト。
現状はmath_noexam.sql専用テンプレート。
"""
import sys
import yaml

def parse_math_noexam_sql(sql_text):
	tree = {
		"履修情報一覧": [
			{
				"履修要綱一覧": [
					{"学部課程": '"数理" を含む'},
					{"必須度": '"必修"'},
					{"科目区分": '"数学" または "数理"'},
					{"科目小区分": '"数学" または "数理"'}
				]
			}
		],
		"開講情報一覧": [
			{
				"シラバス一覧": [
					{"担当教員一覧": "氏名を抽出"},
					{"成績評価基準一覧": '空 or 項目に "試験" を含まない'},
					{"対象学部課程一覧": '"数理" を含む'}
				]
			}
		]
	}
	return tree

def main(sql_file):
	with open(sql_file, encoding='utf-8') as f:
		sql_text = f.read()
	tree = parse_math_noexam_sql(sql_text)
	print(yaml.dump(tree, allow_unicode=True, sort_keys=False))

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print("使い方: python sql_where_yaml.py <sqlファイル>")
		sys.exit(1)
	main(sys.argv[1]) 