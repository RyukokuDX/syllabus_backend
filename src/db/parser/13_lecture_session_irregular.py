# -*- coding: utf-8 -*-
# File Version: v1.0.4
# Project Version: v1.3.35
# Last Updated: 2025/6/23

import os
import json
import sys
from typing import List, Dict
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
	from utils import normalize_subject_name, process_session_data, is_regular_session_list
except ImportError:
	# utils.pyが見つからない場合のフォールバック関数
	def normalize_subject_name(text: str) -> str:
		"""文字列を正規化する関数"""
		return unicodedata.normalize('NFKC', text)
	
	def process_session_data(session_text: str) -> tuple[bool, int, str]:
		"""フォールバック関数"""
		return False, 0, ""
	
	def is_regular_session_list(schedule_data: list) -> bool:
		"""フォールバック関数"""
		return False

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

def parse_lecture_sessions_irregular_from_schedule(schedule_data: List[Dict]) -> List[Dict]:
	"""スケジュールデータから不規則な講義セッションのみを解析して正規化する"""
	import re  # 関数内でインポート
	
	lecture_sessions_irregular = []  # 不規則な講義セッションのみ
	
	if not schedule_data:
		return lecture_sessions_irregular
	
	# リスト全体が正規かどうかを判定
	if is_regular_session_list(schedule_data):
		return lecture_sessions_irregular
	
	# 不規則な理由を判定
	error_reasons = []
	
	# 非回数データのチェック
	has_non_numeric = False
	# 重複回数データのチェック
	normalized_sessions = []
	
	for session_data in schedule_data:
		if not isinstance(session_data, dict):
			continue
		
		session = session_data.get("session", "")
		if not session:
			continue
		
		# セッションデータを処理
		is_regular, session_number, session_pattern = process_session_data(session)
		
		if is_regular and session_number > 0:
			normalized_sessions.append(session_number)
		else:
			has_non_numeric = True
	
	# 重複チェック
	if len(normalized_sessions) != len(set(normalized_sessions)):
		error_reasons.append("重複回数データ包含")
	
	if has_non_numeric:
		error_reasons.append("非回数データ包含")
	
	# エラーメッセージを生成
	error_message = "、".join(error_reasons) if error_reasons else "不規則データ"
	
	# 不規則なセッションを処理
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
		
		# 内容を取得
		contents = session_data.get("content", "")
		# 担当者情報を取得（シラバスJSONの値をそのまま）
		instructor = session_data.get("instructor", "")
		
		lecture_sessions_irregular.append({
			'syllabus_id': None,  # 後で設定
			'session_pattern': session_pattern,
			'contents': contents if contents else None,
			'other_info': None,
			'instructor': instructor if instructor else None,
			'error_message': error_message
		})
	
	return lecture_sessions_irregular

def get_json_files(year: int) -> List[str]:
	"""指定された年のJSONファイル一覧を取得"""
	json_dir = os.path.join("src", "syllabus", str(year), "json")
	json_files = []
	
	if os.path.exists(json_dir):
		for file in os.listdir(json_dir):
			if file.endswith('.json'):
				json_files.append(os.path.join(json_dir, file))
	
	return json_files

def extract_lecture_session_irregular_from_single_json(json_data: Dict, session, year: int, json_file: str) -> tuple[List[Dict], List[str]]:
	"""単一のJSONファイルから不規則な講義セッション情報を抽出"""
	lecture_sessions_irregular = []
	errors = []
	
	try:
		# JSONデータから科目コードを取得
		syllabus_code = json_data.get('科目コード')
		syllabus_year = year
		
		if not syllabus_code:
			errors.append(f"科目コードが見つかりません: {json_file}")
			return lecture_sessions_irregular, errors
		
		# シラバスマスターのIDを取得
		syllabus_master_id = get_syllabus_master_id_from_db(session, syllabus_code, syllabus_year)
		
		if not syllabus_master_id:
			errors.append(f"シラバスマスターIDが見つかりません: {syllabus_code} ({syllabus_year})")
			return lecture_sessions_irregular, errors
		
		# スケジュールデータを取得
		schedule_data = json_data.get('講義計画', {}).get('内容', {}).get('schedule', [])
		
		# スケジュールデータから不規則な講義セッションを解析
		parsed_sessions_irregular = parse_lecture_sessions_irregular_from_schedule(schedule_data)
		
		# シラバスマスターIDを追加
		for session_data in parsed_sessions_irregular:
			session_data['syllabus_id'] = syllabus_master_id
			lecture_sessions_irregular.append(session_data)
		
	except Exception as e:
		error_msg = f"エラーが発生しました: {str(e)}"
		if 'syllabus_code' in locals():
			error_msg = f"科目コード {syllabus_code}: {error_msg}"
		print(f"        EXTRACT ERROR: {error_msg}")
		errors.append(error_msg)
	
	return lecture_sessions_irregular, errors

