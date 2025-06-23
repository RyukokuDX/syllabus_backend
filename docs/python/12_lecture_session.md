---
title: 講義セッション情報抽出処理
file_version: v1.3.1
project_version: v1.3.31
last_updated: 2025-06-23
---

# 講義セッション情報抽出処理

- File Version: v1.3.1
- Project Version: v1.3.31
- Last Updated: 2025-06-23

[readmeへ](../README.md) | [docへ](./doc.md)

## 目次
1. [概要](#概要)
2. [処理フロー](#処理フロー)
3. [データ構造](#データ構造)
4. [講義セッション解析ロジック](#講義セッション解析ロジック)
5. [出力ファイル](#出力ファイル)
6. [エラー処理](#エラー処理)
7. [使用例](#使用例)

## 概要

### 目的
Web Syllabusから取得したJSONファイルから講義セッション情報を抽出し、通常の講義セッションと不規則な講義セッションに分類して保存する。

### 対象データ
- **入力**: `src/syllabus/{year}/json/` ディレクトリ内のJSONファイル
- **出力**: 
  - 通常の講義セッション: `updates/lecture_session/add/`
  - 不規則な講義セッション: `updates/lecture_session_irregular/add/`
  - エラー情報: `warning/{year}/`

### 処理対象
- 講義計画のスケジュール情報
- 各講義回数の内容と担当者情報

## 処理フロー

### 1. 初期化処理
```python
# 年度の取得
year = get_year_from_user()

# JSONファイル一覧の取得
json_files = get_json_files(year)

# データベース接続
session = get_db_connection()

# 出力ファイルの準備
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
```

### 2. ストリーミング処理
```python
# ファイルを開いて逐次書き込み
with open(lecture_session_file, 'w') as lecture_f:
    with open(lecture_session_irregular_file, 'w') as irregular_f:
        for json_file in json_files:
            # 各JSONファイルを処理
            # 結果を即座にファイルに書き込み
```

### 3. データ抽出処理
```python
# JSONファイルからデータを抽出
json_data = json.load(f)

# シラバスマスターIDを取得
syllabus_master_id = get_syllabus_master_id_from_db(session, syllabus_code, year)

# 講義セッションを解析
lecture_sessions, lecture_sessions_irregular = parse_lecture_sessions_from_schedule(schedule_data)
```

## データ構造

### 入力JSON構造
```json
{
  "科目コード": "CS101",
  "講義計画": {
    "内容": {
      "schedule": [
        {
          "session": "1-1",
          "content": "講義内容",
          "instructor": "担当者名"
        }
      ]
    }
  }
}
```

### 出力データ構造

#### 通常の講義セッション
```json
{
  "syllabus_id": 123,
  "session_number": 1,
  "contents": "講義内容",
  "other_info": null
}
```

#### 不規則な講義セッション
```json
{
  "syllabus_id": 123,
  "session_pattern": "I-1",
  "contents": "講義内容",
  "other_info": null
}
```

## 講義セッション解析ロジック

### 1. 文字列正規化
```python
# 全角文字を半角に変換
session_normalized = normalize_subject_name(session)
session_halfwidth = unicodedata.normalize('NFKC', session_normalized)
```

### 2. 分類ルール

#### 不規則として扱う場合
正規化後、以下で分類
- 「部,月」が含まれる文字列
- 全角文字を削除後に数字にならない文字列(例: 1-1)
- リスト内に、１件でも不規則なレコードがある場合

#### 通常として扱う場合
正規化後
- 「部,月」が含んでいない
- 全角文字を取り除いて、数字になる


### 3. 重複チェック
```python
# 重複チェック用のセット
seen_sessions = set()

# 重複を防いでセッションを追加
if session_number not in seen_sessions:
    lecture_sessions.append(session_data)
    seen_sessions.add(session_number)
```

### 4. 範囲処理
```python
# ハイフン区切りの場合
if len(session_parts) >= 2:
    start_session = int(session_parts[0])
    end_session = int(session_parts[1])
    
    # 範囲内の各セッションを生成
    for session_number in range(start_session, end_session + 1):
        if session_number not in seen_sessions:
            lecture_sessions.append(session_data)
            seen_sessions.add(session_number)
```

## 出力ファイル

### ファイル名規則
- **通常セッション**: `lecture_session_{timestamp}.json`
- **不規則セッション**: `lecture_session_irregular_{timestamp}.json`
- **エラー情報**: `lecture_session_{timestamp}.csv`

### ファイル構造
```json
[
  {
    "syllabus_id": 123,
    "session_number": 1,
    "contents": "講義内容",
    "other_info": null
  },
  {
    "syllabus_id": 123,
    "session_number": 2,
    "contents": "講義内容",
    "other_info": null
  }
]
```

## エラー処理

### エラーの種類
1. **ファイル読み込みエラー**: JSONファイルの読み込み失敗
2. **データベースエラー**: シラバスマスターID取得失敗
3. **データ抽出エラー**: 講義セッション解析失敗

### エラー出力
```csv
エラータイプ,エラー内容
処理エラー,科目コードが見つかりません: file.json
処理エラー,シラバスマスターIDが見つかりません: CS101 (2025)
```

## 使用例

### 実行方法
```bash
cd src/db/parser
python 12_lecture_session.py
```

## 注意事項

### メモリ使用量
- ストリーミング処理により、メモリ使用量を最小限に抑制
- 大量データでも安定して処理可能

### 重複防止
- 同じセッション番号の重複生成を防止
- 異常に大きな範囲指定は不規則として扱う

### データ整合性
- シラバスマスターIDとの関連を保持
- 外部キー制約に準拠したデータ構造

## 関連ファイル

- **入力**: `src/syllabus/{year}/json/*.json`
- **出力**: 
  - `updates/lecture_session/add/lecture_session_*.json`
  - `updates/lecture_session_irregular/add/lecture_session_irregular_*.json`
  - `warning/{year}/lecture_session_*.csv`
- **設定**: `src/db/parser/12_lecture_session.py`

[🔝 ページトップへ](#講義セッション情報抽出処理) 