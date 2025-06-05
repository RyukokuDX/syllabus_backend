import os
import json
import csv
from typing import List, Dict, Set
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm
from dotenv import load_dotenv
from .utils import normalize_subject_name

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

def get_csv_files(year: int) -> List[str]:
    """指定された年度のCSVファイルのパスを取得する"""
    base_dir = os.path.join("src", "course_guide", str(year), "csv")
    if not os.path.exists(base_dir):
        raise FileNotFoundError(f"ディレクトリが見つかりません: {base_dir}")
    
    csv_files = [f for f in os.listdir(base_dir) if f.endswith('.csv')]
    if not csv_files:
        raise FileNotFoundError(f"CSVファイルが見つかりません: {base_dir}")
    
    return [os.path.join(base_dir, f) for f in csv_files]

def get_db_connection(db_config: Dict[str, str]):
    """データベース接続を取得する"""
    # 接続文字列を作成
    connection_string = f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['db']}"
    
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

def get_subject_name_id_from_db(session, subject_name: str) -> int:
    """科目名IDを取得する"""
    try:
        # 科目名を正規化
        normalized_name = normalize_subject_name(subject_name)
        
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
        return None
            
    except Exception as e:
        print(f"エラー: 科目名IDの取得中にエラーが発生しました: {str(e)}")
        session.rollback()
        return None

def get_faculty_id_from_db(session, faculty_name: str) -> int:
    """学部IDを取得する"""
    try:
        query = text("""
            SELECT faculty_id 
            FROM faculty 
            WHERE faculty_name = :name
            ORDER BY faculty_id
            LIMIT 1
        """)
        
        result = session.execute(
            query,
            {"name": faculty_name}
        ).first()
        
        if result:
            return result[0]
        return None
            
    except Exception as e:
        print(f"エラー: 学部IDの取得中にエラーが発生しました: {str(e)}")
        session.rollback()
        return None

def get_subject_id_from_db(session, subject_name_id: int, faculty_id: int, curriculum_year: int) -> int:
    """科目IDを取得する"""
    try:
        query = text("""
            SELECT subject_id 
            FROM subject 
            WHERE subject_name_id = :subject_name_id
            AND faculty_id = :faculty_id
            AND curriculum_year = :curriculum_year
            ORDER BY subject_id
            LIMIT 1
        """)
        
        result = session.execute(
            query,
            {
                "subject_name_id": subject_name_id,
                "faculty_id": faculty_id,
                "curriculum_year": curriculum_year
            }
        ).first()
        
        if result:
            return result[0]
        return None
            
    except Exception as e:
        print(f"エラー: 科目IDの取得中にエラーが発生しました: {str(e)}")
        session.rollback()
        return None

def get_attribute_id_from_db(session, attribute_name: str) -> int:
    """属性IDを取得する"""
    try:
        query = text("""
            SELECT attribute_id 
            FROM subject_attribute 
            WHERE attribute_name = :name
            ORDER BY attribute_id
            LIMIT 1
        """)
        
        result = session.execute(
            query,
            {"name": attribute_name}
        ).first()
        
        if result:
            return result[0]
        else:
            print(f"エラー: 属性が見つかりません: {attribute_name}")
            return None
            
    except Exception as e:
        print(f"エラー: 属性IDの取得中にエラーが発生しました: {str(e)}")
        session.rollback()
        return None

def extract_subject_attribute_values(csv_file: str, db_config: Dict[str, str]) -> List[Dict]:
    """CSVから科目属性値情報を抽出する"""
    attribute_values = []
    session = get_db_connection(db_config)
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                # 17_subject.pyで処理したフィールドを除外
                processed_fields = {'科目名', '学部課程', '年度', '科目区分', '科目小区分', '必須度'}
                attribute_fields = set(row.keys()) - processed_fields
                
                # 科目名IDを取得
                subject_name_id = get_subject_name_id_from_db(session, row['科目名'])
                if subject_name_id is None:
                    continue
                
                # 学部IDを取得
                faculty_id = get_faculty_id_from_db(session, row['学部課程'])
                if faculty_id is None:
                    continue
                
                # 科目IDを取得
                subject_id = get_subject_id_from_db(session, subject_name_id, faculty_id, int(row['年度']))
                if subject_id is None:
                    continue
                
                # 各属性フィールドを処理
                for field_name in attribute_fields:
                    value = row[field_name]
                    if value == "NULL":  # CSVのnull値は文字列"NULL"として保存されている
                        continue
                        
                    attribute_id = get_attribute_id_from_db(session, field_name)
                    if attribute_id is None:
                        continue
                    
                    attribute_value_info = {
                        'subject_id': subject_id,
                        'attribute_id': attribute_id,
                        'value': value,
                        'created_at': datetime.now().isoformat()
                    }
                    attribute_values.append(attribute_value_info)
    finally:
        session.close()
    
    return attribute_values

def create_subject_attribute_value_json(attribute_values: List[Dict]) -> str:
    """科目属性値情報のJSONファイルを作成する"""
    output_dir = os.path.join("updates", "subject_attribute_value", "add")
    os.makedirs(output_dir, exist_ok=True)
    
    # 現在の日時を取得してファイル名を生成
    current_time = datetime.now()
    filename = f"subject_attribute_value_{current_time.strftime('%Y%m%d_%H%M')}.json"
    output_file = os.path.join(output_dir, filename)
    
    data = {
        "subject_attribute_values": [{
            "subject_id": value["subject_id"],
            "attribute_id": value["attribute_id"],
            "value": value["value"],
            "created_at": value["created_at"]
        } for value in sorted(attribute_values, key=lambda x: (
            x["subject_id"],
            x["attribute_id"]
        ))]
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return output_file

def main(db_config: Dict[str, str]):
    """メイン処理"""
    try:
        # 年度の取得
        year = get_year_from_user()
        print(f"処理対象年度: {year}")
        
        # CSVファイルの取得
        csv_files = get_csv_files(year)
        print(f"処理対象ファイル数: {len(csv_files)}")
        
        # 科目属性値情報の抽出
        all_attribute_values = []
        for csv_file in tqdm(csv_files, desc="CSVファイル処理中"):
            attribute_values = extract_subject_attribute_values(csv_file, db_config)
            all_attribute_values.extend(attribute_values)
        
        # 重複を除去
        unique_attribute_values = []
        seen_values = set()
        for value in all_attribute_values:
            value_key = (value['subject_id'], value['attribute_id'], value['value'])
            if value_key not in seen_values:
                seen_values.add(value_key)
                unique_attribute_values.append(value)
        
        print(f"抽出された科目属性値情報: {len(unique_attribute_values)}件")
        
        # JSONファイルの作成
        output_file = create_subject_attribute_value_json(unique_attribute_values)
        print(f"JSONファイルを作成しました: {output_file}")
        
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        raise

if __name__ == "__main__":
    # .envファイルから設定を読み込む
    load_dotenv()
    
    # データベース設定を取得（デフォルト値を設定）
    db_config = {
        'user': os.getenv('POSTGRES_USER', 'postgres'),
        'password': os.getenv('POSTGRES_PASSWORD', 'postgres'),
        'host': os.getenv('POSTGRES_HOST', 'localhost'),
        'port': os.getenv('POSTGRES_PORT', '5432'),
        'db': os.getenv('POSTGRES_DB', 'syllabus_db')
    }
    
    main(db_config) 