def process_lecture_session_irregular_json(json_file: str, session, year: int) -> tuple[List[Dict], List[str]]:
	"""JSONファイルを処理して不規則な講義セッション情報を抽出"""
	all_lecture_sessions_irregular = []
	all_errors = []
	
	try:
		with open(json_file, 'r', encoding='utf-8') as f:
			json_data = json.load(f)
		
		lecture_sessions_irregular, errors = extract_lecture_session_irregular_from_single_json(json_data, session, year, json_file)
		
		all_lecture_sessions_irregular.extend(lecture_sessions_irregular)
		all_errors.extend(errors)
		
	except Exception as e:
		all_errors.append(f"ファイル読み込みエラー {json_file}: {str(e)}")
	
	return all_lecture_sessions_irregular, all_errors

def create_lecture_session_irregular_json(lecture_sessions_irregular: List[Dict]) -> str:
	"""不規則な講義セッション情報をJSONファイルとして保存"""
	output_dir = os.path.join("updates", "lecture_session_irregular", "add")
	os.makedirs(output_dir, exist_ok=True)
	
	timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
	filename = f"lecture_session_irregular_{timestamp}.json"
	filepath = os.path.join(output_dir, filename)
	
	print(f"  JSONファイルに書き込み中: {filename}")
	print(f"  データ件数: {len(lecture_sessions_irregular):,}件")
	
	# データサイズを確認
	data_size = len(json.dumps(lecture_sessions_irregular, ensure_ascii=False))
	print(f"  データサイズ: {data_size:,} バイト ({data_size/1024/1024:.2f} MB)")
	
	try:
		# 大量データの場合は分割処理
		if len(lecture_sessions_irregular) > 100000:  # 10万件以上
			print(f"  大量データのため分割処理を実行中...")
			chunk_size = 50000  # 5万件ずつ分割
			chunks = [lecture_sessions_irregular[i:i + chunk_size] for i in range(0, len(lecture_sessions_irregular), chunk_size)]
			
			with open(filepath, 'w', encoding='utf-8') as f:
				f.write('[\n')
				for chunk_idx, chunk in enumerate(chunks):
					print(f"    チャンク {chunk_idx + 1}/{len(chunks)} を処理中...")
					for i, session in enumerate(chunk):
						if chunk_idx > 0 or i > 0:
							f.write(',\n')
						json.dump(session, f, ensure_ascii=False, indent=2)
				f.write('\n]')
		else:
			# 通常のストリーミング書き込み
			print(f"  ストリーミング書き込みを実行中...")
			with open(filepath, 'w', encoding='utf-8') as f:
				f.write('[\n')
				for i, session in tqdm(enumerate(lecture_sessions_irregular), total=len(lecture_sessions_irregular), desc="  ストリーミング書き込み"):
					if i > 0:
						f.write(',\n')
					json.dump(session, f, ensure_ascii=False, indent=2)
				f.write('\n]')
		
		print(f"  書き込み完了: {filepath}")
	except Exception as e:
		print(f"  書き込みエラー: {str(e)}")
		raise
	
	return filepath

def create_error_csv(all_errors: List[str], final_session_errors: List[str], year: int) -> str:
	"""エラー情報をCSVファイルとして保存"""
	output_dir = os.path.join("warning", str(year))
	os.makedirs(output_dir, exist_ok=True)
	
	timestamp = datetime.now().strftime("%Y%m%d_%H%M")
	filename = f"lecture_session_irregular_{timestamp}.csv"
	filepath = os.path.join(output_dir, filename)
	
	print(f"  CSVファイルに書き込み中: {filename}")
	with open(filepath, 'w', encoding='utf-8', newline='') as f:
		writer = csv.writer(f)
		writer.writerow(['エラータイプ', 'エラー内容'])
		
		for error in all_errors:
			writer.writerow(['処理エラー', error])
		
		for error in final_session_errors:
			writer.writerow(['最終エラー', error])
	
	return filepath

