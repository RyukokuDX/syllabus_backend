from datetime import datetime
import unicodedata

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