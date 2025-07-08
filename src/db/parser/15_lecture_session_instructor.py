# -*- coding: utf-8 -*-
# File Version: v3.0.0
# Project Version: v3.0.0
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

# 現在のディレクトリのPythonパッケージをインポート
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# utils.pyから関数をインポート
try:
	from utils import normalize_subject_name, get_db_connection, get_syllabus_master_id_from_db, process_session_data, is_regular_session_list
except ImportError:
	# utils.pyが見つからない場合のフォールバック関数
	def normalize_subject_name(text: str) -> str:
		"""文字列を正規化する関数"""
		return unicodedata.normalize('NFKC', text)
	
	def get_db_connection():
		"""データベース接続を取得する"""
		# 環境変数から接続情報を取得
		user = os.getenv('POSTGRES_USER', 'postgres')
		password = os.getenv('POSTGRES_PASSWORD', 'postgres')
		host = os.getenv('POSTGRES_HOST', 'localhost')
		port = os.getenv('POSTGRES_PORT', '5432')
		db = os.getenv('POSTGRES_DB', 'syllabus_db')

		# 接続文字列を作成
		connection_string = f"postgresql://{user}:{password}@{host}:{port}/{db}"
		
		# エンジンを作成
		engine = create_engine(
			connection_string,
			connect_args={
				'options': '-c client_encoding=utf-8'
			}
		)
		
		# セッションを作成
		Session = sessionmaker(bind=engine)
		session = Session()
		
		# セッション作成後にエンコーディングを設定
		session.execute(text("SET client_encoding TO 'utf-8'"))
		session.commit()
		
		return session
	
	def get_syllabus_master_id_from_db(session, syllabus_code: str, syllabus_year: int) -> int:
		"""シラバスマスターのIDを取得する"""
		try:
			# シラバスマスターのIDを検索
			query = text("""
				SELECT syllabus_id 
				FROM syllabus_master 
				WHERE syllabus_code = :code 
				AND syllabus_year = :year
			""")
			
			result = session.execute(
				query,
				{"code": syllabus_code, "year": syllabus_year}
			).first()
			
			return result[0] if result else None
		except Exception as e:
			print(f"データベースエラー: {syllabus_code} ({syllabus_year}) - {str(e)}")
			session.rollback()
			return None
	
	def process_session_data(session_text: str) -> tuple[bool, int, str, Optional[str]]:
		"""フォールバック関数"""
		return False, 0, "", None

def get_instructor_id_from_db(session, instructor_name: str) -> Optional[int]:
	"""教員名からinstructor_idを取得する"""
	try:
		# 教員名を正規化
		normalized_name = normalize_subject_name(instructor_name)
		
		# instructorテーブルから教員IDを検索
		query = text("""
			SELECT instructor_id 
			FROM instructor 
			WHERE name = :name
		""")
		
		result = session.execute(
			query,
			{"name": normalized_name}
		).first()
		
		return result[0] if result else None
	except Exception as e:
		tqdm.write(f"[DB接続エラー] instructor取得時にエラー: {e}")
		session.rollback()
		return None

def get_lecture_session_id_from_db(session, syllabus_id: int, session_number: int) -> Optional[int]:
	"""シラバスIDと回数からlecture_session_idを取得する"""
	try:
		query = text("""
			SELECT lecture_session_id 
			FROM lecture_session 
			WHERE syllabus_id = :syllabus_id 
			AND session_number = :session_number
		""")
		
		result = session.execute(
			query,
			{"syllabus_id": syllabus_id, "session_number": session_number}
		).first()
		
		return result[0] if result else None
	except Exception as e:
		tqdm.write(f"[DB接続エラー] lecture_session取得時にエラー: {e}")
		session.rollback()
		return None

def get_lecture_session_max_id_from_db(session) -> Optional[int]:
	"""lecture_sessionテーブルの最大IDを取得する"""
	try:
		query = text("""
			SELECT MAX(lecture_session_id) 
			FROM lecture_session
		""")
		
		result = session.execute(query).first()
		
		return result[0] if result and result[0] else None
	except Exception as e:
		tqdm.write(f"[DB接続エラー] lecture_session最大ID取得時にエラー: {e}")
		session.rollback()
		return None

def get_current_year() -> int:
	"""現在の年を取得する"""
	return datetime.now().year

def get_year_from_user() -> int:
	"""ユーザーから年を入力してもらう"""
	while True:
		try:
			year = input("年を入力してください（空の場合は現在の年）: ").strip()
			if not year:
				return get_current_year()
			year = int(year)
			if 2000 <= year <= 2100:  # 妥当な年の範囲をチェック
				return year
			print("2000年から2100年の間で入力してください")
		except ValueError:
			print("正しい数値を入力してください")

