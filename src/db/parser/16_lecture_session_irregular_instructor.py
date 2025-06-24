# -*- coding: utf-8 -*-
# File Version: v1.0.3
# Project Version: v1.3.34
# Last Updated: 2025/6/23

import os
import json
import sys
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import re
from tqdm import tqdm
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import unicodedata
import csv

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

try:
	from utils import normalize_subject_name, get_db_connection, get_syllabus_master_id_from_db, process_session_data
except ImportError:
	def normalize_subject_name(text: str) -> str:
		return unicodedata.normalize('NFKC', text)
	def get_db_connection():
		user = os.getenv('POSTGRES_USER', 'postgres')
		password = os.getenv('POSTGRES_PASSWORD', 'postgres')
		host = os.getenv('POSTGRES_HOST', 'localhost')
		port = os.getenv('POSTGRES_PORT', '5432')
		db = os.getenv('POSTGRES_DB', 'syllabus_db')
		connection_string = f"postgresql://{user}:{password}@{host}:{port}/{db}"
		engine = create_engine(connection_string, connect_args={'options': '-c client_encoding=utf-8'})
		Session = sessionmaker(bind=engine)
		session = Session()
		session.execute(text("SET client_encoding TO 'utf-8'"))
		session.commit()
		return session
	def get_syllabus_master_id_from_db(session, syllabus_code: str, syllabus_year: int) -> int:
		query = text("""
			SELECT syllabus_id FROM syllabus_master WHERE syllabus_code = :code AND syllabus_year = :year
		""")
		result = session.execute(query, {"code": syllabus_code, "year": syllabus_year}).first()
		return result[0] if result else None
	def process_session_data(session_text: str) -> tuple[bool, int, str]:
		"""フォールバック関数"""
		return False, 0, ""

def get_instructor_id_from_db(session, instructor_name: str) -> Optional[int]:
	try:
		normalized_name = normalize_subject_name(instructor_name)
		query = text("SELECT instructor_id FROM instructor WHERE name = :name")
		result = session.execute(query, {"name": normalized_name}).first()
		return result[0] if result else None
	except Exception as e:
		tqdm.write(f"[DB接続エラー] instructor取得時にエラー: {e}")
		session.rollback()
		return None

def get_lecture_session_irregular_id_from_db(session, syllabus_id: int, session_pattern: str) -> Optional[int]:
	try:
		# 正規化せずにそのまま検索（データベースのsession_patternは正規化されていないため）
		query = text("""
			SELECT lecture_session_irregular_id FROM lecture_session_irregular WHERE syllabus_id = :syllabus_id AND session_pattern = :session_pattern
		""")
		result = session.execute(query, {"syllabus_id": syllabus_id, "session_pattern": session_pattern}).first()
		return result[0] if result else None
	except Exception as e:
		tqdm.write(f"[DB接続エラー] lecture_session_irregular取得時にエラー: {e}")
		session.rollback()
		return None

def get_lecture_session_id_from_db(session, syllabus_id: int) -> Optional[int]:
	"""syllabus_idがlecture_sessionテーブルに存在するか確認"""
	try:
		query = text("""
			SELECT lecture_session_id FROM lecture_session WHERE syllabus_id = :syllabus_id
		""")
		result = session.execute(query, {"syllabus_id": syllabus_id}).first()
		return result[0] if result else None
	except Exception as e:
		tqdm.write(f"[DB接続エラー] lecture_session取得時にエラー: {e}")
		session.rollback()
		return None

def get_current_year() -> int:
	return datetime.now().year

def get_year_from_user() -> int:
	while True:
		try:
			year = input("年を入力してください（空の場合は現在の年）: ").strip()
			if not year:
				return get_current_year()
			year = int(year)
			if 2000 <= year <= 2100:
				return year
			print("2000年から2100年の間で入力してください")
		except ValueError:
			print("正しい数値を入力してください")

def get_json_files(year: int) -> List[str]:
	json_dir = os.path.join("src", "syllabus", str(year), "json")
	json_files = []
	if os.path.exists(json_dir):
		for file in os.listdir(json_dir):
			if file.endswith('.json'):
				json_files.append(os.path.join(json_dir, file))
	return json_files

