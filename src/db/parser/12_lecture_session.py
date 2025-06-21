# -*- coding: utf-8 -*-
# File Version: v1.3.1
# Project Version: v1.3.21
# Last Updated: 2025/6/21

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

# 現在のディレクトリをPythonパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# utils.pyから正規化関数をインポート
try:
	from utils import normalize_subject_name
except ImportError:
	# utils.pyが見つからない場合のフォールバック
	def normalize_subject_name(text: str) -> str:
		"""テキストを正規化する（フォールバック）"""
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
	
	# セッション作成時に一度だけ文字エンコーディングを設定
	session.execute(text("SET client_encoding TO 'utf-8'"))
	session.commit()
	
	return session

def get_syllabus_master_id_from_db(session, syllabus_code: str, syllabus_year: int) -> int:
	"""シラバスマスターIDを取得する"""
	try:
		# シラバスマスターIDを取得
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
		session.rollback()
		return None

def get_current_year() -> int:
	"""現在の年度を取得する"""
	return datetime.now().year

def get_year_from_user() -> int:
	"""ユーザーから年度を入力してもらう"""
	while True:
		try:
			year = input("年度を入力してください（空の場合は現在の年度）: ").strip()
			if not year:
				return get_current_year()
			year = int(year)
			if 2000 <= year <= 2100:  # 妥当な年度の範囲をチェック
				return year
			print("2000年から2100年の間で入力してください。")
		except ValueError:
			print("有効な数値を入力してください。")

def parse_lecture_sessions_from_schedule(schedule_data: List[Dict]) -> tuple[List[Dict], List[Dict]]:
	"""講義計画のschedule配列から講義回数データを解析して構造化する
	通常の講義回数と不定形講義回数に分けて返す"""
	import re  # 関数の先頭でインポート
	
	lecture_sessions = []  # 通常の講義回数（1-15回）
	lecture_sessions_irregular = []  # 不定形講義回数
	
	if not schedule_data:
		return lecture_sessions, lecture_sessions_irregular
	
	for session_data in schedule_data:
		if not isinstance(session_data, dict):
			continue
		
		# 回数を取得（例: "1-1" → 1, "2-2" → 2, "1回目" → 1）
		session = session_data.get("session", "")
		if not session:
			continue
		
		# utils.pyの正規化機能を使用して全角文字を半角に変換
		session_normalized = normalize_subject_name(session)
		
		# 全角文字を除去（数字以外の全角文字を削除）
		session_cleaned = re.sub(r'[^\d\-]', '', session_normalized)
		
		# デバッグ用: 正規化前後の値を確認
		# print(f"DEBUG: session='{session}' -> normalized='{session_normalized}' -> cleaned='{session_cleaned}'")
		
		# 内容を取得
		contents = session_data.get("content", "")
		
		# 担当者情報を取得（lecture_session_instructorテーブル用）
		instructor = session_data.get("instructor", "")
		
		# 回数パターンの分類
		session_pattern = session  # 元のパターンを保持
		
		# まず「回目」形式をチェック
		if '回目' in session_normalized:
			# 数字を抽出
			numbers = re.findall(r'\d+', session_normalized)
			if numbers:
				try:
					session_number = int(numbers[0])
					# 1-15回の範囲内かチェック
					if 1 <= session_number <= 15:
						# 通常の講義回数として処理
						lecture_sessions.append({
							'session_number': session_number,
							'contents': contents if contents else None,
							'other_info': None,
							'instructor': instructor if instructor else None
						})
					else:
						# 範囲外の場合は不定形として処理
						lecture_sessions_irregular.append({
							'session_pattern': session_pattern,
							'contents': contents if contents else None,
							'other_info': None,
							'instructor': instructor if instructor else None
						})
				except ValueError:
					# 数値変換できない場合は不定形として処理
					lecture_sessions_irregular.append({
						'session_pattern': session_pattern,
						'contents': contents if contents else None,
						'other_info': None,
						'instructor': instructor if instructor else None
					})
			else:
				# 数字が見つからない場合は不定形として処理
				lecture_sessions_irregular.append({
					'session_pattern': session_pattern,
					'contents': contents if contents else None,
					'other_info': None,
					'instructor': instructor if instructor else None
				})
		else:
			# ハイフン区切りの形式をチェック
			session_parts = session_cleaned.split('-')
			if len(session_parts) >= 2:
				try:
					start_session = int(session_parts[0])
					end_session = int(session_parts[1])
					
					# 範囲が1-15回内で、連続している場合は通常の講義回数として処理
					if (1 <= start_session <= 15 and 1 <= end_session <= 15 and 
						end_session >= start_session and end_session - start_session <= 14):
						# 範囲内のすべての回数を生成
						for session_number in range(start_session, end_session + 1):
							lecture_sessions.append({
								'session_number': session_number,
								'contents': contents if contents else None,
								'other_info': None,
								'instructor': instructor if instructor else None
							})
					else:
						# 範囲外または不連続の場合は不定形として処理
						lecture_sessions_irregular.append({
							'session_pattern': session_pattern,
							'contents': contents if contents else None,
							'other_info': None,
							'instructor': instructor if instructor else None
						})
				except ValueError:
					# 数値変換できない場合は不定形として処理
					lecture_sessions_irregular.append({
						'session_pattern': session_pattern,
						'contents': contents if contents else None,
						'other_info': None,
						'instructor': instructor if instructor else None
					})
			elif len(session_parts) == 1:
				try:
					session_number = int(session_parts[0])
					# 1-15回の範囲内かチェック
					if 1 <= session_number <= 15:
						# 通常の講義回数として処理
						lecture_sessions.append({
							'session_number': session_number,
							'contents': contents if contents else None,
							'other_info': None,
							'instructor': instructor if instructor else None
						})
					else:
						# 範囲外の場合は不定形として処理
						lecture_sessions_irregular.append({
							'session_pattern': session_pattern,
							'contents': contents if contents else None,
							'other_info': None,
							'instructor': instructor if instructor else None
						})
				except ValueError:
					# 数値変換できない場合は不定形として処理
					lecture_sessions_irregular.append({
						'session_pattern': session_pattern,
						'contents': contents if contents else None,
						'other_info': None,
						'instructor': instructor if instructor else None
					})
			else:
				# 有効な形式でない場合は不定形として処理
				lecture_sessions_irregular.append({
					'session_pattern': session_pattern,
					'contents': contents if contents else None,
					'other_info': None,
					'instructor': instructor if instructor else None
				})
	
	# print(f"DEBUG: Total lecture_sessions created: {len(lecture_sessions)}")
	# print(f"DEBUG: Total lecture_sessions_irregular created: {len(lecture_sessions_irregular)}")
	return lecture_sessions, lecture_sessions_irregular

