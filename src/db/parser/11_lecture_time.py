# File Version: v1.3.0
# Project Version: v1.3.18
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

def parse_lecture_time(time_text: str) -> List[Dict]:
	"""講義時間テキストを解析して曜日と時限を抽出する"""
	lecture_times = []
	
	if not time_text:
		return lecture_times
	
	# 集中講義の場合
	if '集中' in time_text:
		lecture_times.append({
			'day_of_week': '集中',
			'period': 0
		})
		return lecture_times
	
	# 通常の講義時間を解析
	# 例: "後期 水２(Y019)" → 水曜日2限
	# 例: "前期 月１・水３" → 月曜日1限、水曜日3限
	# 例: "１Ｑ 木４(YJ11)・木５（ペア）" → 木曜日4限、木曜日5限
	
	# 曜日のマッピング
	day_mapping = {
		'月': '月',
		'火': '火', 
		'水': '水',
		'木': '木',
		'金': '金',
		'土': '土',
		'日': '日'
	}
	
	# utils.pyの正規化機能を使用して全角数字を半角に変換
	time_text_normalized = normalize_subject_name(time_text)
	
	# 複数の時限を分割（・で区切られている場合）
	time_parts = time_text_normalized.split('')  # 正規化された中点で分割
	
	for part in time_parts:
		part = part.strip()
		if not part:
			continue
		
		# 曜日と時限のパターンを検索
		# パターン: 曜日 + 数字（1-6限）
		pattern = r'([月火水木金土日])([1-6])'
		matches = re.findall(pattern, part)
		
		for day_char, period_str in matches:
			if day_char in day_mapping:
				lecture_times.append({
					'day_of_week': day_mapping[day_char],
					'period': int(period_str)
				})
	
	# マッチしない場合は、テキスト全体をそのまま使用
	if not lecture_times and time_text.strip():
		lecture_times.append({
			'day_of_week': time_text.strip(),
			'period': 0
		})
	
	return lecture_times

def get_json_files(year: int) -> List[str]:
	"""指定された年度のすべてのJSONファイルのパスを取得する"""
	json_dir = os.path.join("src", "syllabus", str(year), "json")
	if not os.path.exists(json_dir):
		raise FileNotFoundError(f"ディレクトリが見つかりません: {json_dir}")
	
	json_files = [f for f in os.listdir(json_dir) if f.endswith('.json')]
	if not json_files:
		raise FileNotFoundError(f"JSONファイルが見つかりません: {json_dir}")
	
	return [os.path.join(json_dir, f) for f in json_files]

def extract_lecture_time_from_single_json(json_data: Dict, session, year: int) -> List[Dict]:
	"""単一のJSONファイルから講義時間情報を抽出する"""
	lecture_times = []
	
	# 科目コードを取得
	syllabus_code = json_data.get("科目コード", "")
	
	# 開講期・曜講時を取得
	basic_info = json_data.get("基本情報", {})
	time_info = basic_info.get("開講期・曜講時", {})
	time_text = time_info.get("内容", "") if isinstance(time_info, dict) else str(time_info)
	
	if time_text and syllabus_code:
		# syllabus_masterからsyllabus_idを取得
		syllabus_id = get_syllabus_master_id_from_db(session, syllabus_code, year)
		
		if syllabus_id:
			# 講義時間を解析
			parsed_times = parse_lecture_time(time_text)
			for time_data in parsed_times:
				lecture_times.append({
					'syllabus_id': syllabus_id,
					'day_of_week': time_data['day_of_week'],
					'period': time_data['period']
				})
	
	return lecture_times

def process_lecture_time_json(json_file: str, session, year: int) -> tuple[List[Dict], List[str]]:
	"""個別の講義時間JSONファイルを処理する"""
	errors = []
	try:
		with open(json_file, 'r', encoding='utf-8') as f:
			json_data = json.load(f)
		
		# 講義時間情報を抽出
		lecture_times = extract_lecture_time_from_single_json(json_data, session, year)
		
		if not lecture_times:
			errors.append("講義時間情報が見つからないか、syllabus_masterに対応するレコードがありません")
		
		return lecture_times, errors
		
	except json.JSONDecodeError as e:
		errors.append(f"JSONファイルの解析エラー: {str(e)}")
		return [], errors
	except Exception as e:
		errors.append(f"処理中にエラーが発生: {str(e)}")
		return [], errors

def create_lecture_time_json(lecture_times: List[Dict]) -> str:
	"""講義時間情報のJSONファイルを作成する"""
	output_dir = os.path.join("updates", "lecture_time", "add")
	os.makedirs(output_dir, exist_ok=True)
	
	# 現在の日時を取得してファイル名を生成
	current_time = datetime.now()
	filename = f"lecture_time_{current_time.strftime('%Y%m%d_%H%M')}.json"
	output_file = os.path.join(output_dir, filename)
	
	data = {
		"lecture_times": [{
			"syllabus_id": time["syllabus_id"],
			"day_of_week": time["day_of_week"],
			"period": time["period"],
			"created_at": current_time.isoformat()
		} for time in sorted(lecture_times, key=lambda x: (x["syllabus_id"], x["day_of_week"], x["period"]))]
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
		
		# 講義時間情報を処理
		all_lecture_times = []
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
			"total_lecture_times": 0
		}
		
		print(f"\n処理開始: {len(json_files)}個のJSONファイル")
		
		# tqdmを使用してプログレスバーを表示
		for json_file in tqdm(json_files, desc="JSONファイルを処理中"):
			try:
				# 個別のJSONファイルを処理
				lecture_times, errors = process_lecture_time_json(json_file, session, year)
				
				if lecture_times:
					all_lecture_times.extend(lecture_times)
					processed_count += len(lecture_times)
					stats["successful_files"] += 1
					stats["total_lecture_times"] += len(lecture_times)
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
		print(f"- 総講義時間数: {stats['total_lecture_times']}")
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
		if all_lecture_times:
			output_file = create_lecture_time_json(all_lecture_times)
			print(f"\nJSONファイルを作成しました: {output_file}")
		else:
			print("\n処理可能な講義時間データが見つかりませんでした。")
		
	except Exception as e:
		print(f"エラーが発生しました: {str(e)}")
		print(f"エラーの種類: {type(e)}")
		raise
	finally:
		if session:
			session.close()

if __name__ == "__main__":
	main() 