def extract_instructors_from_schedule(schedule_data: List[Dict]) -> Tuple[List[Dict], int]:
	"""スケジュールデータから不規則セッションの担当者のみを抽出し、分割件数も返す"""
	results = []
	total_instructor_count = 0
	if not schedule_data:
		return results, total_instructor_count
	# リスト内に1件でも不規則なレコードがあるかをチェック
	has_irregular = False
	for session_data in schedule_data:
		if not isinstance(session_data, dict):
			continue
		session = session_data.get("session", "")
		if not session:
			continue
		# 不規則セッションかどうかを判定
		is_regular, _, _ = process_session_data(session)
		if not is_regular:
			has_irregular = True
			break
	# リスト内に不規則なレコードがない場合は空のリストを返す
	if not has_irregular:
		return results, total_instructor_count
	# リスト全体が不規則として扱われるため、すべてのセッションを処理
	for session_data in schedule_data:
		if not isinstance(session_data, dict):
			continue
		# セッション情報を取得
		session = session_data.get("session", "")
		if not session:
			continue
		# セッションデータを処理
		is_regular, _, session_pattern = process_session_data(session)
		# 正規セッションの場合はスキップ
		if is_regular:
			continue
		# 担当者情報を取得
		instructor = session_data.get("instructor", "")
		if not instructor:
			continue
		# 担当者名を分割（複数人の場合）
		instructor_names = []
		if instructor:
			# 区切り文字で分割（カンマ、セミコロン、改行など）
			split_pattern = r'[,;、；\n\r]+'
			instructor_names = [name.strip() for name in re.split(split_pattern, instructor) if name.strip()]
		if instructor_names:
			results.append({
				'syllabus_id': None,  # 後で設定
				'session_pattern': session_pattern,
				'instructor_names': instructor_names
			})
			total_instructor_count += len(instructor_names)
	return results, total_instructor_count

def extract_lecture_session_irregular_instructor_from_single_json(json_data: Dict, session, year: int, json_file: str) -> tuple[List[Dict], List[str], int]:
	lecture_session_irregular_instructors = []
	errors = []
	total_instructor_count = 0
	try:
		syllabus_code = json_data.get('科目コード')
		syllabus_year = year
		if not syllabus_code:
			errors.append(f"科目コードが見つかりません: {json_file}")
			return lecture_session_irregular_instructors, errors, total_instructor_count
		syllabus_master_id = get_syllabus_master_id_from_db(session, syllabus_code, syllabus_year)
		if not syllabus_master_id:
			errors.append(f"シラバスマスターIDが見つかりません: {syllabus_code} ({syllabus_year})")
			return lecture_session_irregular_instructors, errors, total_instructor_count
		schedule_data = json_data.get('講義計画', {}).get('内容', {}).get('schedule', [])
		# スケジュールデータから担当者を抽出（分割件数も取得）
		instructors, instructor_count = extract_instructors_from_schedule(schedule_data)
		total_instructor_count += instructor_count
		for instructor_data in instructors:
			session_pattern = instructor_data['session_pattern']
			instructor_names = instructor_data['instructor_names']
			lecture_session_irregular_id = get_lecture_session_irregular_id_from_db(session, syllabus_master_id, session_pattern)
			if not lecture_session_irregular_id:
				lecture_session_id = get_lecture_session_id_from_db(session, syllabus_master_id)
				if lecture_session_id:
					continue
				else:
					errors.append(f"lecture_session_irregular_idが見つかりません: {syllabus_code} パターン[{session_pattern}]")
					continue
			# instructorがNoneや空文字の場合もエラー
			if not instructor_names or all(not name.strip() for name in instructor_names):
				errors.append(f"instructorが未設定: {syllabus_code} パターン[{session_pattern}]")
				continue
			for name in instructor_names:
				instructor_id = get_instructor_id_from_db(session, name)
				if not instructor_id:
					errors.append(f"instructor_idが見つかりません: {name} ({syllabus_code} パターン[{session_pattern}])")
					continue
				lecture_session_irregular_instructors.append({
					'lecture_session_irregular_id': lecture_session_irregular_id,
					'instructor_id': instructor_id,
					'role': '担当'
				})
	except Exception as e:
		error_msg = f"エラーが発生しました: {str(e)}"
		if 'syllabus_code' in locals():
			error_msg = f"科目コード {syllabus_code}: {error_msg}"
		tqdm.write(f"        EXTRACT ERROR: {error_msg}")
		errors.append(error_msg)
	return lecture_session_irregular_instructors, errors, total_instructor_count

def process_lecture_session_irregular_instructor_json(json_file: str, session, year: int) -> tuple[List[Dict], List[str], int]:
	all_lecture_session_irregular_instructors = []
	all_errors = []
	total_instructor_count = 0
	try:
		with open(json_file, 'r', encoding='utf-8') as f:
			json_data = json.load(f)
		lecture_session_irregular_instructors, errors, instructor_count = extract_lecture_session_irregular_instructor_from_single_json(json_data, session, year, json_file)
		all_lecture_session_irregular_instructors.extend(lecture_session_irregular_instructors)
		all_errors.extend(errors)
		total_instructor_count += instructor_count
	except Exception as e:
		all_errors.append(f"ファイル読み込みエラー {json_file}: {str(e)}")
	return all_lecture_session_irregular_instructors, all_errors, total_instructor_count