def get_json_files(year: int) -> List[str]:
	"""指定された年度のすべてのJSONファイルのパスを取得する"""
	json_dir = os.path.join("src", "syllabus", str(year), "json")
	if not os.path.exists(json_dir):
		raise FileNotFoundError(f"ディレクトリが見つかりません: {json_dir}")
	
	json_files = [f for f in os.listdir(json_dir) if f.endswith('.json')]
	if not json_files:
		raise FileNotFoundError(f"JSONファイルが見つかりません: {json_dir}")
	
	return [os.path.join(json_dir, f) for f in json_files]

def extract_lecture_session_from_single_json(json_data: Dict, session, year: int) -> tuple[List[Dict], List[Dict], List[str]]:
	"""単一のJSONファイルから講義回数情報を抽出する
	通常の講義回数と不定形講義回数を分けて返す"""
	lecture_sessions = []  # 通常の講義回数
	lecture_sessions_irregular = []  # 不定形講義回数
	errors = []
	
	# 科目コードを取得
	syllabus_code = json_data.get("科目コード", "")
	
	if not syllabus_code:
		errors.append("科目コードが見つかりません")
		return lecture_sessions, lecture_sessions_irregular, errors
	
	# syllabus_masterからsyllabus_idを取得
	syllabus_id = get_syllabus_master_id_from_db(session, syllabus_code, year)
	
	if not syllabus_id:
		errors.append(f"syllabus_masterに対応するレコードがありません（科目コード: {syllabus_code}）")
		return lecture_sessions, lecture_sessions_irregular, errors
	
	# 講義計画を取得
	lecture_plan = json_data.get("講義計画", {})
	schedule_data = lecture_plan.get("内容", {})
	
	if isinstance(schedule_data, dict):
		schedule = schedule_data.get("schedule", [])
	else:
		schedule = []
	
	if not schedule:
		errors.append("講義計画のscheduleが見つかりません")
		return lecture_sessions, lecture_sessions_irregular, errors
	
	# 講義回数を解析
	parsed_sessions, parsed_sessions_irregular = parse_lecture_sessions_from_schedule(schedule)
	
	if not parsed_sessions and not parsed_sessions_irregular:
		errors.append("講義回数の解析結果が空です")
		return lecture_sessions, lecture_sessions_irregular, errors
	
	# 通常の講義回数を処理
	for session_data in parsed_sessions:
		lecture_sessions.append({
			'syllabus_id': syllabus_id,
			'session_number': session_data['session_number'],
			'contents': session_data['contents'],
			'other_info': session_data['other_info'],
			'instructor': session_data['instructor']
		})
	
	# 不定形講義回数を処理
	for session_data in parsed_sessions_irregular:
		lecture_sessions_irregular.append({
			'syllabus_id': syllabus_id,
			'session_pattern': session_data['session_pattern'],
			'contents': session_data['contents'],
			'other_info': session_data['other_info'],
			'instructor': session_data['instructor']
		})
	
	# 集中講義かどうかをチェック
	basic_info = json_data.get("基本情報", {})
	time_info = basic_info.get("開講期・曜講時", {})
	time_text = time_info.get("内容", "") if isinstance(time_info, dict) else str(time_info)
	
	# 集中講義でない場合、最終回をチェック（通常の講義回数のみ）
	if time_text and '集中' not in time_text:
		if lecture_sessions:
			max_session = max(session['session_number'] for session in lecture_sessions)
			if max_session not in [15, 30]:
				errors.append(f"最終回が{max_session}回（期待値: 15回または30回）")
	
	return lecture_sessions, lecture_sessions_irregular, errors

