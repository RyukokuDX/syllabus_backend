# File Version: v2.5.0
# Project Version: v2.5.0
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

# 現在のディレクトリをPythonパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

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

def expand_grade_range(grade_text: str) -> List[str]:
	"""学年の範囲を展開する"""
	if not grade_text:
		return []
	
	# 全学年の場合
	if '全学年' in grade_text:
		return ['学部1年', '学部2年', '学部3年', '学部4年', '修士1年', '修士2年', '博士1年', '博士2年', '博士3年']
	
	# ～を含む範囲の場合
	if '～' in grade_text:
		parts = grade_text.split('～')
		if len(parts) != 2:
			return [grade_text]
		
		start = parts[0].strip()
		end = parts[1].strip()
		
		# 学年の数値を取得
		start_match = re.search(r'(\d+)年', start)
		end_match = re.search(r'(\d+)年', end)
		
		if not start_match or not end_match:
			return [grade_text]
		
		start_year = int(start_match.group(1))
		end_year = int(end_match.group(1))
		
		# 範囲内の学年を生成
		grades = []
		for year in range(start_year, end_year + 1):
			if year <= 4:
				grades.append(f"学部{year}年")
			elif year <= 6:
				grades.append(f"修士{year-4}年")
			else:
				grades.append(f"博士{year-6}年")
		
		return grades
	
	# カンマ区切りの場合
	if '、' in grade_text:
		grade_list = [grade.strip() for grade in grade_text.split('、')]
		converted_grades = []
		for grade in grade_list:
			converted_grades.extend(convert_grade_format(grade))
		return converted_grades
	
	# 単一の学年の場合
	return convert_grade_format(grade_text)

def convert_grade_format(grade_text: str) -> List[str]:
	"""学年の形式を変換する"""
	if not grade_text:
		return []
	
	# 既に正しい形式の場合はそのまま返す
	if any(prefix in grade_text for prefix in ['学部', '修士', '博士']):
		return [grade_text]
	
	# 数字のみの場合（例：1年、2年など）
	match = re.search(r'(\d+)年', grade_text)
	if match:
		year = int(match.group(1))
		if year <= 4:
			return [f"学部{year}年"]
		elif year <= 6:
			return [f"修士{year-4}年"]
		else:
			return [f"博士{year-6}年"]
	
	# その他の形式の場合はそのまま返す
	return [grade_text]

def get_json_files(year: int) -> List[str]:
	"""指定された年度のすべてのJSONファイルのパスを取得する"""
	json_dir = os.path.join("src", "syllabus", str(year), "json")
	if not os.path.exists(json_dir):
		raise FileNotFoundError(f"ディレクトリが見つかりません: {json_dir}")
	
	json_files = [f for f in os.listdir(json_dir) if f.endswith('.json')]
	if not json_files:
		raise FileNotFoundError(f"JSONファイルが見つかりません: {json_dir}")
	
	return [os.path.join(json_dir, f) for f in json_files]

def extract_grade_info_from_single_json(json_data: Dict, session, year: int) -> List[Dict]:
	"""単一のJSONファイルから学年情報を抽出する"""
	grades = []
	
	# 科目コードを取得
	syllabus_code = json_data.get("科目コード", "")
	
	# 配当年次を取得
	basic_info = json_data.get("基本情報", {})
	grade_info = basic_info.get("配当年次", {})
	grade_text = grade_info.get("内容", "") if isinstance(grade_info, dict) else str(grade_info)
	
	if grade_text and syllabus_code:
		# syllabus_masterからsyllabus_idを取得
		syllabus_id = get_syllabus_master_id_from_db(session, syllabus_code, year)
		
		if syllabus_id:
			expanded_grades = expand_grade_range(grade_text)
			for grade in expanded_grades:
				grades.append({
					'syllabus_id': syllabus_id,
					'grade': grade
				})
	
	return grades

