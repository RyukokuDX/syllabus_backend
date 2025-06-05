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

def get_subject_name_id_from_db(session, name: str) -> int:
    """科目名IDを取得する"""
    try:
        # 科目名を正規化
        normalized_name = normalize_subject_name(name)
        
        # まず完全一致で検索
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
            
        # 完全一致で見つからない場合、部分一致で検索
        query = text("""
            SELECT subject_name_id 
            FROM subject_name 
            WHERE name LIKE :name
            ORDER BY subject_name_id
            LIMIT 1
        """)
        
        result = session.execute(
            query,
            {"name": f"%{normalized_name}%"}
        ).first()
        
        if result:
            print(f"警告: 科目名の部分一致が見つかりました: {name} -> {normalized_name}")
            return result[0]
            
        # 部分一致でも見つからない場合、ローマ数字を除去して検索
        name_without_roman = normalized_name.replace('I', '').replace('II', '').replace('III', '').replace('IV', '').replace('V', '').strip()
        if name_without_roman != normalized_name:
            query = text("""
                SELECT subject_name_id 
                FROM subject_name 
                WHERE name LIKE :name
                ORDER BY subject_name_id
                LIMIT 1
            """)
            
            result = session.execute(
                query,
                {"name": f"%{name_without_roman}%"}
            ).first()
            
            if result:
                print(f"警告: ローマ数字を除去した科目名の部分一致が見つかりました: {name} -> {name_without_roman}")
                return result[0]
        
        print(f"エラー: 科目名が見つかりません: {name}")
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
        else:
            print(f"エラー: 学部が見つかりません: {faculty_name}")
            return None
            
    except Exception as e:
        print(f"エラー: 学部IDの取得中にエラーが発生しました: {str(e)}")
        session.rollback()
        return None

def get_class_id_from_db(session, class_name: str) -> int:
    """科目区分IDを取得する"""
    try:
        query = text("""
            SELECT class_id 
            FROM class 
            WHERE class_name = :name
            ORDER BY class_id
            LIMIT 1
        """)
        
        result = session.execute(
            query,
            {"name": class_name}
        ).first()
        
        if result:
            return result[0]
        else:
            print(f"エラー: 科目区分が見つかりません: {class_name}")
            return None
            
    except Exception as e:
        print(f"エラー: 科目区分IDの取得中にエラーが発生しました: {str(e)}")
        session.rollback()
        return None

def get_subclass_id_from_db(session, subclass_name: str) -> int:
    """科目小区分IDを取得する"""
    try:
        query = text("""
            SELECT subclass_id 
            FROM subclass 
            WHERE subclass_name = :name
            ORDER BY subclass_id
            LIMIT 1
        """)
        
        result = session.execute(
            query,
            {"name": subclass_name}
        ).first()
        
        if result:
            return result[0]
        else:
            print(f"エラー: 科目小区分が見つかりません: {subclass_name}")
            return None
            
    except Exception as e:
        print(f"エラー: 科目小区分IDの取得中にエラーが発生しました: {str(e)}")
        session.rollback()
        return None

def extract_syllabus_info(csv_file: str, db_config: Dict[str, str]) -> List[Dict]:
    """CSVからシラバス情報を抽出する"""
    syllabi = []
    session = get_db_connection(db_config)
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                subject_name_id = get_subject_name_id_from_db(session, row['科目名'])
                faculty_id = get_faculty_id_from_db(session, row['学部課程'])
                class_id = get_class_id_from_db(session, row['科目区分'])
                subclass_id = get_subclass_id_from_db(session, row['科目小区分']) if row['科目小区分'] else None
                
                if subject_name_id is None or faculty_id is None or class_id is None:
                    print(f"エラー: 必要なIDが見つかりません - 科目名: {row['科目名']}")
                    continue
                    
                syllabus_info = {
                    'subject_name_id': subject_name_id,
                    'faculty_id': faculty_id,
                    'curriculum_year': int(row['年度']),
                    'class_id': class_id,
                    'subclass_id': subclass_id,
                    'requirement_type': row['必須度'],
                    'created_at': datetime.now().isoformat()
                }
                syllabi.append(syllabus_info)
    finally:
        session.close()
    
    return syllabi

def create_syllabus_json(syllabi: Set[Dict]) -> str:
    """シラバス情報のJSONファイルを作成する"""
    output_dir = os.path.join("updates", "subject", "add")
    os.makedirs(output_dir, exist_ok=True)
    
    # 現在の日時を取得してファイル名を生成
    current_time = datetime.now()
    filename = f"subject_{current_time.strftime('%Y%m%d_%H%M')}.json"
    output_file = os.path.join(output_dir, filename)
    
    data = {
        "subjects": [{
            "subject_name_id": syllabus["subject_name_id"],
            "faculty_id": syllabus["faculty_id"],
            "curriculum_year": syllabus["curriculum_year"],
            "class_id": syllabus["class_id"],
            "subclass_id": syllabus["subclass_id"],
            "requirement_type": syllabus["requirement_type"],
            "created_at": syllabus["created_at"]
        } for syllabus in sorted(syllabi, key=lambda x: (
            x["subject_name_id"],
            x["faculty_id"],
            x["curriculum_year"],
            x["class_id"],
            x["subclass_id"] if x["subclass_id"] is not None else 0
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
        
        # シラバス情報の抽出
        all_syllabi = set()
        for csv_file in tqdm(csv_files, desc="CSVファイル処理中"):
            syllabi = extract_syllabus_info(csv_file, db_config)
            
            # 各シラバスの情報をタプルに変換してセットに追加（重複を防ぐため）
            for syllabus in syllabi:
                syllabus_tuple = tuple(sorted(syllabus.items()))
                all_syllabi.add(syllabus_tuple)
        
        # タプルを辞書に戻す
        syllabus_dicts = [dict(t) for t in all_syllabi]
        print(f"抽出されたシラバス情報: {len(syllabus_dicts)}件")
        
        # JSONファイルの作成
        output_file = create_syllabus_json(syllabus_dicts)
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