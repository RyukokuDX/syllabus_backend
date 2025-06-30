# File Version: v1.5.0
# Project Version: v1.5.0
# Last Updated: 2025-06-30

import os
import json
import sys
from typing import List, Dict, Set
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm

# 現在のディレクトリをPythonパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from utils import normalize_subject_name

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

def get_subject_name_id_from_db(session, name: str) -> int:
    """科目名IDを取得する"""
    try:
        # 科目名を正規化
        normalized_name = normalize_subject_name(name)
        
        # 科目名IDを取得（重複を考慮）
        query = text("""
            SELECT subject_name_id 
            FROM subject_name 
            WHERE name = :name
            ORDER BY subject_name_id
            LIMIT 1
        """)
        
        result = session.execute(
            query,
            {"name": normalized_name}
        ).first()
        
        if result:
            return result[0]
        else:
            return None
    except Exception as e:
        session.rollback()
        return None

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

def create_syllabus_json(syllabi: List[Dict]) -> str:
    """シラバス情報のJSONファイルを作成する"""
    output_dir = os.path.join("updates", "syllabus", "add")
    os.makedirs(output_dir, exist_ok=True)
    
    # 現在の日時を取得してファイル名を生成
    current_time = datetime.now()
    filename = f"syllabus_{current_time.strftime('%Y%m%d_%H%M')}.json"
    output_file = os.path.join(output_dir, filename)
    
    data = {
        "syllabuses": [{
            "syllabus_id": syllabus["syllabus_id"],
            "subject_name_id": syllabus["subject_name_id"],
            "subtitle": syllabus["subtitle"],
            "term": syllabus["term"],
            "campus": syllabus["campus"],
            "credits": syllabus["credits"],
            "goals": syllabus["goals"],
            "summary": syllabus["summary"],
            "attainment": syllabus["attainment"],
            "methods": syllabus["methods"],
            "outside_study": syllabus["outside_study"],
            "textbook_comment": syllabus["textbook_comment"],
            "reference_comment": syllabus["reference_comment"],
            "grading_comment": syllabus["grading_comment"],
            "advice": syllabus["advice"],
            "created_at": current_time.isoformat()
        } for syllabus in sorted(syllabi, key=lambda x: x["syllabus_id"])]
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return output_file

def get_latest_json(year: int) -> str:
    """指定された年度の最新のJSONファイルを取得する"""
    data_dir = os.path.join("src", "syllabus", str(year), "json")
    if not os.path.exists(data_dir):
        raise FileNotFoundError(f"ディレクトリが見つかりません: {data_dir}")
    
    json_files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
    if not json_files:
        raise FileNotFoundError(f"JSONファイルが見つかりません: {data_dir}")
    
    # ファイル名でソートして最新のものを取得
    latest_json = sorted(json_files)[-1]
    return os.path.join(data_dir, latest_json)

def get_all_json_files(year: int) -> List[str]:
    """指定された年度のすべてのJSONファイルを取得する"""
    data_dir = os.path.join("src", "syllabus", str(year), "json")
    if not os.path.exists(data_dir):
        raise FileNotFoundError(f"ディレクトリが見つかりません: {data_dir}")
    
    json_files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
    if not json_files:
        raise FileNotFoundError(f"JSONファイルが見つかりません: {data_dir}")
    
    # ファイル名でソート
    json_files.sort()
    return [os.path.join(data_dir, f) for f in json_files]

def get_year_from_user() -> int:
    """ユーザーから年度を入力してもらう"""
    while True:
        try:
            year = input("年度を入力してください（空の場合は現在の年度）: ").strip()
            if not year:
                return datetime.now().year
            year = int(year)
            if 2000 <= year <= 2100:  # 妥当な年度の範囲をチェック
                return year
            print("2000年から2100年の間で入力してください。")
        except ValueError:
            print("有効な数値を入力してください。")

def process_syllabus_json(json_file: str, session) -> tuple[List[Dict], List[str]]:
	"""個別のシラバスJSONファイルを処理する"""
	errors = []
	try:
		with open(json_file, 'r', encoding='utf-8') as f:
			json_data = json.load(f)
		
		# 基本情報からデータを抽出
		basic_info = json_data.get("基本情報", {})
		detail_info = json_data.get("詳細情報", {})
		
		# 必須情報の取得
		subject_name = basic_info.get("科目名", {}).get("内容")
		syllabus_code = json_data.get("科目コード")
		syllabus_year = int(basic_info.get("開講年度", {}).get("内容", "2025"))
		
		if not subject_name or not syllabus_code:
			errors.append(f"必須情報が不足 - 科目名: {subject_name}, 科目コード: {syllabus_code}")
			return [], errors
		
		# 科目名を正規化
		normalized_subject_name = normalize_subject_name(subject_name)
		
		# データベースからIDを取得
		subject_name_id = get_subject_name_id_from_db(session, normalized_subject_name)
		syllabus_master_id = get_syllabus_master_id_from_db(session, syllabus_code, syllabus_year)
		
		if not subject_name_id:
			errors.append(f"科目名が見つかりません - '{normalized_subject_name}' (元: '{subject_name}')")
			return [], errors
		
		if not syllabus_master_id:
			errors.append(f"シラバスマスターが見つかりません - コード: {syllabus_code}, 年度: {syllabus_year}")
			return [], errors
		
		# 開講期・曜講時から学期を抽出
		term_info = basic_info.get("開講期・曜講時", {}).get("内容", "")
		term = ""
		
		# 学期の抽出（前期、後期、通年、1Q、2Q、3Q、4Qなど）
		if "前期" in term_info:
			term = "前期"
		elif "後期" in term_info:
			term = "後期"
		elif "通年" in term_info:
			term = "通年"
		elif "１Ｑ" in term_info or "1Q" in term_info:
			term = "1Q"
		elif "２Ｑ" in term_info or "2Q" in term_info:
			term = "2Q"
		elif "３Ｑ" in term_info or "3Q" in term_info:
			term = "3Q"
		elif "４Ｑ" in term_info or "4Q" in term_info:
			term = "4Q"
		else:
			term = term_info  # その他の場合はそのまま使用
		
		# キャンパス情報の取得
		campus = basic_info.get("開講キャンパス", {}).get("内容", "")
		
		# 単位数の取得
		credits = int(basic_info.get("単位", {}).get("内容", "0"))
		
		# 詳細情報の取得
		summary = detail_info.get("講義概要", {}).get("内容", "")
		goals = detail_info.get("目的", {}).get("内容", None)
		attainment = detail_info.get("到達目標", {}).get("内容", "")  # 到達目標を正しく設定
		methods = detail_info.get("講義方法", {}).get("内容", "")
		outside_study = detail_info.get("授業外学習", {}).get("内容", "")
		
		# テキストと参考文献のコメント
		textbook_info = detail_info.get("テキスト", {})
		textbook_comment = ""
		if textbook_info.get("内容", {}).get("自由記載"):
			textbook_comment = textbook_info.get("内容", {}).get("自由記載", "")
		
		reference_info = detail_info.get("参考文献", {})
		reference_comment = ""
		if reference_info.get("内容", {}).get("自由記載"):
			reference_comment = reference_info.get("内容", {}).get("自由記載", "")
		
		# 成績評価の方法
		grading_info = detail_info.get("成績評価の方法", {})
		grading_comment = ""
		if grading_info.get("内容", {}).get("自由記載"):
			grading_comment = grading_info.get("内容", {}).get("自由記載", "")
		
		# 履修上の注意
		advice = detail_info.get("履修上の注意・担当者からの一言", {}).get("内容", "")
		
		# サブタイトル（サブタイトルフィールドから取得）
		subtitle = basic_info.get("サブタイトル", {}).get("内容", "")
		if subtitle is None:
			subtitle = ""
		
		syllabus_info = {
			"syllabus_id": syllabus_master_id,
			"subject_name_id": subject_name_id,
			"subtitle": subtitle,
			"term": term,
			"campus": campus,
			"credits": credits,
			"goals": goals,
			"summary": summary,
			"attainment": attainment,
			"methods": methods,
			"outside_study": outside_study,
			"textbook_comment": textbook_comment,
			"reference_comment": reference_comment,
			"grading_comment": grading_comment,
			"advice": advice
		}
		
		return [syllabus_info], errors
		
	except Exception as e:
		errors.append(f"処理中にエラーが発生: {str(e)}")
		return [], errors

def main():
	"""メイン処理"""
	try:
		# 年度の取得
		year = get_year_from_user()
		print(f"処理対象年度: {year}")
		
		# すべてのJSONファイルを取得
		json_files = get_all_json_files(year)
		print(f"処理対象ファイル数: {len(json_files)}")
		
		# データベース接続
		session = get_db_connection()
		
		# シラバス情報を処理
		all_syllabi = []
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
			"total_syllabi": 0
		}
		
		print(f"\n処理開始: {len(json_files)}個のJSONファイル")
		
		# tqdmを使用してプログレスバーを表示
		for json_file in tqdm(json_files, desc="JSONファイルを処理中"):
			try:
				# 個別のJSONファイルを処理
				syllabi, errors = process_syllabus_json(json_file, session)
				
				if syllabi:
					all_syllabi.extend(syllabi)
					processed_count += len(syllabi)
					stats["successful_files"] += 1
					stats["total_syllabi"] += len(syllabi)
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
		print(f"- 総シラバス数: {stats['total_syllabi']}")
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
		if all_syllabi:
			output_file = create_syllabus_json(all_syllabi)
			print(f"\nJSONファイルを作成しました: {output_file}")
		else:
			print("\n処理可能なシラバスデータが見つかりませんでした。")
		
	except Exception as e:
		print(f"エラーが発生しました: {str(e)}")
		print(f"エラーの種類: {type(e)}")
		raise
	finally:
		if 'session' in locals():
			session.close()

if __name__ == "__main__":
	main() 