def extract_instructors_from_schedule(schedule_data: List[Dict]) -> tuple[List[Tuple[int, List[str]]], int]:
	"""スケジュールデータから講義回数と担当者を抽出"""
	lecture_session_instructors = []
	null_instructor_count = 0  # null講師名のカウンター
	
	if not schedule_data:
		return lecture_session_instructors, null_instructor_count
	
	# リスト全体が正規かどうかを判定
	if not is_regular_session_list(schedule_data):
		# リスト内に1件でも不規則なレコードがある場合は全体をスキップ
		return lecture_session_instructors, null_instructor_count
	
	for session_data in schedule_data:
		if not isinstance(session_data, dict):
			continue
		
		# セッション情報を取得
		session = session_data.get("session", "")
		if not session:
			continue
		
		# セッションデータを処理
		is_regular, session_number, _, _ = process_session_data(session)
		
		# 不規則セッションの場合はスキップ（この時点では全て正規のはず）
		if not is_regular or session_number == 0:
			continue
		
		# 担当者情報を取得
		instructor = session_data.get("instructor", "")
		if not instructor:
			null_instructor_count += 1
			continue
		
		# 担当者名を分割（複数人の場合）
		instructor_names = []
		if instructor:
			# 区切り文字で分割（カンマ、セミコロン、改行など）
			split_pattern = r'[,;、；\n\r]+'
			instructor_names = [name.strip() for name in re.split(split_pattern, instructor) if name.strip()]
		
		if instructor_names:
			lecture_session_instructors.append((session_number, instructor_names))
		else:
			null_instructor_count += 1
	
	# 統計情報を表示
	if null_instructor_count > 0:
		print(f"講師名null件数: {null_instructor_count}件")
	
	return lecture_session_instructors, null_instructor_count

def get_json_files(year: int) -> List[str]:
	"""指定された年のJSONファイル一覧を取得"""
	json_dir = os.path.join("src", "syllabus", str(year), "json")
	json_files = []
	
	if os.path.exists(json_dir):
		for file in os.listdir(json_dir):
			if file.endswith('.json'):
				json_files.append(os.path.join(json_dir, file))
	
	return json_files

def check_lecture_session_irregular_exists(session, syllabus_id: int) -> bool:
	"""lecture_session_irregularテーブルにsyllabus_idが存在するかチェック"""
	query = text("""
		SELECT COUNT(*) FROM lecture_session_irregular 
		WHERE syllabus_id = :syllabus_id
	""")
	
	result = session.execute(query, {'syllabus_id': syllabus_id}).fetchone()
	return result[0] > 0 if result else False

def extract_lecture_session_instructor_from_single_json(json_data: Dict, session, year: int, json_file: str, stats: Dict = None, max_lecture_session_id: int = None) -> tuple[List[Dict], List[str]]:
	"""単一のJSONファイルから講義回数担当者情報を抽出"""
	lecture_session_instructors = []
	errors = []
	
	try:
		# JSONデータから科目コードを取得
		syllabus_code = json_data.get('科目コード')
		syllabus_year = year
		
		if not syllabus_code:
			errors.append(f"科目コードが見つかりません: {json_file}")
			return lecture_session_instructors, errors
		
		# シラバスマスターのIDを取得
		syllabus_master_id = get_syllabus_master_id_from_db(session, syllabus_code, syllabus_year)
		
		if not syllabus_master_id:
			errors.append(f"シラバスマスターIDが見つかりません: {syllabus_code} ({syllabus_year})")
			return lecture_session_instructors, errors
		
		# スケジュールデータを取得
		schedule_data = json_data.get('講義計画', {}).get('内容', {}).get('schedule', [])
		
		# スケジュールデータから講義回数と担当者を抽出
		session_instructors, null_instructor_count = extract_instructors_from_schedule(schedule_data)
		
		# 統計情報にnull件数を反映
		if stats is not None:
			stats['null_instructor_count'] += null_instructor_count
		
		# 各講義回数と担当者の組み合わせを処理
		for session_number, instructor_names in session_instructors:
			# lecture_session_idを取得
			lecture_session_id = get_lecture_session_id_from_db(session, syllabus_master_id, session_number)
			
			if not lecture_session_id:
				# lecture_session_irregularテーブルにsyllabus_idが存在するかチェック
				if check_lecture_session_irregular_exists(session, syllabus_master_id):
					# 不規則データの場合はエラーとして扱わない
					continue
				else:
					errors.append(f"lecture_session_idが見つかりません: {syllabus_code} 回数{session_number}")
					continue
			
			# lecture_session_idが最大値を超えているかチェック
			if max_lecture_session_id and lecture_session_id > max_lecture_session_id:
				error_msg = f"lecture_session_idが最大値を超えています: {lecture_session_id} > {max_lecture_session_id} ({syllabus_code} 回数{session_number})"
				errors.append(error_msg)
				tqdm.write(f"        ERROR: {error_msg}")
				continue
			
			# 各担当者についてレコードを作成
			for instructor_name in instructor_names:
				# instructor_idを取得
				instructor_id = get_instructor_id_from_db(session, instructor_name)
				
				if not instructor_id:
					errors.append(f"instructor_idが見つかりません: {instructor_name} ({syllabus_code} 回数{session_number})")
					continue
				
				# レコードを作成
				lecture_session_instructors.append({
					'lecture_session_id': lecture_session_id,
					'instructor_id': instructor_id,
					'role': '担当'  # 役割を「担当」に設定
				})
		
	except Exception as e:
		error_msg = f"エラーが発生しました: {str(e)}"
		if 'syllabus_code' in locals():
			error_msg = f"科目コード {syllabus_code}: {error_msg}"
		tqdm.write(f"        EXTRACT ERROR: {error_msg}")
		errors.append(error_msg)
	
	return lecture_session_instructors, errors

