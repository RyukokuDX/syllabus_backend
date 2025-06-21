# File Version: v1.3.1
# Project Version: v1.3.21
# Last Updated: 2025-06-21

from datetime import datetime
import unicodedata
import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# プロジェクトルートをパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.db.database import SessionLocal
from src.db.models import SyllabusMaster

def normalize_subject_name(name: str) -> str:
    """科目名を正規化する"""
    # 前後の空白を削除
    name = name.strip()
    
    # 全角→半角（英数字・記号）
    name = unicodedata.normalize('NFKC', name)
    
    # 全角スペースを半角スペースに変換
    name = name.replace('　', ' ')
    
    # 連続するスペースを1つに
    while '  ' in name:
        name = name.replace('  ', ' ')
    
    # ハイフンの統一（全角→半角）
    hyphen_map = {
        '－': '-',  # 全角ハイフン
        'ー': '-',  # 長音記号
        '‐': '-',   # ハイフン
        '‑': '-',   # ノーブレークハイフン
        '‒': '-',   # フィギュアダッシュ
        '–': '-',   # エンダッシュ
        '—': '-',   # エムダッシュ
        '―': '-'    # 水平バー
    }
    for full, half in hyphen_map.items():
        name = name.replace(full, half)
    
    # 括弧の統一（全角→半角）
    bracket_map = {
        '（': '(', '）': ')',
        '［': '[', '］': ']',
        '｛': '{', '｝': '}',
        '【': '[', '】': ']',
        '〔': '[', '〕': ']',
        '〈': '<', '〉': '>',
        '《': '<', '》': '>',
        '〝': '"', '〟': '"',
        '″': '"', '″': '"',
        '′': "'", '′': "'"
    }
    for full, half in bracket_map.items():
        name = name.replace(full, half)
    
    # ローマ数字の統一（全角→半角）
    roman_map = {
        'Ⅰ': 'I', 'Ⅱ': 'II', 'Ⅲ': 'III', 'Ⅳ': 'IV', 'Ⅴ': 'V',
        'Ⅵ': 'VI', 'Ⅶ': 'VII', 'Ⅷ': 'VIII', 'Ⅸ': 'IX', 'Ⅹ': 'X'
    }
    for full, half in roman_map.items():
        name = name.replace(full, half)
    
    # 中点の統一（全角→半角）
    name = name.replace('・', '·')
    
    return name 

def get_current_year() -> int:
    """現在の年度を取得する
    
    Returns:
        int: 現在の年度（例：2024）
    """
    return datetime.now().year

def get_year_from_user() -> int:
    """ユーザーから年度を入力してもらう
    
    Returns:
        int: 入力された年度
        
    Raises:
        ValueError: 入力が無効な場合
    """
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

def get_db_connection():
    """データベース接続を取得する"""
    user = os.getenv('POSTGRES_USER', 'postgres')
    password = os.getenv('POSTGRES_PASSWORD', 'postgres')
    host = os.getenv('POSTGRES_HOST', 'localhost')
    port = os.getenv('POSTGRES_PORT', '5432')
    db = os.getenv('POSTGRES_DB', 'syllabus_db')  # デフォルトをsyllabus_dbに明示

    connection_string = f"postgresql://{user}:{password}@{host}:{port}/{db}"
    engine = create_engine(
        connection_string,
        connect_args={'options': '-c client_encoding=utf-8'}
    )
    Session = sessionmaker(bind=engine)
    session = Session()
    session.execute(text("SET client_encoding TO 'utf-8'"))
    session.commit()
    return session

def get_syllabus_master_id_from_db(session, syllabus_code: str, year: int) -> int:
    try:
        query = text("""
            SELECT syllabus_id 
            FROM syllabus_master 
            WHERE syllabus_code = :code 
            AND syllabus_year = :year
        """)
        result = session.execute(
            query,
            {"code": syllabus_code, "year": year}
        ).first()
        return result[0] if result else None
    except Exception as e:
        print(f"[DB接続エラー] syllabus_master取得時にエラー: {str(e)}")
        raise 