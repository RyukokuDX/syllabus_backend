---
title: ユーティリティ関数ガイドライン
file_version: v2.5.1
project_version: v2.5.1
last_updated: 2025-07-04
---

<!--
更新時の注意事項:
- 準拠とは、類推せずに内容に従うこと
- 更新は docs/doc.md に準拠すること
-->

# ユーティリティ関数ガイドライン

- File Version: v2.5.1
- Project Version: v2.5.1
- Last Updated: 2025-07-04

[readmeへ](../README.md) | [docへ](./doc.md)

## 目次
1. [基本方針](#基本方針)
2. [関数の命名規則](#関数の命名規則)
3. [引数と戻り値](#引数と戻り値)
4. [エラー処理](#エラー処理)
5. [ドキュメンテーション](#ドキュメンテーション)
6. [テスト](#テスト)
7. [使用例](#使用例)
8. [共通機能](#共通機能)

## 基本方針

### 目的
- 再利用可能な共通機能を提供すること
- コードの重複を避けること
- 一貫性のある実装を維持すること

### 文字の正規化方針
- 平仮名と片仮名以外の文字で全角と半角が存在する場合は、半角を採用
  - アルファベット：全角（ＡＢＣ）→半角（ABC）
  - 数字：全角（１２３）→半角（123）
  - 記号：全角（（））→半角（()）
  - スペース：全角（　）→半角（ ）
  - ハイフン類：全角（－）→半角（-）
  - ローマ数字：全角（Ⅰ Ⅱ Ⅲ）→半角（I II III）
  - 中点：全角（・）→半角（·）
- 平仮名と片仮名は全角のまま維持
- 連続するスペースは1つに統一

### 対象読者
- プロジェクトの開発者
- コードレビュアー
- 将来のメンテナ

## 関数の命名規則

### 命名規則
- スネークケースを使用（例：`normalize_subject_name`）
- 動詞から始める（例：`get_`, `set_`, `create_`）
- 目的を明確に示す（例：`parse_csv_data`）

### 命名例
```python
def normalize_subject_name(name: str) -> str:
    """科目名を正規化する"""
    pass

def get_syllabus_master_id_from_db(session, syllabus_code: str, year: int) -> int:
    """データベースからシラバスマスターIDを取得する"""
    pass
```

## 引数と戻り値

### 型ヒント
- すべての引数と戻り値に型ヒントを付ける
- 複雑な型は`typing`モジュールを使用

### 引数の順序
1. 必須パラメータ
2. オプショナルパラメータ
3. キーワード引数

例：
```python
def process_data(
    required_param: str,
    optional_param: int = 0,
    *,
    keyword_param: bool = True
) -> Dict[str, Any]:
    pass
```

## エラー処理

### 例外の使用
- 適切な例外クラスを使用
- カスタム例外は`exceptions.py`で定義

### エラーメッセージ
- 具体的で分かりやすいメッセージ
- エラーの原因と対処方法を含める

例：
```python
def validate_input(data: str) -> None:
    if not data:
        raise ValueError("入力データが空です")
    if len(data) > 100:
        raise ValueError("入力データが長すぎます（最大100文字）")
```

## ドキュメンテーション

### 関数のドキュメント
```python
def function_name(param1: type, param2: type) -> return_type:
    """関数の概要

    Args:
        param1 (type): パラメータ1の説明
        param2 (type): パラメータ2の説明

    Returns:
        return_type: 戻り値の説明

    Raises:
        ExceptionType: 例外が発生する条件の説明
    """
    pass
```

### モジュールのドキュメント
```python
"""
モジュールの概要

このモジュールは以下の機能を提供します：
- 機能1の説明
- 機能2の説明

使用例：
    >>> from utils import function_name
    >>> result = function_name(param1, param2)
"""
```

## テスト

### テストの要件
- 単体テストを必ず作成
- エッジケースをカバー
- モックを使用して外部依存を分離

### テストの構造
```python
def test_function_name():
    """テストの目的"""
    # 準備
    input_data = "test"
    expected = "expected"
    
    # 実行
    result = function_name(input_data)
    
    # 検証
    assert result == expected
```

## 使用例

### 基本的な使用例
```python
from utils import normalize_subject_name

# 科目名の正規化
name = " データベース基礎Ⅰ "
normalized = normalize_subject_name(name)
print(normalized)  # "データベース基礎I"
```

### エラー処理の例
```python
from utils import get_syllabus_master_id_from_db

try:
    syllabus_id = get_syllabus_master_id_from_db(session, "CS101", 2024)
except Exception as e:
    print(f"エラー: {e}")
```

## 共通機能

### 年度の取得と検証
年度の取得と検証は、以下の関数を使用します：

```python
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
```

### データベース接続
データベース接続は、以下の関数を使用します：

```python
def get_db_connection():
    """データベース接続を取得する
    
    Returns:
        Session: SQLAlchemyセッションオブジェクト
        
    Note:
        環境変数から接続情報を取得し、UTF-8エンコーディングを設定します
    """
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
```

### シラバスマスターID取得
シラバスマスターIDの取得は、以下の関数を使用します：

```python
def get_syllabus_master_id_from_db(session, syllabus_code: str, year: int) -> int:
    """データベースからシラバスマスターIDを取得する
    
    Args:
        session: SQLAlchemyセッション
        syllabus_code (str): シラバスコード
        year (int): 年度
        
    Returns:
        int: シラバスマスターID（見つからない場合はNone）
        
    Raises:
        Exception: データベース接続エラー時
    """
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
```

### 講義回数の正規判定
講義回数の正規判定は、以下の関数を使用します：

```python
def is_regular_session(session_text: str) -> bool:
    """講義セッションが正規かどうかを判定する
    
    Args:
        session_text (str): 講義セッション文字列
        
    Returns:
        bool: 正規の場合True、不規則の場合False
        
    Note:
        以下の処理を順次実行して判定します：
        1. 正規化（全角→半角変換など）
        2. 講義形式の括弧を削除（(オンライン)、(ハイブリット)）
        3. Lを削除
        4. 全角文字を排除
        5. 空白削除
        6. 先頭の0を削除
        7. 数字判定
    """
    if not session_text:
        return False
    # 部、月の混入判定
    if '部' in session_text or '月' in session_text:
        return False
    # 正規化
    normalized = normalize_subject_name(session_text)
    
    # 講義形式の括弧を削除
    import re
    normalized = re.sub(r'\(オンライン\)', '', normalized)
    normalized = re.sub(r'\(ハイブリット\)', '', normalized)
    
    # Lを削除
    normalized = normalized.replace('L', '')
    
    # 全角文字を排除
    cleaned_text = re.sub(r'[^\x00-\x7F\s]', '', normalized)
    # 空白削除
    cleaned_text = re.sub(r'\s', '', cleaned_text)
    # 先頭の0を削除
    cleaned_text = cleaned_text.lstrip('0')
    # 数字判定
    if not cleaned_text or not re.match(r'^\d+$', cleaned_text):
        return False
    return True

def extract_session_number(session_text: str) -> int:
    """正規セッションから回数を抽出する
    
    Args:
        session_text (str): 講義セッション文字列
        
    Returns:
        int: 抽出された回数（抽出できない場合は0）
        
    Note:
        is_regular_sessionと同じ前処理を実行してから回数を抽出します
    """
    if not session_text:
        return 0
    # 部、月の混入判定
    if '部' in session_text or '月' in session_text:
        return 0
    # 正規化
    normalized = normalize_subject_name(session_text)
    
    # 講義形式の括弧を削除
    import re
    normalized = re.sub(r'\(オンライン\)', '', normalized)
    normalized = re.sub(r'\(ハイブリット\)', '', normalized)
    
    # Lを削除
    normalized = normalized.replace('L', '')
    
    # 全角文字を排除
    cleaned_text = re.sub(r'[^\x00-\x7F\s]', '', normalized)
    # 空白削除
    cleaned_text = re.sub(r'\s', '', cleaned_text)
    # 先頭の0を削除
    cleaned_text = cleaned_text.lstrip('0')
    # 数字判定
    if not cleaned_text or not re.match(r'^\d+$', cleaned_text):
        return 0
    try:
        session_number = int(cleaned_text)
        return session_number if session_number > 0 else 0
    except ValueError:
        return 0

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

### 使用例
```python
from utils import get_year_from_user, get_db_connection, get_syllabus_master_id_from_db

# 年度の取得
year = get_year_from_user()
print(f"処理対象年度: {year}")

# データベース接続
session = get_db_connection()

# シラバスマスターIDの取得
try:
    syllabus_id = get_syllabus_master_id_from_db(session, "CS101", year)
    if syllabus_id:
        print(f"シラバスID: {syllabus_id}")
    else:
        print("シラバスが見つかりませんでした")
except Exception as e:
    print(f"エラー: {e}")
finally:
    session.close()

# 講義回数の正規判定
session_texts = ["L1(オンライン)", "L02(ハイブリット)", "L15", "1回目", "部1"]
for text in session_texts:
    is_regular = is_regular_session(text)
    session_number = extract_session_number(text)
    print(f"'{text}' -> 正規: {is_regular}, 回数: {session_number}")

# スケジュールリストの正規判定
schedule_data = [
    {"session": "L1(オンライン)", "content": "導入"},
    {"session": "L2(ハイブリット)", "content": "基礎"},
    {"session": "L3", "content": "応用"}
]
is_regular_list = is_regular_session_list(schedule_data)
print(f"スケジュールリスト正規: {is_regular_list}")
```


[🔝 ページトップへ](#ユーティリティ関数ガイドライン) 