<!--
更新時の注意事項:
- 準拠とは、類推せずに内容に従うこと
- 更新は docs/doc.md に準拠すること
-->

# ユーティリティ関数ガイドライン

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

def get_subject_name_id_from_db(name: str) -> int:
    """データベースから科目名IDを取得する"""
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
from utils import get_subject_name_id_from_db

try:
    subject_id = get_subject_name_id_from_db("存在しない科目名")
except ValueError as e:
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

### 使用例
```python
from utils import get_year_from_user

# 年度の取得
year = get_year_from_user()
print(f"処理対象年度: {year}")
```

## 更新履歴

| 日付 | バージョン | 更新者 | 内容 |
|------|------------|--------|------|
| 2024-03-20 | 1.0.0 | 開発者名 | 初版作成 |

[🔝 ページトップへ](#ユーティリティ関数ガイドライン) 