def process_lecture_session_instructor_json(json_file: str, session, year: int) -> tuple[List[Dict], List[str]]:
	"""JSONファイルを処理して講義回数担当者情報を抽出"""
	all_lecture_session_instructors = []
	all_errors = []
	
	try:
		with open(json_file, 'r', encoding='utf-8') as f:
			json_data = json.load(f)
		
		lecture_session_instructors, errors = extract_lecture_session_instructor_from_single_json(json_data, session, year, json_file)
		
		all_lecture_session_instructors.extend(lecture_session_instructors)
		all_errors.extend(errors)
		
	except Exception as e:
		all_errors.append(f"ファイル読み込みエラー {json_file}: {str(e)}")
	
	return all_lecture_session_instructors, all_errors

def create_lecture_session_instructor_json(lecture_session_instructors: List[Dict]) -> str:
	"""講義回数担当者情報をJSONファイルとして保存"""
	output_dir = os.path.join("updates", "lecture_session_instructor", "add")
	os.makedirs(output_dir, exist_ok=True)
	
	timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
	filename = f"lecture_session_instructor_{timestamp}.json"
	filepath = os.path.join(output_dir, filename)
	
	tqdm.write(f"  JSONファイルに書き込み中: {filename}")
	tqdm.write(f"  データ件数: {len(lecture_session_instructors):,}件")
	
	# データサイズを確認
	data_size = len(json.dumps(lecture_session_instructors, ensure_ascii=False))
	tqdm.write(f"  データサイズ: {data_size:,} バイト ({data_size/1024/1024:.2f} MB)")
	
	try:
		# 大量データの場合は分割処理
		if len(lecture_session_instructors) > 100000:  # 10万件以上
			tqdm.write(f"  大量データのため分割処理を実行中...")
			chunk_size = 50000  # 5万件ずつ分割
			chunks = [lecture_session_instructors[i:i + chunk_size] for i in range(0, len(lecture_session_instructors), chunk_size)]
			
			with open(filepath, 'w', encoding='utf-8') as f:
				f.write('[\n')
				for chunk_idx, chunk in enumerate(chunks):
					tqdm.write(f"    チャンク {chunk_idx + 1}/{len(chunks)} を処理中...")
					for i, instructor in enumerate(chunk):
						if chunk_idx > 0 or i > 0:
							f.write(',\n')
						json.dump(instructor, f, ensure_ascii=False, indent=2)
				f.write('\n]')
		else:
			# 通常のストリーミング書き込み
			tqdm.write(f"  ストリーミング書き込みを実行中...")
			with open(filepath, 'w', encoding='utf-8') as f:
				f.write('[\n')
				for i, instructor in tqdm(enumerate(lecture_session_instructors), total=len(lecture_session_instructors), desc="  ストリーミング書き込み"):
					if i > 0:
						f.write(',\n')
					json.dump(instructor, f, ensure_ascii=False, indent=2)
				f.write('\n]')
		
		tqdm.write(f"  書き込み完了: {filepath}")
	except Exception as e:
		tqdm.write(f"  書き込みエラー: {str(e)}")
		raise
	
	return filepath