def process_lecture_session_json(json_file: str, session, year: int) -> tuple[List[Dict], List[Dict], List[str]]:
	"""個別の講義回数JSONファイルを処理する
	通常の講義回数と不定形講義回数を分けて返す"""
	errors = []
	try:
		with open(json_file, 'r', encoding='utf-8') as f:
			json_data = json.load(f)
		
		# 講義回数情報を抽出
		lecture_sessions, lecture_sessions_irregular, extraction_errors = extract_lecture_session_from_single_json(json_data, session, year)
		
		# 抽出エラーを追加
		errors.extend(extraction_errors)
		
		# エラーがない場合は成功
		if not errors and (lecture_sessions or lecture_sessions_irregular):
			return lecture_sessions, lecture_sessions_irregular, []
		
		# エラーがある場合は詳細を記録
		if errors:
			return [], [], errors
		
		# 講義回数情報が空の場合
		return [], [], ["講義回数情報が抽出できませんでした"]
		
	except json.JSONDecodeError as e:
		errors.append(f"JSONファイルの解析エラー: {str(e)}")
		return [], [], errors
	except Exception as e:
		errors.append(f"処理中にエラーが発生: {str(e)}")
		return [], [], errors

def create_lecture_session_json(lecture_sessions: List[Dict]) -> str:
	"""講義回数情報のJSONファイルを作成する"""
	# lecture_session用のディレクトリ
	session_output_dir = os.path.join("updates", "lecture_session", "add")
	os.makedirs(session_output_dir, exist_ok=True)
	
	# 現在の日時を取得してファイル名を生成
	current_time = datetime.now()
	
	# lecture_session用のJSONファイル
	filename = f"lecture_session_{current_time.strftime('%Y%m%d_%H%M')}.json"
	output_file = os.path.join(session_output_dir, filename)
	
	data = {
		"lecture_sessions": [{
			"syllabus_id": session["syllabus_id"],
			"session_number": session["session_number"],
			"contents": session["contents"],
			"other_info": session["other_info"],
			"created_at": current_time.isoformat()
		} for session in sorted(lecture_sessions, key=lambda x: (x["syllabus_id"], x["session_number"]))]
	}
	
	with open(output_file, 'w', encoding='utf-8') as f:
		json.dump(data, f, ensure_ascii=False, indent=2)
	
	return output_file

