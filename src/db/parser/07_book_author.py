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
    engine = create_engine(connection_string)
    
    # セッションを作成
    Session = sessionmaker(bind=engine)
    return Session()

def get_book_id_from_db(session, title: str) -> int:
    """書籍IDを取得する"""
    try:
        result = session.execute(
            text("SELECT book_id FROM book WHERE title = :title"),
            {"title": title}
        ).first()
        return result[0] if result else None
    except Exception as e:
        print(f"警告: 書籍IDの取得中にエラーが発生しました: {str(e)}")
        return None

def process_book_authors(session, book_id: int, author: str) -> None:
    """書籍著者情報を処理する"""
    if not author:  # NULLの場合はスキップ
        return

    try:
        # 著者情報を追加
        session.execute(
            text("""
                INSERT INTO book_author (book_id, author_name, created_at)
                VALUES (:book_id, :author_name, :created_at)
                ON CONFLICT DO NOTHING
            """),
            {
                "book_id": book_id,
                "author_name": author,
                "created_at": datetime.now()
            }
        )
        session.commit()
    except Exception as e:
        print(f"警告: 著者情報の追加中にエラーが発生しました: {str(e)}")
        session.rollback()

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
        
        # 書籍情報を処理
        processed_count = 0
        for syllabus in tqdm(json_data.get("content", []), desc="書籍著者情報を処理中"):
            for book in syllabus.get("books", []):
                if not book.get("title") or not book.get("author"):
                    continue
                
                book_id = get_book_id_from_db(session, book["title"])
                if book_id:
                    process_book_authors(session, book_id, book["author"])
                    processed_count += 1
        
        print(f"処理完了: {processed_count}件の書籍著者情報を処理しました")
        
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        raise
    finally:
        if 'session' in locals():
            session.close()

if __name__ == "__main__":
    main() 