def main():
	"""メイン処理"""
	print("不規則講義セッション情報抽出処理を開始します...")
	
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
	
	# 不規則な講義セッション用ファイル
	lecture_session_irregular_dir = os.path.join("updates", "lecture_session_irregular", "add")
	os.makedirs(lecture_session_irregular_dir, exist_ok=True)
	lecture_session_irregular_file = os.path.join(lecture_session_irregular_dir, f"lecture_session_irregular_{timestamp}.json")
	
	# エラー情報用ファイル
	error_dir = os.path.join("warning", str(year))
	os.makedirs(error_dir, exist_ok=True)
	error_file = os.path.join(error_dir, f"lecture_session_irregular_{timestamp}.csv")
	
	# ファイルを開いて書き込み開始
	lecture_session_irregular_count = 0
	all_errors = []
	
	# 不規則な講義セッションファイルを開く
	irregular_f = open(lecture_session_irregular_file, 'w', encoding='utf-8')
	irregular_f.write('[\n')
	irregular_first = True
	
	try:
		# 処理開始時のメッセージ
		tqdm.write(f"\n{'='*60}")
		tqdm.write(f"不規則講義セッション情報抽出処理 - 対象年度: {year}")
		tqdm.write(f"{'='*60}")
		
		for i, json_file in enumerate(tqdm(json_files, desc="JSONファイル処理中", unit="file")):
			try:
				with open(json_file, 'r', encoding='utf-8') as f:
					json_data = json.load(f)
				
				lecture_sessions_irregular, errors = extract_lecture_session_irregular_from_single_json(json_data, session, year, json_file)
				
				# 統計情報の更新
				stats['processed_files'] += 1
				stats['total_items'] += len(lecture_sessions_irregular)
				stats['valid_items'] += len(lecture_sessions_irregular)
				stats['error_items'] += len(errors)
				
				# 不規則な講義セッションを書き込み
				for session_data in lecture_sessions_irregular:
					if not irregular_first:
						irregular_f.write(',\n')
					json.dump(session_data, irregular_f, ensure_ascii=False, indent=2)
					irregular_first = False
					lecture_session_irregular_count += 1
				
				all_errors.extend(errors)
				
			except Exception as e:
				error_msg = f"ファイル読み込みエラー {json_file}: {str(e)}"
				tqdm.write(f"エラー: {error_msg}")
				all_errors.append(error_msg)
				stats['error_items'] += 1
		
		# ファイルを閉じる
		irregular_f.write('\n]')
		irregular_f.close()
		
	except Exception as e:
		# エラーが発生した場合もファイルを閉じる
		try:
			irregular_f.close()
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
	tqdm.write(f"✅ 不規則セッション: {lecture_session_irregular_count:,}件")
	tqdm.write(f"⚠️  エラーデータ: {len(all_errors)}件")
	tqdm.write(f"📈 合計: {lecture_session_irregular_count:,}件")
	
	# 結果を表示
	final_session_errors = []
	
	if lecture_session_irregular_count > 0:
		tqdm.write(f"不規則な講義セッション情報を保存しました: {lecture_session_irregular_file}")
	else:
		final_session_errors.append("不規則な講義セッション情報が見つかりませんでした")
	
	# エラー情報を保存
	if all_errors or final_session_errors:
		with open(error_file, 'w', encoding='utf-8', newline='') as f:
			writer = csv.writer(f)
			writer.writerow(['エラータイプ', 'エラー内容'])
			
			for error in all_errors:
				writer.writerow(['処理エラー', error])
			
			for error in final_session_errors:
				writer.writerow(['最終エラー', error])
		
		tqdm.write(f"エラー情報を保存しました: {error_file}")
	
	# セッションを閉じる
	session.close()
	
	tqdm.write("不規則講義セッション情報抽出処理が完了しました")

if __name__ == "__main__":
	main() 