def create_lecture_session_irregular_json(lecture_sessions_irregular: List[Dict]) -> str:
	"""不定形講義回数情報のJSONファイルを作成する"""
	# lecture_session_irregular用のディレクトリ
	session_output_dir = os.path.join("updates", "lecture_session_irregular", "add")
	os.makedirs(session_output_dir, exist_ok=True)
	
	# 現在の日時を取得してファイル名を生成
	current_time = datetime.now()
	
	# lecture_session_irregular用のJSONファイル
	filename = f"lecture_session_irregular_{current_time.strftime('%Y%m%d_%H%M')}.json"
	output_file = os.path.join(session_output_dir, filename)
	
	data = {
		"lecture_session_irregulars": [{
			"syllabus_id": session["syllabus_id"],
			"session_pattern": session["session_pattern"],
			"contents": session["contents"],
			"other_info": session["other_info"],
			"created_at": current_time.isoformat()
		} for session in sorted(lecture_sessions_irregular, key=lambda x: (x["syllabus_id"], x["session_pattern"]))]
	}
	
	with open(output_file, 'w', encoding='utf-8') as f:
		json.dump(data, f, ensure_ascii=False, indent=2)
	
	return output_file

def create_error_csv(all_errors: List[str], final_session_errors: List[str], year: int) -> str:
	"""エラー内容をCSVファイルとして出力する"""
	warning_dir = os.path.join("warning", str(year))
	os.makedirs(warning_dir, exist_ok=True)
	
	# 現在の日時を取得してファイル名を生成
	current_time = datetime.now()
	filename = f"lecture_session_{current_time.strftime('%Y%m%d_%H%M')}.csv"
	output_file = os.path.join(warning_dir, filename)
	
	# エラー情報を整理
	error_data = []
	
	# 通常エラーを処理
	for error in all_errors:
		# エラーメッセージからJSONファイル名を抽出
		if ": " in error:
			json_name, error_message = error.split(": ", 1)
		else:
			json_name = "unknown"
			error_message = error
		
		error_data.append({
			'json_name': json_name,
			'error_message': error_message,
			'date': current_time.strftime('%Y-%m-%d %H:%M:%S')
		})
	
	# 最終回エラーを処理
	for error in final_session_errors:
		# エラーメッセージからJSONファイル名を抽出
		if ": " in error:
			json_name, error_message = error.split(": ", 1)
		else:
			json_name = "unknown"
			error_message = error
		
		error_data.append({
			'json_name': json_name,
			'error_message': error_message,
			'date': current_time.strftime('%Y-%m-%d %H:%M:%S')
		})
	
	# CSVファイルに書き込み
	with open(output_file, 'w', newline='', encoding='utf-8') as f:
		writer = csv.DictWriter(f, fieldnames=['json_name', 'error_message', 'date'])
		writer.writeheader()
		writer.writerows(error_data)
	
	return output_file

