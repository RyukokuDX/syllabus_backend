import os
import json
from typing import List, Dict, Set
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm

def get_db_connection():
    """データベース接続を取得する"""
    # 環境変数から接続情報を取得
    user = os.getenv('POSTGRES_USER', 'postgres')
    password = os.getenv('POSTGRES_PASSWORD', 'postgres')
    host = os.getenv('POSTGRES_HOST', 'postgres-db')
    port = os.getenv('POSTGRES_PORT', '5432')
    db = os.getenv('POSTGRES_DB', 'syllabus_db')

    # 接続文字列を作成
    connection_string = f"postgresql://{user}:{password}@{host}:{port}/{db}"
    
    # エンジンを作成
    engine = create_engine(
        connection_string,
        connect_args={
            'options': '-c client_encoding=utf8'
        }
    )
    
    # セッションを作成
    Session = sessionmaker(bind=engine)
    return Session()

def get_subject_name_id_from_db(session, name: str) -> int:
    """科目名IDを取得する"""
    try:
        # 文字エンコーディングを設定
        session.execute(text("SET client_encoding TO 'utf8'"))
        session.commit()
        
        # デバッグ情報を出力
        print(f"科目名を検索: {name}")
        
        # 科目名IDを取得
        result = session.execute(
            text("SELECT subject_name_id FROM subject_name WHERE name = :name"),
            {"name": name}
        ).first()
        
        if result:
            print(f"科目名IDを取得: {result[0]}")
        else:
            print(f"科目名が見つかりません: {name}")
        
        return result[0] if result else None
    except Exception as e:
        print(f"警告: 科目名IDの取得中にエラーが発生しました: {str(e)}")
        session.rollback()
        return None

def get_syllabus_master_id_from_db(session, syllabus_code: str, syllabus_year: int) -> int:
    """シラバスマスターIDを取得する"""
    try:
        # 文字エンコーディングを設定
        session.execute(text("SET client_encoding TO 'utf8'"))
        session.commit()
        
        # デバッグ情報を出力
        print(f"シラバスマスターを検索: code={syllabus_code}, year={syllabus_year}")
        
        # シラバスマスターIDを取得
        result = session.execute(
            text("SELECT syllabus_id FROM syllabus_master WHERE syllabus_code = :code AND syllabus_year = :year"),
            {"code": syllabus_code, "year": syllabus_year}
        ).first()
        
        if result:
            print(f"シラバスマスターIDを取得: {result[0]}")
        else:
            print(f"シラバスマスターが見つかりません: code={syllabus_code}, year={syllabus_year}")
        
        return result[0] if result else None
    except Exception as e:
        print(f"警告: シラバスマスターIDの取得中にエラーが発生しました: {str(e)}")
        session.rollback()
        return None

def create_syllabus_json(syllabi: Set[Dict]) -> str:
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
            "summary": syllabus["summary"],
            "goals": syllabus["goals"],
            "methods": syllabus["methods"],
            "outside_study": syllabus["outside_study"],
            "notes": syllabus["notes"],
            "remarks": syllabus["remarks"],
            "created_at": current_time.isoformat()
        } for syllabus in sorted(syllabi, key=lambda x: x["syllabus_id"])]
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return output_file

def get_latest_json(year: int) -> str:
    """指定された年度の最新のJSONファイルを取得する"""
    data_dir = os.path.join("src", "syllabus", str(year), "data")
    if not os.path.exists(data_dir):
        raise FileNotFoundError(f"ディレクトリが見つかりません: {data_dir}")
    
    json_files = [f for f in os.listdir(data_dir) if f.startswith('syllabus_') and f.endswith('.json')]
    if not json_files:
        raise FileNotFoundError(f"JSONファイルが見つかりません: {data_dir}")
    
    # ファイル名のタイムスタンプでソートして最新のものを取得
    latest_json = sorted(json_files)[-1]
    return os.path.join(data_dir, latest_json)

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

def main():
    """メイン処理"""
    try:
        # 年度の取得
        year = get_year_from_user()
        print(f"処理対象年度: {year}")
        
        # 最新のJSONファイルを取得
        json_file = get_latest_json(year)
        print(f"処理対象ファイル: {json_file}")
        
        # JSONファイルを読み込む
        with open(json_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        # データベース接続
        session = get_db_connection()
        
        # シラバス情報を処理
        all_syllabi = set()
        processed_count = 0
        
        # デバッグ情報を出力
        print("\n最初のシラバスデータ:")
        if json_data.get("content"):
            first_syllabus = json_data["content"][0]
            print(f"科目名: {first_syllabus.get('subject_name')}")
            print(f"シラバスコード: {first_syllabus.get('syllabus_code')}")
            print(f"年度: {first_syllabus.get('syllabus_year')}")
        
        for syllabus in tqdm(json_data.get("content", []), desc="シラバス情報を処理中"):
            if not syllabus.get("subject_name") or not syllabus.get("syllabus_code"):
                continue
            
            subject_name_id = get_subject_name_id_from_db(session, syllabus["subject_name"])
            syllabus_master_id = get_syllabus_master_id_from_db(session, syllabus["syllabus_code"], syllabus["syllabus_year"])
            
            if subject_name_id and syllabus_master_id:
                syllabus_info = {
                    "syllabus_id": syllabus_master_id,
                    "subject_name_id": subject_name_id,
                    "subtitle": syllabus.get("subtitle", ""),
                    "term": syllabus["term"],
                    "campus": syllabus["campus"],
                    "credits": syllabus["credits"],
                    "summary": syllabus.get("summary", ""),
                    "goals": syllabus.get("goals", ""),
                    "methods": syllabus.get("methods", ""),
                    "outside_study": syllabus.get("outside_study", ""),
                    "notes": syllabus.get("notes", ""),
                    "remarks": syllabus.get("remarks", "")
                }
                syllabus_tuple = tuple(sorted(syllabus_info.items()))
                all_syllabi.add(syllabus_tuple)
                processed_count += 1
        
        # タプルを辞書に戻す
        syllabus_dicts = [dict(t) for t in all_syllabi]
        print(f"抽出されたシラバス情報: {len(syllabus_dicts)}件")
        
        # JSONファイルの作成
        output_file = create_syllabus_json(syllabus_dicts)
        print(f"JSONファイルを作成しました: {output_file}")
        
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        raise
    finally:
        if 'session' in locals():
            session.close()

if __name__ == "__main__":
    main() 