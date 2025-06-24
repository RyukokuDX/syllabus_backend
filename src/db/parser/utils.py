# -*- coding: utf-8 -*-
# File Version: v1.3.2
# Project Version: v1.3.34
# Last Updated: 2025-06-24
# curosrはversionをいじるな

from datetime import datetime
import unicodedata
import sys
import os
from typing import Tuple
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
    
    # チルダの統一（全角→半角）
    name = name.replace('～', '~')
    name = name.replace('〜', '~')
    
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

def is_regular_session(session_text: str) -> bool:
    """講義セッションが正規かどうかを判定する"""
    if not session_text:
        return False
    # 部、月の混入判定
    if '部' in session_text or '月' in session_text:
        return False
    # 正規化
    normalized = normalize_subject_name(session_text)
    # 全角文字を排除
    import re
    # 全角文字（ひらがな、カタカナ、漢字など）を除去
    cleaned_text = re.sub(r'[^\x00-\x7F\s]', '', normalized)
    # 空白削除
    cleaned_text = re.sub(r'\s', '', cleaned_text)
    # 数字判定
    if not cleaned_text or not re.match(r'^\d+$', cleaned_text):
        return False
    # 50より大きい値の場合のみ表示
    try:
        session_number = int(cleaned_text)
        if session_number > 50:
            print(f"判定成功（50超）: '{session_text}' -> 正規化後: '{normalized}' -> 全角排除後: '{cleaned_text}' -> 数値: {session_number}")
    except ValueError:
        pass
    return True

def is_regular_session_list(schedule_data: list) -> bool:
    """スケジュールリスト全体が正規かどうかを判定する
    
    Args:
        schedule_data (list): スケジュールデータのリスト
        
    Returns:
        bool: リスト全体が正規の場合True、1件でも不規則がある場合または重複がある場合はFalse
        
    Note:
        ドキュメントの分類ルールに従い、リスト内に1件でも不規則なレコードがある場合は
        全体を不規則として扱う。また、正規化後に重複が1件でもある場合も不規則として扱う。
    """
    if not schedule_data:
        return True
    
    # 正規化後のセッション番号を格納するリスト
    normalized_sessions = []
    
    # リスト内の各セッションをチェック
    for session_data in schedule_data:
        if not isinstance(session_data, dict):
            continue
        
        session = session_data.get("session", "")
        if not session:
            continue
        
        # 1件でも不規則なセッションがあれば、リスト全体を不規則として扱う
        if not is_regular_session(session):
            return False
        
        # 正規セッションの場合、正規化後の番号を取得
        session_number = extract_session_number(session)
        if session_number > 0:
            normalized_sessions.append(session_number)
    
    # 重複チェック
    if len(normalized_sessions) != len(set(normalized_sessions)):
        return False
    
    return True

def extract_session_number(session_text: str) -> int:
    """正規セッションから回数を抽出する"""
    if not session_text:
        return 0
    # 部、月の混入判定
    if '部' in session_text or '月' in session_text:
        return 0
    # 正規化
    normalized = normalize_subject_name(session_text)
    # 全角文字を排除
    import re
    # 全角文字（ひらがな、カタカナ、漢字など）を除去
    cleaned_text = re.sub(r'[^\x00-\x7F\s]', '', normalized)
    # 空白削除
    cleaned_text = re.sub(r'\s', '', cleaned_text)
    # 数字判定
    if not cleaned_text or not re.match(r'^\d+$', cleaned_text):
        return 0
    try:
        session_number = int(cleaned_text)
        # 50より大きい値の場合のみ表示
        if session_number > 50:
            print(f"抽出成功（50超）: '{session_text}' -> 正規化後: '{normalized}' -> 全角排除後: '{cleaned_text}' -> 数値: {session_number}")
        return session_number if session_number > 0 else 0
    except ValueError:
        print(f"抽出失敗（数値変換エラー）: '{session_text}' -> 正規化後: '{normalized}' -> 全角排除後: '{cleaned_text}'")
        return 0

def process_session_data(session_text: str) -> Tuple[bool, int, str]:
    """セッション文字列を処理して正規性、回数、パターンを返す
    
    Args:
        session_text (str): セッション文字列
        
    Returns:
        Tuple[bool, int, str]: (正規かどうか, 回数, セッションパターン)
            - 正規の場合: (True, 回数, "")
            - 不規則の場合: (False, 0, 元の文字列)
    """
    if not session_text:
        return False, 0, ""
    
    if is_regular_session(session_text):
        session_number = extract_session_number(session_text)
        return True, session_number, ""
    else:
        return False, 0, session_text 