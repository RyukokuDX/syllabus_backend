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
        # デバッグ情報を出力
        print(f"科目名を検索: {name}")
        print(f"科目名のバイト表現: {name.encode('utf-8')}")
        
        # 科目名IDを取得（重複を考慮）
        query = text("""
            SELECT subject_name_id 
            FROM subject_name 
            WHERE name = :name
            ORDER BY subject_name_id
            LIMIT 1
        """)
        print(f"実行するSQL: {query}")
        
        result = session.execute(
            query,
            {"name": name}
        ).first()
        
        if result:
            print(f"科目名IDを取得: {result[0]}")
        else:
            print(f"科目名が見つかりません: {name}")
            # データベース内の科目名を確認
            all_names = session.execute(text("""
                SELECT name, COUNT(*) as count 
                FROM subject_name 
                GROUP BY name 
                HAVING COUNT(*) > 1
            """)).fetchall()
            if all_names:
                print("重複している科目名一覧:")
                for n in all_names:
                    print(f"- {n[0]} (重複数: {n[1]})")
        
        return result[0] if result else None
    except Exception as e:
        print(f"警告: 科目名IDの取得中にエラーが発生しました: {str(e)}")
        print(f"エラーの種類: {type(e)}")
        session.rollback()
        return None

def get_syllabus_master_id_from_db(session, syllabus_code: str, syllabus_year: int) -> int:
    """シラバスマスターIDを取得する"""
    try:
        # デバッグ情報を出力
        print(f"シラバスマスターを検索: code={syllabus_code}, year={syllabus_year}")
        
        # シラバスマスターIDを取得
        query = text("""
            SELECT syllabus_id 
            FROM syllabus_master 
            WHERE syllabus_code = :code 
            AND syllabus_year = :year
        """)
        print(f"実行するSQL: {query}")
        
        result = session.execute(
            query,
            {"code": syllabus_code, "year": syllabus_year}
        ).first()
        
        if result:
            print(f"シラバスマスターIDを取得: {result[0]}")
        else:
            print(f"シラバスマスターが見つかりません: code={syllabus_code}, year={syllabus_year}")
            # データベース内のシラバスコードを確認
            all_codes = session.execute(text("""
                SELECT syllabus_code, syllabus_year, COUNT(*) as count 
                FROM syllabus_master 
                GROUP BY syllabus_code, syllabus_year 
                HAVING COUNT(*) > 1
            """)).fetchall()
            if all_codes:
                print("重複しているシラバスコード一覧:")
                for c in all_codes:
                    print(f"- {c[0]} (年度: {c[1]}, 重複数: {c[2]})")
        
        return result[0] if result else None
    except Exception as e:
        print(f"警告: シラバスマスターIDの取得中にエラーが発生しました: {str(e)}")
        print(f"エラーの種類: {type(e)}")
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
        all_syllabi = []
        processed_count = 0
        error_count = 0
        skipped_count = 0
        duplicate_subject_names = set()
        
        # スキップ理由の統計
        skip_reasons = {
            "missing_subject_name": 0,
            "missing_syllabus_code": 0,
            "missing_both": 0,
            "subject_name_not_found": 0,
            "syllabus_master_not_found": 0
        }
        
        # 科目名が不足しているデータを記録
        missing_subject_name_data = []
        
        # デバッグ情報を出力
        print("\n最初のシラバスデータ:")
        if json_data.get("content"):
            first_syllabus = json_data["content"][0]
            print(f"科目名: {first_syllabus.get('subject_name')}")
            print(f"シラバスコード: {first_syllabus.get('syllabus_code')}")
            print(f"年度: {first_syllabus.get('syllabus_year')}")
        
        total_records = len(json_data.get("content", []))
        print(f"\n処理対象レコード数: {total_records}")
        
        # 科目名の重複を確認
        subject_name_counts = {}
        for syllabus in json_data.get("content", []):
            subject_name = syllabus.get("subject_name")
            if subject_name:
                subject_name_counts[subject_name] = subject_name_counts.get(subject_name, 0) + 1
        
        duplicate_subjects = {name: count for name, count in subject_name_counts.items() if count > 1}
        if duplicate_subjects:
            print("\n重複する科目名一覧:")
            for name, count in duplicate_subjects.items():
                print(f"- {name}: {count}回")
        
        for syllabus in tqdm(json_data.get("content", []), desc="シラバス情報を処理中"):
            try:
                # 必須情報のチェック
                subject_name = syllabus.get("subject_name")
                syllabus_code = syllabus.get("syllabus_code")
                
                if not subject_name and not syllabus_code:
                    print(f"スキップ: 科目名とシラバスコードの両方が不足 - {syllabus}")
                    skip_reasons["missing_both"] += 1
                    skipped_count += 1
                    continue
                elif not subject_name:
                    print(f"スキップ: 科目名が不足 - シラバスコード: {syllabus_code}")
                    skip_reasons["missing_subject_name"] += 1
                    skipped_count += 1
                    # 科目名が不足しているデータを記録
                    missing_subject_name_data.append({
                        "syllabus_code": syllabus_code,
                        "syllabus_year": syllabus.get("syllabus_year"),
                        "term": syllabus.get("term"),
                        "campus": syllabus.get("campus"),
                        "credits": syllabus.get("credits"),
                        "raw_data": syllabus
                    })
                    continue
                elif not syllabus_code:
                    print(f"スキップ: シラバスコードが不足 - 科目名: {subject_name}")
                    skip_reasons["missing_syllabus_code"] += 1
                    skipped_count += 1
                    continue
                
                subject_name_id = get_subject_name_id_from_db(session, subject_name)
                syllabus_master_id = get_syllabus_master_id_from_db(session, syllabus_code, syllabus["syllabus_year"])
                
                if not subject_name_id:
                    print(f"スキップ: 科目名が見つかりません - {subject_name}")
                    skip_reasons["subject_name_not_found"] += 1
                    error_count += 1
                    continue
                
                if not syllabus_master_id:
                    print(f"スキップ: シラバスマスターが見つかりません - コード: {syllabus_code}, 年度: {syllabus['syllabus_year']}")
                    skip_reasons["syllabus_master_not_found"] += 1
                    error_count += 1
                    continue
                
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
                    all_syllabi.append(syllabus_info)
                    processed_count += 1
                    
                    if subject_name_counts.get(subject_name, 0) > 1:
                        duplicate_subject_names.add(subject_name)
                
            except Exception as e:
                print(f"エラー: シラバス処理中にエラーが発生: {str(e)}")
                error_count += 1
                continue
        
        print(f"\n処理結果:")
        print(f"- 総レコード数: {total_records}")
        print(f"- 成功: {processed_count}件")
        print(f"- エラー: {error_count}件")
        print(f"- スキップ: {skipped_count}件")
        print(f"- 合計: {len(all_syllabi)}件")
        print(f"- 重複する科目名の数: {len(duplicate_subject_names)}件")
        
        print("\nスキップ理由の内訳:")
        for reason, count in skip_reasons.items():
            print(f"- {reason}: {count}件")
        
        # 科目名が不足しているデータの詳細を表示
        if missing_subject_name_data:
            print("\n科目名が不足しているデータの詳細:")
            for i, data in enumerate(missing_subject_name_data, 1):
                print(f"\n{i}件目:")
                print(f"- シラバスコード: {data['syllabus_code']}")
                print(f"- 年度: {data['syllabus_year']}")
                print(f"- 学期: {data['term']}")
                print(f"- キャンパス: {data['campus']}")
                print(f"- 単位数: {data['credits']}")
                print("- 生データ:")
                for key, value in data['raw_data'].items():
                    print(f"  - {key}: {value}")
        
        # JSONファイルの作成
        output_file = create_syllabus_json(all_syllabi)
        print(f"JSONファイルを作成しました: {output_file}")
        
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        print(f"エラーの種類: {type(e)}")
        raise
    finally:
        if 'session' in locals():
            session.close()

if __name__ == "__main__":
    main() 