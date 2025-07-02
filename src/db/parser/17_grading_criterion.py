# -*- coding: utf-8 -*-
# cursorはversionを弄るな
"""
# File Version: v2.2.0
# Project Version: v2.2.0
# Last Updated: 2025-07-02
"""

import os
import json
import glob
import csv
import re
from typing import List, Dict, Set, Tuple, Any, Optional
from datetime import datetime
from tqdm import tqdm
from .utils import get_year_from_user, get_db_connection, get_syllabus_master_id_from_db
from pathlib import Path
from sqlalchemy import text

def get_grading_criterion_info(year: int) -> List[Dict[str, Any]]:
	"""成績評価基準情報を取得する"""
	grading_criteria = []
	
	# 統計情報
	stats = {
		'total_files': 0,
		'processed_files': 0,
		'total_criteria': 0,
		'valid_criteria': 0,
		'files_with_criteria': 0
	}
	
	# データベース接続
	session = get_db_connection()
	
	try:
		# シラバスから成績評価基準情報を取得
		script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
		json_pattern = os.path.join(script_dir, 'syllabus', str(year), 'json', '*.json')
		
		json_files = glob.glob(json_pattern)
		stats['total_files'] = len(json_files)
		
		print(f"処理開始: {stats['total_files']}個のJSONファイルを処理します")
		
		for json_file in tqdm(json_files, desc="シラバスファイル処理中", unit="file"):
			try:
				with open(json_file, 'r', encoding='utf-8') as f:
					data = json.load(f)
				
				if '詳細情報' not in data:
					continue
					
				detail = data['詳細情報']
				syllabus_code = data.get('科目コード', '')
				
				# 基本情報から年度を取得
				basic_info = data.get("基本情報", {})
				syllabus_year = int(basic_info.get("開講年度", {}).get("内容", str(year)))
				
				# syllabus_masterからsyllabus_idを取得
				try:
					syllabus_id = get_syllabus_master_id_from_db(session, syllabus_code, syllabus_year)
					if not syllabus_id:
						continue
				except Exception as e:
					print(f"❌ 致命的なDB接続エラー: {e}")
					raise
				
				stats['processed_files'] += 1
				
				# 成績評価の方法情報の処理
				if '成績評価の方法' in detail and '内容' in detail['成績評価の方法'] and detail['成績評価の方法']['内容'] is not None:
					grading_content = detail['成績評価の方法']['内容']
					if isinstance(grading_content, dict) and '評価項目' in grading_content:
						criteria_list = grading_content['評価項目']
						if isinstance(criteria_list, list) and criteria_list:  # nullでない場合のみ処理
							stats['files_with_criteria'] += 1
							stats['total_criteria'] += len(criteria_list)
							
							# 評価項目処理の進捗を表示
							for criterion in tqdm(criteria_list, desc=f"評価項目処理中 ({syllabus_code})", leave=False):
								try:
									raw_criteria_type = criterion.get('項目', '')
									criteria_type = str(raw_criteria_type).strip() if raw_criteria_type is not None else ""
									ratio = None
									ratio_str = criterion.get('割合', '')
									if ratio_str and str(ratio_str).strip():
										try:
											ratio = int(ratio_str)
										except ValueError:
											pass
									raw_criteria_description = criterion.get('基準', '')
									criteria_description = str(raw_criteria_description).strip() if raw_criteria_description is not None else ""
									raw_note = criterion.get('備考', '')
									note = str(raw_note).strip() if raw_note is not None else ""
									now = datetime.now().isoformat()
									
									# 必須フィールドのチェック
									if not criteria_type:
										continue
									
									# 成績評価基準情報として登録
									grading_criterion_info = {
										'syllabus_id': syllabus_id,
										'criteria_type': criteria_type,
										'ratio': ratio,
										'criteria_description': criteria_description,
										'note': note,
										'created_at': now
									}
									grading_criteria.append(grading_criterion_info)
									stats['valid_criteria'] += 1
								except Exception as e:
									print(f"❌ 項目処理エラー ({syllabus_code}): {str(e)}")
									import traceback
									print(f"📋 エラーの詳細: {traceback.format_exc()}")
									continue
			except Exception as e:
				continue
		
		# 最終統計の表示
		print("\n" + "="*60)
		print("処理完了 - 統計情報")
		print("="*60)
		print(f"総ファイル数: {stats['total_files']}")
		print(f"処理済みファイル数: {stats['processed_files']}")
		print(f"評価項目ありファイル数: {stats['files_with_criteria']}")
		print(f"総評価項目数: {stats['total_criteria']}")
		print(f"有効評価項目数: {stats['valid_criteria']}")
		print("="*60)
		
		return grading_criteria
		
	except Exception as e:
		print(f"成績評価基準情報取得中にエラーが発生しました: {str(e)}")
		import traceback
		print(f"エラーの詳細: {traceback.format_exc()}")
		return grading_criteria
	finally:
		# データベース接続を閉じる
		if session:
			session.close()

def create_grading_criterion_json(grading_criteria: List[Dict[str, Any]]) -> str:
	"""成績評価基準情報のJSONファイルを作成する"""
	output_dir = os.path.join("updates", "grading_criterion", "add")
	os.makedirs(output_dir, exist_ok=True)
	
	# 現在の日時を取得してファイル名を生成
	current_time = datetime.now()
	filename = f"grading_criterion_{current_time.strftime('%Y%m%d_%H%M')}.json"
	output_file = os.path.join(output_dir, filename)
	
	data = {
		"grading_criteria": [{
			"syllabus_id": criterion["syllabus_id"],
			"criteria_type": criterion["criteria_type"],
			"ratio": criterion["ratio"],
			"criteria_description": criterion["criteria_description"],
			"note": criterion["note"],
			"created_at": criterion["created_at"]
		} for criterion in sorted(grading_criteria, key=lambda x: (x["syllabus_id"], x["criteria_type"]))]
	}
	
	with open(output_file, 'w', encoding='utf-8') as f:
		json.dump(data, f, ensure_ascii=False, indent=2)
	
	return output_file

def main():
	"""メイン処理"""
	session = None
	try:
		# 年度の取得
		year = get_year_from_user()
		print(f"\n{'='*60}")
		print(f"成績評価基準情報抽出処理開始 - 対象年度: {year}")
		print(f"{'='*60}")
		
		# 成績評価基準情報の取得
		print("\n📊 成績評価基準情報の取得を開始します...")
		grading_criteria = get_grading_criterion_info(year)
		
		# 結果サマリー
		print(f"\n{'='*60}")
		print("📊 抽出結果サマリー")
		print(f"{'='*60}")
		print(f"✅ 成績評価基準: {len(grading_criteria)}件")
		print(f"📈 合計: {len(grading_criteria)}件")
		
		# JSONファイルの作成
		print(f"\n💾 JSONファイルの作成を開始します...")
		if grading_criteria:
			grading_criterion_output_file = create_grading_criterion_json(grading_criteria)
			print(f"✅ 成績評価基準JSONファイルを作成しました: {grading_criterion_output_file}")
		else:
			print("ℹ️  成績評価基準は0件でした")
		
		print(f"\n{'='*60}")
		print("🎉 処理が完了しました！")
		print(f"{'='*60}")
		
	except Exception as e:
		print(f"\n❌ エラーが発生しました: {str(e)}")
		import traceback
		print(f"📋 エラーの詳細: {traceback.format_exc()}")
		raise
	finally:
		# データベース接続を閉じる
		if session:
			session.close()

if __name__ == "__main__":
	# メイン処理
	main() 