def create_error_csv(all_errors: List[str], final_errors: List[str], year: int) -> str:
	"""エラー情報をCSVファイルとして保存"""
	output_dir = os.path.join("warning", str(year))
	os.makedirs(output_dir, exist_ok=True)
	
	timestamp = datetime.now().strftime("%Y%m%d_%H%M")
	filename = f"lecture_session_instructor_{timestamp}.csv"
	filepath = os.path.join(output_dir, filename)
	
	tqdm.write(f"  CSVファイルに書き込み中: {filename}")
	with open(filepath, 'w', encoding='utf-8', newline='') as f:
		writer = csv.writer(f)
		writer.writerow(['エラータイプ', 'エラー内容'])
		
		for error in all_errors:
			writer.writerow(['処理エラー', error])
		
		for error in final_errors:
			writer.writerow(['最終エラー', error])
	
	return filepath

def main():
	"""メイン処理"""
	print("講義回数担当者情報抽出処理を開始します...")
	
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
		'null_instructor_count': 0,  # null講師名のカウンター
		'specific_errors': {}
	}
	
	# lecture_session_idの最大値を取得
	max_lecture_session_id = get_lecture_session_max_id_from_db(session)
	if max_lecture_session_id:
		tqdm.write(f"lecture_session_idの最大値: {max_lecture_session_id}")
		stats['max_lecture_session_id'] = max_lecture_session_id
	else:
		tqdm.write("lecture_session_idの最大値の取得に失敗しました")
		return
	
	# 出力ファイルの準備
	timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
	
	# 講義回数担当者用ファイル
	lecture_session_instructor_dir = os.path.join("updates", "lecture_session_instructor", "add")
	os.makedirs(lecture_session_instructor_dir, exist_ok=True)
	lecture_session_instructor_file = os.path.join(lecture_session_instructor_dir, f"lecture_session_instructor_{timestamp}.json")
	
	# エラー情報用ファイル
	error_dir = os.path.join("warning", str(year))
	os.makedirs(error_dir, exist_ok=True)
	error_file = os.path.join(error_dir, f"lecture_session_instructor_{timestamp}.csv")
	
	# ファイルを開いて書き込み開始
	lecture_session_instructor_count = 0
	all_errors = []
	
	# 講義回数担当者ファイルを開く
	instructor_f = open(lecture_session_instructor_file, 'w', encoding='utf-8')
	instructor_f.write('[\n')
	instructor_first = True
	
	try:
		# 処理開始時のメッセージ
		tqdm.write(f"講義回数担当者情報抽出処理 - 対象年度: {year}")
		
		for i, json_file in enumerate(tqdm(json_files, desc="JSONファイル処理中", unit="file")):
			try:
				with open(json_file, 'r', encoding='utf-8') as f:
					json_data = json.load(f)
				
				lecture_session_instructors, errors = extract_lecture_session_instructor_from_single_json(json_data, session, year, json_file, stats, max_lecture_session_id)
				
				# 統計情報の更新
				stats['processed_files'] += 1
				stats['total_items'] += len(lecture_session_instructors)
				stats['valid_items'] += len(lecture_session_instructors)
				stats['error_items'] += len(errors)
				
				# 講義回数担当者を書き込み
				for instructor_data in lecture_session_instructors:
					if not instructor_first:
						instructor_f.write(',\n')
					json.dump(instructor_data, instructor_f, ensure_ascii=False, indent=2)
					instructor_first = False
					lecture_session_instructor_count += 1
				
				all_errors.extend(errors)
				
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
	tqdm.write(f"講師名null件数: {stats['null_instructor_count']}")
	if 'max_lecture_session_id' in stats:
		tqdm.write(f"lecture_session_id最大値: {stats['max_lecture_session_id']}")
	tqdm.write("="*60)
	
	# 結果サマリーの表示
	tqdm.write(f"\n{'='*60}")
	tqdm.write("📊 抽出結果サマリー")
	tqdm.write(f"{'='*60}")
	tqdm.write(f"✅ 講義回数担当者: {lecture_session_instructor_count:,}件")
	tqdm.write(f"⚠️  エラーデータ: {len(all_errors)}件")
	tqdm.write(f"📈 合計: {lecture_session_instructor_count:,}件")
	
	# 結果を表示
	final_errors = []
	
	if lecture_session_instructor_count > 0:
		tqdm.write(f"講義回数担当者情報を保存しました: {lecture_session_instructor_file}")
	else:
		final_errors.append("講義回数担当者情報が見つかりませんでした")
	
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
	
	tqdm.write("講義回数担当者情報抽出処理が完了しました")

if __name__ == "__main__":
	main() 