def main():
	"""メイン処理"""
	print("講義セッション担当者情報抽出処理を開始します...")
	
	# 年を取得
	year = get_year_from_user()
	
	# JSONファイル一覧を取得
	json_files = get_json_files(year)
	if not json_files:
		print(f"{year}年のJSONファイルが見つかりません")
		return
	
	# データベース接続
	try:
		session = get_db_connection()
	except Exception as e:
		print(f"データベース接続エラー: {str(e)}")
		return
	
	# 統計情報の初期化
	stats = {
		'total_files': len(json_files),
		'processed_files': 0,
		'total_items': 0,
		'valid_items': 0,
		'error_items': 0,
		'specific_errors': {}
	}
	
	# 出力ファイルの準備
	timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
	
	# 講義セッション担当者用ファイル
	irregular_instructor_dir = os.path.join("updates", "lecture_session_irregular_instructor", "add")
	os.makedirs(irregular_instructor_dir, exist_ok=True)
	irregular_instructor_file = os.path.join(irregular_instructor_dir, f"lecture_session_irregular_instructor_{timestamp}.json")
	
	# エラー情報用ファイル
	error_dir = os.path.join("warning", str(year))
	os.makedirs(error_dir, exist_ok=True)
	error_file = os.path.join(error_dir, f"lecture_session_irregular_{timestamp[:-3]}.csv")
	
	# ファイルを開いて書き込み開始
	irregular_instructor_count = 0
	all_errors = []
	all_total_instructor_count = 0
	
	# 講義セッション担当者ファイルを開く
	instructor_f = open(irregular_instructor_file, 'w', encoding='utf-8')
	instructor_f.write('[\n')
	instructor_first = True
	
	try:
		# 処理開始時のメッセージ
		tqdm.write(f"\n{'='*60}")
		tqdm.write(f"講義セッション担当者情報抽出処理 - 対象年度: {year}")
		tqdm.write(f"{'='*60}")
		
		for i, json_file in enumerate(tqdm(json_files, desc="JSONファイル処理中", unit="file")):
			try:
				with open(json_file, 'r', encoding='utf-8') as f:
					json_data = json.load(f)
				
				lecture_session_irregular_instructors, errors, instructor_count = process_lecture_session_irregular_instructor_json(json_file, session, year)
				
				# 統計情報の更新
				stats['processed_files'] += 1
				stats['total_items'] += len(lecture_session_irregular_instructors)
				stats['valid_items'] += len(lecture_session_irregular_instructors)
				stats['error_items'] += len(errors)
				
				# 講義セッション担当者を書き込み
				for instructor_data in lecture_session_irregular_instructors:
					if not instructor_first:
						instructor_f.write(',\n')
					json.dump(instructor_data, instructor_f, ensure_ascii=False, indent=2)
					instructor_first = False
					irregular_instructor_count += 1
				
				all_errors.extend(errors)
				all_total_instructor_count += instructor_count
				
			except Exception as e:
				error_msg = f"ファイル読み込みエラー {json_file}: {str(e)}"
				tqdm.write(f"エラー: {error_msg}")
				all_errors.append(error_msg)
				stats['error_items'] += 1
		
		# ファイルを閉じる
		instructor_f.write('\n]')
		instructor_f.close()
		
	except Exception as e:
		# エラーが発生した場合もファイルを閉じる
		try:
			instructor_f.close()
		except:
			pass
		raise e
	
	# 最終統計の表示
	tqdm.write("\n" + "="*60)
	tqdm.write("処理完了 - 統計情報")
	tqdm.write("="*60)
	tqdm.write(f"総ファイル数: {stats['total_files']}")
	tqdm.write(f"処理済みファイル数: {stats['processed_files']}")
	tqdm.write(f"総データ数: {stats['total_items']}")
	tqdm.write(f"正常データ数: {stats['valid_items']}")
	tqdm.write(f"エラーデータ数: {stats['error_items']}")
	tqdm.write("="*60)
	
	# 結果サマリーの表示
	tqdm.write(f"\n{'='*60}")
	tqdm.write("📊 抽出結果サマリー")
	tqdm.write(f"{'='*60}")
	tqdm.write(f"✅ 講義セッション担当者: {irregular_instructor_count:,}件")
	tqdm.write(f"⚠️  エラーデータ: {len(all_errors)}件")
	tqdm.write(f"📈 合計: {irregular_instructor_count:,}件")
	tqdm.write(f"分割した担当者名の総数: {all_total_instructor_count}")
	
	# 結果を表示
	final_errors = []
	
	if irregular_instructor_count > 0:
		tqdm.write(f"講義セッション担当者情報を保存しました: {irregular_instructor_file}")
	else:
		final_errors.append("講義セッション担当者情報が見つかりませんでした")
	
	# エラー情報を保存
	if all_errors or final_errors:
		with open(error_file, 'w', encoding='utf-8', newline='') as f:
			writer = csv.writer(f)
			writer.writerow(['エラータイプ', 'エラー内容'])
			
			for error in all_errors:
				writer.writerow(['処理エラー', error])
			
			for error in final_errors:
				writer.writerow(['最終エラー', error])
		
		tqdm.write(f"エラー情報を保存しました: {error_file}")
	
	# セッションを閉じる
	session.close()
	
	tqdm.write("講義セッション担当者情報抽出処理が完了しました")

if __name__ == "__main__":
	main() 