def process_grade_json(json_file: str, session, year: int) -> tuple[List[Dict], List[str]]:
	"""個別の学年JSONファイルを処理する"""
	errors = []
	try:
		with open(json_file, 'r', encoding='utf-8') as f:
			json_data = json.load(f)
		
		# 学年情報を抽出
		grades = extract_grade_info_from_single_json(json_data, session, year)
		
		if not grades:
			errors.append("学年情報が見つからないか、syllabus_masterに対応するレコードがありません")
		
		return grades, errors
		
	except json.JSONDecodeError as e:
		errors.append(f"JSONファイルの解析エラー: {str(e)}")
		return [], errors
	except Exception as e:
		errors.append(f"処理中にエラーが発生: {str(e)}")
		return [], errors

def create_grade_json(grades: List[Dict]) -> str:
	"""学年情報のJSONファイルを作成する"""
	output_dir = os.path.join("updates", "subject_grade", "add")
	os.makedirs(output_dir, exist_ok=True)
	
	# 現在の日時を取得してファイル名を生成
	current_time = datetime.now()
	filename = f"subject_grade_{current_time.strftime('%Y%m%d_%H%M')}.json"
	output_file = os.path.join(output_dir, filename)
	
	data = {
		"subject_grades": [{
			"syllabus_id": grade["syllabus_id"],
			"grade": grade["grade"],
			"created_at": current_time.isoformat()
		} for grade in sorted(grades, key=lambda x: (x["syllabus_id"], x["grade"]))]
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
		print(f"処理対象年度: {year}")
		
		# データベース接続
		session = get_db_connection()
		
		# すべてのJSONファイルを取得
		json_files = get_json_files(year)
		print(f"処理対象ファイル数: {len(json_files)}")
		
		# 学年情報を処理
		all_grades = []
		processed_count = 0
		error_count = 0
		skipped_count = 0
		
		# エラー情報を収集
		all_errors = []
		
		# 統計情報
		stats = {
			"total_files": len(json_files),
			"successful_files": 0,
			"error_files": 0,
			"total_grades": 0
		}
		
		print(f"\n処理開始: {len(json_files)}個のJSONファイル")
		
		# tqdmを使用してプログレスバーを表示
		for json_file in tqdm(json_files, desc="JSONファイルを処理中"):
			try:
				# 個別のJSONファイルを処理
				grades, errors = process_grade_json(json_file, session, year)
				
				if grades:
					all_grades.extend(grades)
					processed_count += len(grades)
					stats["successful_files"] += 1
					stats["total_grades"] += len(grades)
				else:
					skipped_count += 1
					stats["error_files"] += 1
				
				# エラー情報を収集
				if errors:
					for error in errors:
						all_errors.append(f"{os.path.basename(json_file)}: {error}")
					
			except Exception as e:
				error_count += 1
				stats["error_files"] += 1
				all_errors.append(f"{os.path.basename(json_file)}: 処理中にエラーが発生: {str(e)}")
				continue
		
		print(f"\n処理結果:")
		print(f"- 総ファイル数: {stats['total_files']}")
		print(f"- 成功ファイル数: {stats['successful_files']}")
		print(f"- エラーファイル数: {stats['error_files']}")
		print(f"- 総学年情報数: {stats['total_grades']}")
		print(f"- 成功: {processed_count}件")
		print(f"- エラー: {error_count}件")
		print(f"- スキップ: {skipped_count}件")
		
		# エラー情報をまとめて表示
		if all_errors:
			print(f"\nエラー詳細 ({len(all_errors)}件):")
			print("=" * 80)
			for i, error in enumerate(all_errors, 1):
				print(f"{i:3d}. {error}")
			print("=" * 80)
		
		# JSONファイルの作成
		if all_grades:
			output_file = create_grade_json(all_grades)
			print(f"\nJSONファイルを作成しました: {output_file}")
		else:
			print("\n処理可能な学年データが見つかりませんでした。")
		
	except Exception as e:
		print(f"エラーが発生しました: {str(e)}")
		print(f"エラーの種類: {type(e)}")
		raise
	finally:
		if session:
			session.close()

if __name__ == "__main__":
	main() 