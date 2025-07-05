---
title: パーサー一覧
file_version: v2.6.0
project_version: v2.6.0
last_updated: 2025-07-05
---

<!--
更新時の注意事項:
- 準拠とは、類推せずに内容に従うこと
- 更新は docs/doc.md に準拠すること
-->

# パーサー一覧

- File Version: v2.6.0
- Project Version: v2.6.0
- Last Updated: 2025-07-05

[readmeへ](../../README.md)

## 目次
1. [概要](#概要)
2. [パーサー一覧](#パーサー一覧)
3. [実行方法](#実行方法)
4. [基本方針](#基本方針)

## 概要

このドキュメントでは、シラバスデータベースの構築に使用される各パーサーの役割と処理内容について説明します。
各パーサーは特定のデータソースから情報を抽出し、データベースに格納するための処理を行います。

## パーサー一覧

> **注意:** `src/course_guide/{year}/csv/*.csv` のデータソースは**タブ区切り**です。

| パーサー名 | ファイル名 | 処理内容 | データソース | 対応テーブル |
|------------|------------|----------|--------------|--------------|
| 科目区分パーサー | 01_class.py | 科目区分の抽出 | `src/course_guide/{year}/csv/*.csv`（タブ区切り） | class |
| 科目小区分パーサー | 02_subclass.py | 科目小区分の抽出 | `src/course_guide/{year}/csv/*.csv`（タブ区切り） | subclass |
| 学部パーサー | 03_faculty.py | 学部情報の抽出 | `src/course_guide/{year}/csv/*.csv`（タブ区切り） | faculty |
| 科目名パーサー | 04_subject_name.py | 科目名の抽出 | `src/syllabus/{year}/json/*.json` | subject_name |
| 教員パーサー | 05_instructor.py | 教員情報の抽出 | `src/syllabus/{year}/json/*.json` | instructor |
| シラバスマスターパーサー | 06_syllabus_master.py | シラバスマスター情報の抽出 | `src/syllabus/{year}/json/*.json` | syllabus_master |
| 書籍パーサー | 07_book.py | 書籍情報の抽出 | `src/syllabus/{year}/json/*.json` | book, book_uncategorized |
| シラバスパーサー | 09_syllabus.py | シラバス詳細情報の抽出 | `src/syllabus/{year}/json/*.json` | syllabus |
| 科目履修可能学年パーサー | 10_subject_grade.py | 履修可能学年の抽出 | `src/syllabus/{year}/json/*.json` | subject_grade |
| 講義時間パーサー | 11_lecture_time.py | 講義時間情報の抽出 | `src/syllabus/{year}/json/*.json` | lecture_time |
| 講義セッションパーサー | 12_lecture_session.py | 講義セッション情報の抽出 | `src/syllabus/{year}/json/*.json` | lecture_session |
| 科目属性パーサー | 16_subject_attribute.py | 科目属性の抽出 | `src/course_guide/{year}/csv/*.csv`（タブ区切り） | subject_attribute |
| 科目パーサー | 17_subject.py | 科目情報の統合 | `src/course_guide/{year}/csv/*.csv`（タブ区切り） | subject |
| 科目属性値パーサー | 19_subject_attribute_value.py | 科目属性値の抽出 | `src/course_guide/{year}/csv/*.csv`（タブ区切り） | subject_attribute_value |
| シラバス学習システムパーサー | 21_syllabus_study_system.py | シラバス系統的履修の抽出 | `src/syllabus/{year}/json/*.json` | syllabus_study_system |
| シラバス学部関連パーサー | 22_syllabus_faculty.py | シラバス学部関連の抽出 | `src/syllabus/{year}/json/*.json` | syllabus_faculty |

### 未実装パーサー（structure.md準拠）

以下のパーサーは`structure.md`で定義されているが、まだ実装されていません：

| パーサー名 | ファイル名 | 処理内容 | データソース | 対応テーブル |
|------------|------------|----------|--------------|--------------|
| シラバス教員関連パーサー | 13_syllabus_instructor.py | シラバス教員関連の抽出 | `src/syllabus/{year}/json/*.json` | syllabus_instructor |
| 講義セッション教員パーサー | 14_lecture_session_instructor.py | 講義セッション教員の抽出 | `src/syllabus/{year}/json/*.json` | lecture_session_instructor |
| シラバス教科書関連パーサー | 15_syllabus_book.py | シラバス教科書関連の抽出 | `src/syllabus/{year}/json/*.json` | syllabus_book |
| 成績評価基準パーサー | 18_grading_criterion.py | 成績評価基準の抽出 | `src/syllabus/{year}/json/*.json` | grading_criterion |

### 削除されたパーサー

以下のパーサーは`structure.md`の変更により削除されました：

| パーサー名 | ファイル名 | 削除理由 |
|------------|------------|----------|
| 科目シラバス関連パーサー | 20_subject_syllabus.py | `subject_syllabus`テーブルが削除されたため |

## 実行方法

パーサーは以下のコマンドで実行できます：

```bash
./syllabus.sh parser [パーサー名または番号]
```

例：
```bash
./syllabus.sh parser 01  # 科目区分パーサーを実行
./syllabus.sh parser class  # 科目区分パーサーを実行
./syllabus.sh parser 21  # シラバス学習システムパーサーを実行
```

## 基本方針

### tqdmメッセージ表示の基本方針

#### 1. 処理開始時のメッセージ
```python
tqdm.write(f"\n{'='*60}")
tqdm.write(f"処理名 - 対象年度: {year}")
tqdm.write(f"{'='*60}")
```

#### 2. ファイル処理の進捗表示
```python
# ファイル処理の進捗バー
for json_file in tqdm(json_files, desc="ファイル処理中", unit="file"):
    # 処理内容
    pass
```

#### 3. 詳細処理の進捗表示
```python
# 詳細処理の進捗バー（leave=Falseで親バーの下に表示）
for item in tqdm(items, desc=f"詳細処理中 ({identifier})", leave=False):
    # 処理内容
    pass
```

#### 4. 統計情報の表示
処理完了時に以下の形式で統計情報を表示します：

```python
# 最終統計の表示
tqdm.write("\n" + "="*60)
tqdm.write("処理完了 - 統計情報")
tqdm.write("="*60)
tqdm.write(f"総ファイル数: {stats['total_files']}")
tqdm.write(f"処理済みファイル数: {stats['processed_files']}")
tqdm.write(f"総データ数: {stats['total_items']}")
tqdm.write(f"正常データ数: {stats['valid_items']}")
tqdm.write(f"エラーデータ数: {stats['error_items']}")
tqdm.write("="*60)
```

#### 5. 結果サマリーの表示
```python
tqdm.write(f"\n{'='*60}")
tqdm.write("📊 抽出結果サマリー")
tqdm.write(f"{'='*60}")
tqdm.write(f"✅ 正常データ: {len(valid_data)}件")
tqdm.write(f"⚠️  エラーデータ: {len(error_data)}件")
tqdm.write(f"📈 合計: {len(valid_data) + len(error_data)}件")
```

#### 6. エラーメッセージの表示
```python
# 重要なエラーは表示、軽微なエラーはコメントアウト
tqdm.write(f"エラー: {error_message}")  # 重要なエラー
# tqdm.write(f"警告: {warning_message}")  # 軽微なエラー（コメントアウト）
```

### データベースアクセスの基本方針

#### syllabus_masterへの問い合わせ
syllabus_masterテーブルへの問い合わせは、必ず`utils.md`で定義された関数を使用します：

```python
from .utils import get_syllabus_master_id_from_db

# シラバスマスターIDの取得
try:
    syllabus_id = get_syllabus_master_id_from_db(session, syllabus_code, year)
    if not syllabus_id:
        tqdm.write(f"syllabus_masterに対応するレコードがありません（科目コード: {syllabus_code}, 年度: {year}）")
        continue
except Exception as e:
    tqdm.write(f"致命的なDB接続エラー: {e}")
    raise
```

#### データベース接続
データベース接続も`utils.md`の関数を使用します：

```python
from .utils import get_db_connection

# データベース接続
session = get_db_connection()
try:
    # 処理内容
    pass
finally:
    session.close()
```

### 統計情報の管理

各パーサーでは以下の統計情報を管理します：

```python
stats = {
    'total_files': 0,      # 総ファイル数
    'processed_files': 0,  # 処理済みファイル数
    'total_items': 0,      # 総データ数
    'valid_items': 0,      # 正常データ数
    'error_items': 0,      # エラーデータ数
    'specific_errors': {}  # 特定のエラー種別ごとのカウント
}
```

### エラーハンドリング

- 致命的なエラー：例外を再送出して処理を停止
- 軽微なエラー：統計に記録して処理を継続
- デバッグメッセージ：必要最小限に抑制（コメントアウト）

### エラーレポート機能

最新のパーサーでは、エラー詳細をCSVファイルに出力する機能が追加されています：

```python
def create_warning_csv(year: int, errors: List[Dict]) -> str:
    """エラー内容を詳細にCSVファイルに記載する"""
    # 警告ディレクトリを作成
    warning_dir = os.path.join("warning", str(year))
    os.makedirs(warning_dir, exist_ok=True)
    
    # CSVファイルにエラー情報を書き込み
    # ファイル名、行番号、エラータイプ、エラー詳細などを含む
```

[🔝 ページトップへ](#パーサー一覧) 