def main():
	"""メイン処理"""
	session = None
	try:
		# 年度の取得
		year = get_year_from_user()
		print(f"処理対象年度: {year}")
		
		# データベース接続
		session = get_db_connection()
		
		# すべてのJSONファイルを取得
		json_files = get_json_files(year)
		print(f"処理対象ファイル数: {len(json_files)}")
		
		# 講義回数情報を処理
		all_lecture_sessions = []  # 通常の講義回数
		all_lecture_sessions_irregular = []  # 不定形講義回数
		processed_count = 0
		error_count = 0
		skipped_count = 0
		
		# エラー情報を収集
		all_errors = []
		final_session_errors = []  # 最終回エラーを別途収集
		
		# 統計情報
		stats = {
			"total_files": len(json_files),
			"successful_files": 0,
			"error_files": 0,
			"total_lecture_sessions": 0,
			"total_lecture_sessions_irregular": 0,
			"final_session_error_files": 0
		}
		
		print(f"\n処理開始: {len(json_files)}個のJSONファイル")
		
		# tqdmを使用してプログレスバーを表示
		for json_file in tqdm(json_files, desc="JSONファイルを処理中"):
			try:
				lecture_sessions, lecture_sessions_irregular, errors = process_lecture_session_json(json_file, session, year)
				
				# 最終回エラーを分離
				final_session_error = None
				other_errors = []
				for error in errors:
					if "最終回が" in error:
						final_session_error = error
					else:
						other_errors.append(error)
				
				if other_errors:
					all_errors.extend([f"{os.path.basename(json_file)}: {error}" for error in other_errors])
					error_count += 1
					stats["error_files"] += 1
				else:
					if lecture_sessions or lecture_sessions_irregular:
						all_lecture_sessions.extend(lecture_sessions)
						all_lecture_sessions_irregular.extend(lecture_sessions_irregular)
						processed_count += 1
						stats["successful_files"] += 1
						stats["total_lecture_sessions"] += len(lecture_sessions)
						stats["total_lecture_sessions_irregular"] += len(lecture_sessions_irregular)
					else:
						skipped_count += 1
				
				# 最終回エラーを記録
				if final_session_error:
					final_session_errors.append(f"{os.path.basename(json_file)}: {final_session_error}")
					stats["final_session_error_files"] += 1
						
			except Exception as e:
				error_msg = f"{os.path.basename(json_file)}: 予期しないエラー: {str(e)}"
				all_errors.append(error_msg)
				error_count += 1
				stats["error_files"] += 1
		
		# 結果を表示
		print(f"\n処理完了:")
		print(f"  成功: {processed_count}ファイル")
		print(f"  エラー: {error_count}ファイル")
		print(f"  スキップ: {skipped_count}ファイル")
		print(f"  抽出された通常講義回数: {len(all_lecture_sessions)}件")
		print(f"  抽出された不定形講義回数: {len(all_lecture_sessions_irregular)}件")
		print(f"  最終回エラー: {stats['final_session_error_files']}ファイル")
		
		# エラーがある場合は表示
		if all_errors:
			print(f"\nエラー詳細 ({len(all_errors)}件):")
			for error in all_errors[:10]:  # 最初の10件のみ表示
				print(f"  - {error}")
			if len(all_errors) > 10:
				print(f"  ... 他 {len(all_errors) - 10}件のエラー")
		
		# 最終回エラーリストを表示
		if final_session_errors:
			print(f"\n最終回エラーリスト ({len(final_session_errors)}件):")
			for error in final_session_errors:
				print(f"  - {error}")
		
		# 通常の講義回数情報がある場合はJSONファイルを作成
		if all_lecture_sessions:
			output_file = create_lecture_session_json(all_lecture_sessions)
			print(f"\n通常の講義回数情報を保存しました: {output_file}")
		
		# 不定形講義回数情報がある場合はJSONファイルを作成
		if all_lecture_sessions_irregular:
			output_file = create_lecture_session_irregular_json(all_lecture_sessions_irregular)
			print(f"\n不定形講義回数情報を保存しました: {output_file}")
		
		# 統計情報を表示
		if all_lecture_sessions or all_lecture_sessions_irregular:
			print(f"\n統計情報:")
			print(f"  処理対象ファイル数: {stats['total_files']}")
			print(f"  成功ファイル数: {stats['successful_files']}")
			print(f"  エラーファイル数: {stats['error_files']}")
			print(f"  最終回エラーファイル数: {stats['final_session_error_files']}")
			print(f"  抽出された通常講義回数総数: {stats['total_lecture_sessions']}")
			print(f"  抽出された不定形講義回数総数: {stats['total_lecture_sessions_irregular']}")
		else:
			print("\n講義回数情報が見つかりませんでした。")
		
		# エラー内容をCSVファイルとして出力
		error_csv_file = create_error_csv(all_errors, final_session_errors, year)
		print(f"\nエラー内容をCSVファイルとして出力しました: {error_csv_file}")
		
	except FileNotFoundError as e:
		print(f"エラー: {e}")
	except KeyboardInterrupt:
		print("\n処理が中断されました。")
	except Exception as e:
		print(f"予期しないエラーが発生しました: {e}")
	finally:
		if session:
			session.close()

if __name__ == "__main__":
	main() 