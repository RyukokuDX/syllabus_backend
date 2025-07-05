#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# File Version: v2.6.0
# Project Version: v2.6.0
# Last Updated: 2025-07-05
"""

import os
import json
import glob
import csv
import re
import requests
import time
from typing import List, Dict, Set, Tuple, Any, Optional
from datetime import datetime
from tqdm import tqdm
from .utils import get_year_from_user, get_db_connection, get_syllabus_master_id_from_db
from pathlib import Path
from sqlalchemy import text

# レーベンシュタイン距離の計算用ライブラリ
try:
	import Levenshtein
except ImportError:
	# Levenshteinライブラリが利用できない場合の代替実装
	def levenshtein_distance(s1, s2):
		if len(s1) < len(s2):
			return levenshtein_distance(s2, s1)
		if len(s2) == 0:
			return len(s1)
		previous_row = list(range(len(s2) + 1))
		for i, c1 in enumerate(s1):
			current_row = [i + 1]
			for j, c2 in enumerate(s2):
				insertions = previous_row[j + 1] + 1
				deletions = current_row[j] + 1
				substitutions = previous_row[j] + (c1 != c2)
				current_row.append(min(insertions, deletions, substitutions))
			previous_row = current_row
		return previous_row[-1]
	class Levenshtein:
		@staticmethod
		def distance(s1, s2):
			return levenshtein_distance(s1, s2)

def validate_isbn(isbn: str) -> bool:
    """ISBNのチェックディジットを検証する"""
    if not isbn:
        return False
    # 数字以外の文字を除去（Xは除く）
    cleaned_isbn = ''.join(c for c in isbn if c.isdigit() or c.upper() == 'X')
    # ISBN-10の場合
    if len(cleaned_isbn) == 10:
        total = 0
        for i in range(9):
            total += int(cleaned_isbn[i]) * (10 - i)
        check_digit = (11 - (total % 11)) % 11
        # チェックデジットが10の場合は'X'
        expected_check = 'X' if check_digit == 10 else str(check_digit)
        actual_check = cleaned_isbn[9].upper()
        is_valid = expected_check.upper() == actual_check
        if not is_valid:
            tqdm.write(f"ISBN-10 チェックディジット違反: {isbn} -> 期待値: {expected_check}, 実際: {actual_check}")
        return is_valid
    # ISBN-13の場合
    elif len(cleaned_isbn) == 13:
        total = 0
        for i in range(12):
            weight = 1 if i % 2 == 0 else 3
            total += int(cleaned_isbn[i]) * weight
        check_digit = (10 - (total % 10)) % 10
        expected_check = str(check_digit)
        actual_check = cleaned_isbn[12]
        is_valid = expected_check == actual_check
        if not is_valid:
            tqdm.write(f"ISBN-13 チェックディジット違反: {isbn} -> 期待値: {expected_check}, 実際: {actual_check}")
        return is_valid
    return False

def calculate_similarity(str1: str, str2: str) -> float:
    """
    書籍名の類似度を計算する関数
    
    Args:
        str1 (str): 比較対象の書籍名1
        str2 (str): 比較対象の書籍名2
    
    Returns:
        float: 0.0から1.0の間の類似度（1.0が完全一致）
    """
    if not str1 or not str2:
        return 0.0
    
    # 前処理
    def preprocess(title: str) -> str:
        # 小文字化
        title = title.lower()
        # 記号を空白に置換
        title = re.sub(r'[^\w\s]', ' ', title)
        # 連続する空白を1つに
        title = re.sub(r'\s+', ' ', title)
        # 前後の空白を削除
        return title.strip()
    
    # 前処理を適用
    title1 = preprocess(str1)
    title2 = preprocess(str2)
    
    # 完全一致の場合は1.0を返す
    if title1 == title2:
        return 1.0
    
    # レーベンシュタイン距離を計算
    distance = Levenshtein.distance(title1, title2)
    max_len = max(len(title1), len(title2))
    
    # 文字列の類似度を計算（距離が大きいほど類似度は低くなる）
    string_similarity = 1.0 - (distance / max_len)
    
    # シリーズ名などの影響を軽減するため、単語単位での比較も行う
    words1 = set(title1.split())
    words2 = set(title2.split())
    
    # 共通する単語の割合を計算
    if len(words1) == 0 and len(words2) == 0:
        word_similarity = 1.0
    else:
        common_words = words1.intersection(words2)
        word_similarity = len(common_words) / max(len(words1), len(words2))
    
    # 文字列の類似度と単語の類似度を組み合わせる
    # 重み付けは0.7:0.3（仕様書に準拠）
    return 0.7 * string_similarity + 0.3 * word_similarity

def get_book_info(year: int) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """書籍情報を取得する（正常・未分類の2リストを返す）"""
    books = []  # 正常な書籍
    books_uncategorized = []  # 未分類書籍
    # ISBN重複回避のためのセット
    processed_isbns = set()
    
    # 統計情報
    stats = {
        'total_files': 0,
        'processed_files': 0,
        'total_books': 0,
        'valid_books': 0,
        'uncategorized_books': 0,
        'duplicate_isbns': 0,
        'invalid_isbns': 0,
        'cinii_failures': 0
    }
    
    # データベース接続
    session = get_db_connection()
    
    try:
        # シラバスから書籍情報を取得
        script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        json_pattern = os.path.join(script_dir, 'syllabus', str(year), 'json', '*.json')
        
        json_files = glob.glob(json_pattern)
        stats['total_files'] = len(json_files)
        
        tqdm.write(f"処理開始: {stats['total_files']}個のJSONファイルを処理します")
        
        for json_file in tqdm(json_files, desc="シラバスファイル処理中", unit="file"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if '詳細情報' not in data:
                    continue
                    
                detail = data['詳細情報']
                syllabus_code = data.get('科目コード', '')
                
                # 基本情報から年度を取得（09_syllabus.pyを参考）
                basic_info = data.get("基本情報", {})
                syllabus_year = int(basic_info.get("開講年度", {}).get("内容", str(year)))
                
                # syllabus_masterからsyllabus_idを取得
                try:
                    syllabus_id = get_syllabus_master_id_from_db(session, syllabus_code, syllabus_year)
                    if not syllabus_id:
                        tqdm.write(f"syllabus_masterに対応するレコードがありません（科目コード: {syllabus_code}, 年度: {syllabus_year}）")
                        continue
                except Exception as e:
                    tqdm.write(f"致命的なDB接続エラー: {e}")
                    raise
                
                stats['processed_files'] += 1
                
                # 書籍情報処理関数
                def process_books(books_list, role_type):
                    """書籍リストを処理する共通関数"""
                    if isinstance(books_list, list) and books_list:  # nullでない場合のみ処理
                        stats['total_books'] += len(books_list)
                        
                        # 書籍処理の進捗を表示
                        for book in tqdm(books_list, desc=f"{role_type}処理中 ({syllabus_code})", leave=False):
                                isbn = book.get('ISBN', '').strip()
                                title = book.get('書籍名', '').strip()
                                # 著者名を正規化
                                author = normalize_author(book.get('著者', ''))
                                publisher = book.get('出版社', '').strip()
                                price = None
                                price_str = book.get('価格', '')
                                if price_str and price_str.strip():
                                    try:
                                        price = int(price_str.replace(',', '').replace('円', ''))
                                    except ValueError:
                                        pass
                                role = role_type
                                now = datetime.now().isoformat()
                                
                                # ISBNがnullの場合
                                if not isbn:
                                    books_uncategorized.append({
                                        'syllabus_id': syllabus_id,
                                        'title': title,
                                        'author': author,
                                        'publisher': publisher,
                                        'price': price,
                                        'role': role,
                                        'isbn': None,
                                        'categorization_status': 'ISBNなし',
                                        'created_at': now,
                                        'updated_at': now
                                    })
                                    stats['uncategorized_books'] += 1
                                    continue
                                
                                # ISBN重複チェック（正規のISBNのみ）
                                if validate_isbn(isbn) and isbn in processed_isbns:
                                    # tqdm.write(f"重複ISBNをスキップ: {isbn}")
                                    stats['duplicate_isbns'] += 1
                                    continue
                                
                                # ISBNが存在する場合の処理
                                if not validate_isbn(isbn):
                                    # 数字以外の文字を除去した後の長さでチェック
                                    cleaned_isbn = ''.join(c for c in isbn if c.isdigit() or c.upper() == 'X')
                                    if len(cleaned_isbn) != 10 and len(cleaned_isbn) != 13:
                                        books_uncategorized.append({
                                            'syllabus_id': syllabus_id,
                                            'title': title,
                                            'author': author,
                                            'publisher': publisher,
                                            'price': price,
                                            'role': role,
                                            'isbn': isbn,
                                            'categorization_status': '不正ISBN: 桁数違反',
                                            'created_at': now,
                                            'updated_at': now
                                        })
                                    else:
                                        books_uncategorized.append({
                                            'syllabus_id': syllabus_id,
                                            'title': title,
                                            'author': author,
                                            'publisher': publisher,
                                            'price': price,
                                            'role': role,
                                            'isbn': isbn,
                                            'categorization_status': '不正ISBN: cd違反',
                                            'created_at': now,
                                            'updated_at': now
                                        })
                                    stats['invalid_isbns'] += 1
                                    stats['uncategorized_books'] += 1
                                    continue
                                
                                # ISBNが正常な場合の処理（テキストと同様）
                                # シラバスから価格情報を取得（既に取得済みの場合は再取得しない）
                                if price is None:
                                    price_str = book.get('価格', '')
                                    if price_str and price_str.strip():
                                        try:
                                            price = int(price_str.replace(',', '').replace('円', ''))
                                        except ValueError:
                                            pass
                                
                                # シラバスから書籍名を取得（類似度比較用）
                                syllabus_title = book.get('書籍名', '').strip()
                                
                                # src/books/json/{ISBN}.jsonの存在確認
                                book_json_path = Path(f"src/books/json/{isbn}.json")
                                if not book_json_path.exists():
                                    # 既存JSONファイルが存在しない場合はCiNiiから取得
                                    try:
                                        cinii_data = get_cinii_data(isbn)
                                        if not cinii_data:
                                            # tqdm.write(f"CiNiiから取得失敗: {isbn}")
                                            books_uncategorized.append({
                                                'syllabus_id': syllabus_id,
                                                'title': title,
                                                'author': author,
                                                'publisher': publisher,
                                                'price': price,
                                                'role': role,
                                                'isbn': isbn,
                                                'categorization_status': '問題ISBN: ciniiデータ不在',
                                                'created_at': now,
                                                'updated_at': now
                                            })
                                            continue
                                    except Exception as e:
                                        # tqdm.write(f"CiNii取得中にエラー: {isbn} - {str(e)}")
                                        books_uncategorized.append({
                                            'syllabus_id': syllabus_id,
                                            'title': title,
                                            'author': author,
                                            'publisher': publisher,
                                            'price': price,
                                            'role': role,
                                            'isbn': isbn,
                                            'categorization_status': '問題ISBN: ciniiデータ不在',
                                            'created_at': now,
                                            'updated_at': now
                                        })
                                        continue
                                    continue
                                
                                # BibTeX経由で書籍情報を取得
                                bibtex_book_info = get_book_info_from_bibtex(isbn)
                                if bibtex_book_info:
                                    # tqdm.write(f"BibTeXから取得した書籍情報: {bibtex_book_info}")
                                    
                                    # 書籍名の類似度比較
                                    existing_title = bibtex_book_info.get('title', '')
                                    if syllabus_title and existing_title:
                                        similarity = calculate_similarity(syllabus_title, existing_title)
                                        # tqdm.write(f"類似度: {similarity:.3f} (シラバス: {syllabus_title}, BibTeX: {existing_title})")
                                        if similarity < 0.05:
                                            books_uncategorized.append({
                                                'syllabus_id': syllabus_id,
                                                'title': title,
                                                'author': author,
                                                'publisher': publisher,
                                                'price': price,
                                                'role': role,
                                                'isbn': isbn,
                                                'categorization_status': '問題レコード: 書籍名類似度低',
                                                'created_at': now,
                                                'updated_at': now
                                            })
                                            continue
                                    
                                    # BibTeXデータで空の項目がある場合は未分類に
                                    empty_fields = []
                                    if not bibtex_book_info.get('title', ''):
                                        empty_fields.append('タイトル')
                                    if not bibtex_book_info.get('author', ''):
                                        empty_fields.append('著者')
                                    if not bibtex_book_info.get('publisher', ''):
                                        empty_fields.append('出版社')
                                    if empty_fields:
                                        books_uncategorized.append({
                                            'syllabus_id': syllabus_id,
                                            'title': title,
                                            'author': author,
                                            'publisher': publisher,
                                            'price': price,
                                            'role': role,
                                            'isbn': isbn,
                                            'categorization_status': f'不正BibTeX データ: Null検知 - {", ".join(empty_fields)}が空',
                                            'created_at': now,
                                            'updated_at': now
                                        })
                                        stats['uncategorized_books'] += 1
                                        continue
                                    
                                    # 正常な書籍として登録
                                    book_info = {
                                        'title': bibtex_book_info.get('title', '') if bibtex_book_info.get('title', '') else syllabus_title,
                                        'isbn': isbn,
                                        'author': normalize_author(bibtex_book_info.get('author', '')) if bibtex_book_info.get('author', '') else author,
                                        'publisher': bibtex_book_info.get('publisher', '') if bibtex_book_info.get('publisher', '') else publisher,
                                        'price': price,
                                        'created_at': now
                                    }
                                    books.append(book_info)
                                    processed_isbns.add(isbn)
                                    stats['valid_books'] += 1
                                else:
                                    # BibTeX取得に失敗した場合は既存のCiNiiデータを使用
                                    try:
                                        with open(book_json_path, 'r', encoding='utf-8') as f:
                                            existing_data = json.load(f)
                                        
                                        if '@graph' in existing_data and len(existing_data['@graph']) > 0:
                                            channel = existing_data['@graph'][0]
                                            if 'items' in channel and len(channel['items']) > 0:
                                                item = channel['items'][0]
                                                
                                                # 書籍名の類似度比較
                                                existing_title = item.get('title', '')
                                                if syllabus_title and existing_title:
                                                    similarity = calculate_similarity(syllabus_title, existing_title)
                                                    if similarity < 0.05:
                                                        books_uncategorized.append({
                                                            'syllabus_id': syllabus_id,
                                                            'title': title,
                                                            'author': author,
                                                            'publisher': publisher,
                                                            'price': price,
                                                            'role': role,
                                                            'isbn': isbn,
                                                            'categorization_status': '問題レコード: 書籍名類似度低',
                                                            'created_at': now,
                                                            'updated_at': now
                                                        })
                                                        stats['uncategorized_books'] += 1
                                                        continue
                                                
                                                # CiNiiデータで空の項目がある場合は未分類に
                                                empty_fields = []
                                                if not item.get('title', ''):
                                                    empty_fields.append('タイトル')
                                                if not item.get('dc:creator', ''):
                                                    empty_fields.append('著者')
                                                if not item.get('dc:publisher', ''):
                                                    empty_fields.append('出版社')
                                                if empty_fields:
                                                    books_uncategorized.append({
                                                        'syllabus_id': syllabus_id,
                                                        'title': title,
                                                        'author': author,
                                                        'publisher': publisher,
                                                        'price': price,
                                                        'role': role,
                                                        'isbn': isbn,
                                                        'categorization_status': f'不正CiNii データ: Null検知 - {", ".join(empty_fields)}が空',
                                                        'created_at': now,
                                                        'updated_at': now
                                                    })
                                                    stats['uncategorized_books'] += 1
                                                    continue
                                                
                                                # 正常な書籍として登録
                                                cinii_title = item.get('title', '')
                                                cinii_author = normalize_author(item.get('dc:creator', ''))
                                                cinii_publisher = item.get('dc:publisher', '')
                                                
                                                book_info = {
                                                    'title': cinii_title if cinii_title else syllabus_title,
                                                    'isbn': isbn,
                                                    'author': cinii_author if cinii_author else author,
                                                    'publisher': cinii_publisher if cinii_publisher else publisher,
                                                    'price': price,
                                                    'created_at': now
                                                }
                                                
                                                # publisherが配列の場合は最初の要素を使用
                                                if isinstance(book_info['publisher'], list):
                                                    book_info['publisher'] = book_info['publisher'][0] if book_info['publisher'] else ''
                                                
                                                books.append(book_info)
                                                processed_isbns.add(isbn)
                                                stats['valid_books'] += 1
                                            else:
                                                # itemsが見つからない場合は未分類に
                                                books_uncategorized.append({
                                                    'syllabus_id': syllabus_id,
                                                    'title': title,
                                                    'author': author,
                                                    'publisher': publisher,
                                                    'price': price,
                                                    'role': role,
                                                    'isbn': isbn,
                                                    'categorization_status': '問題ISBN: ciniiデータ不在',
                                                    'created_at': now,
                                                    'updated_at': now
                                                })
                                                stats['uncategorized_books'] += 1
                                                stats['cinii_failures'] += 1
                                    except Exception as e:
                                        # tqdm.write(f"警告: 既存JSONファイル {book_json_path} の読み込みに失敗: {str(e)}")
                                        books_uncategorized.append({
                                            'syllabus_id': syllabus_id,
                                            'title': title,
                                            'author': author,
                                            'publisher': publisher,
                                            'price': price,
                                            'role': role,
                                            'isbn': isbn,
                                            'categorization_status': '問題ISBN: ciniiデータ不在',
                                            'created_at': now,
                                            'updated_at': now
                                        })
                                        stats['uncategorized_books'] += 1
                                        stats['cinii_failures'] += 1

                # テキスト情報の処理（教科書）
                if 'テキスト' in detail and '内容' in detail['テキスト'] and detail['テキスト']['内容'] is not None:
                    text_content = detail['テキスト']['内容']
                    if isinstance(text_content, dict) and '書籍' in text_content:
                        process_books(text_content['書籍'], '教科書')

                # 参考文献情報の処理（参考書）
                if '参考文献' in detail and '内容' in detail['参考文献'] and detail['参考文献']['内容'] is not None:
                    ref_content = detail['参考文献']['内容']
                    if isinstance(ref_content, dict) and '書籍' in ref_content:
                        process_books(ref_content['書籍'], '参考書')
            except Exception as e:
                continue
        
        # 最終統計の表示
        tqdm.write("\n" + "="*60)
        tqdm.write("処理完了 - 統計情報")
        tqdm.write("="*60)
        tqdm.write(f"総ファイル数: {stats['total_files']}")
        tqdm.write(f"処理済みファイル数: {stats['processed_files']}")
        tqdm.write(f"総書籍数: {stats['total_books']}")
        tqdm.write(f"正常書籍数: {stats['valid_books']}")
        tqdm.write(f"未分類書籍数: {stats['uncategorized_books']}")
        tqdm.write(f"重複ISBN数: {stats['duplicate_isbns']}")
        tqdm.write(f"不正ISBN数: {stats['invalid_isbns']}")
        tqdm.write(f"CiNii取得失敗数: {stats['cinii_failures']}")
        tqdm.write("="*60)
        
        return books, books_uncategorized
        
    except Exception as e:
        tqdm.write(f"書籍情報取得中にエラーが発生しました: {str(e)}")
        import traceback
        tqdm.write(f"エラーの詳細: {traceback.format_exc()}")
        return books, books_uncategorized
    finally:
        # データベース接続を閉じる
        if session:
            session.close()

def get_cinii_data(isbn: str) -> Optional[Dict[str, str]]:
    """ciniiから書籍データを取得する"""
    try:
        # ciniiのAPIエンドポイント
        url = f"https://ci.nii.ac.jp/books/opensearch/search?isbn={isbn}&format=json"
        
        # ヘッダーの設定
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # APIリクエスト
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # リクエスト間隔を設定（1秒）
        time.sleep(1)
        
        # JSONデータを解析
        data = response.json()
        
        # 書籍情報が存在する場合
        if data.get('@graph') and len(data['@graph']) > 0:
            book_data = data['@graph'][0]
            
            # src/books/json/{ISBN}.jsonに保存（仕様書準拠）
            books_dir = Path("src/books/json")
            books_dir.mkdir(exist_ok=True)
            book_json_path = books_dir / f"{isbn}.json"
            
            with open(book_json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return {
                'title': book_data.get('dc:title', ''),
                'author': book_data.get('dc:creator', ''),
                'publisher': book_data.get('dc:publisher', '')
            }
        
        return None
    
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            tqdm.write(f"警告: CiNii BooksのAPIアクセスが制限されています。ISBN {isbn} の書籍情報を取得できませんでした。")
        else:
            tqdm.write(f"警告: CiNii BooksのAPIでエラーが発生しました。ISBN {isbn} の書籍情報を取得できませんでした。")
        return None
    except Exception as e:
        tqdm.write(f"警告: ISBN {isbn} の書籍情報を取得中にエラーが発生しました: {str(e)}")
        return None

def create_book_json(books: List[Dict[str, Any]]) -> str:
    """正常書籍情報のJSONファイルを作成する"""
    output_dir = os.path.join("updates", "book", "add")
    os.makedirs(output_dir, exist_ok=True)
    
    # 現在の日時を取得してファイル名を生成
    current_time = datetime.now()
    filename = f"book_{current_time.strftime('%Y%m%d_%H%M')}.json"
    output_file = os.path.join(output_dir, filename)
    
    data = {
        "books": [{
            "title": book["title"],
            "author": book["author"],
            "publisher": book["publisher"],
            "price": book["price"],
            "isbn": book["isbn"],
            "created_at": current_time.isoformat()
        } for book in sorted(books, key=lambda x: (x["title"], x["publisher"]))]
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return output_file

def create_book_uncategorized_json(books_uncategorized: List[Dict[str, Any]]) -> str:
    """未分類書籍情報のJSONファイルを作成する"""
    output_dir = os.path.join("updates", "book_uncategorized", "add")
    os.makedirs(output_dir, exist_ok=True)
    
    # 現在の日時を取得してファイル名を生成
    current_time = datetime.now()
    filename = f"book_uncategorized_{current_time.strftime('%Y%m%d_%H%M')}.json"
    output_file = os.path.join(output_dir, filename)
    
    data = {
        "book_uncategorized": [{
            "syllabus_id": book["syllabus_id"],
            "title": book["title"],
            "author": book["author"],
            "publisher": book["publisher"],
            "price": book["price"],
            "role": book["role"],
            "isbn": book["isbn"],
            "categorization_status": book["categorization_status"],
            "created_at": book["created_at"],
            "updated_at": book["updated_at"]
        } for book in sorted(books_uncategorized, key=lambda x: (x["title"], x["syllabus_id"]))]
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return output_file

def test_similarity():
    """類似度計算のテスト"""
    test_cases = [
        ("振動学", "振動学 = Mechanical vibration"),
        ("材料の科学と工学〈1〉材料の微細構造", "機械材料入門")
    ]
    
    for title1, title2 in test_cases:
        similarity = calculate_similarity(title1, title2)
        tqdm.write(f"類似度: {similarity:.3f}")
        tqdm.write(f"  シラバス: {title1}")
        tqdm.write(f"  CiNii: {title2}")
        tqdm.write(f"  判定: {'類似度低い' if similarity < 0.05 else '類似度高い'}")
        tqdm.write("")

def save_bibtex_file(bn: str, bibtex_content: str):
    """BibTeXファイルを保存"""
    bibtex_dir = Path("src/books/bib")
    bibtex_dir.mkdir(exist_ok=True)
    bibtex_file = bibtex_dir / f"{bn}.bib"
    
    with open(bibtex_file, 'w', encoding='utf-8') as f:
        f.write(bibtex_content)
    
    # tqdm.write(f"BibTeXファイルを保存しました: {bibtex_file}")

def extract_bn_from_cinii_json(data: dict) -> Optional[str]:
    """CiNii JSONからBNを抽出"""
    try:
        if '@graph' in data and len(data['@graph']) > 0:
            channel = data['@graph'][0]
            if 'items' in channel and len(channel['items']) > 0:
                item = channel['items'][0]
                # @idからBNを抽出 (例: https://ci.nii.ac.jp/ncid/BB29265110 -> BB29265110)
                item_id = item.get('@id', '')
                if '/ncid/' in item_id:
                    bn = item_id.split('/ncid/')[-1]
                    return bn
        return None
    except Exception as e:
        # tqdm.write(f"BN抽出に失敗: {str(e)}")
        return None

def get_bibtex_from_bn(bn: str) -> Optional[str]:
    """BNからBibTeXファイルを取得"""
    try:
        url = f"https://ci.nii.ac.jp/ncid/{bn}.bib"
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except Exception as e:
        # tqdm.write(f"BibTeX取得に失敗: {bn} - {str(e)}")
        return None

def parse_bibtex(bibtex_text: str) -> Optional[Dict[str, str]]:
    """BibTeXテキストをパースして書籍情報を抽出"""
    try:
        # 正しいBibTeXパーサー
        lines = bibtex_text.split('\n')
        book_info = {}
        
        for line in lines:
            line = line.strip()
            if line.startswith('author'):
                # author = "Turro, Nicholas J. and Ramamurthy, V. and Scaiano, J. C. and 井上, 晴夫  and 伊藤, 攻",
                if '=' in line:
                    value_part = line.split('=', 1)[1].strip()
                    # 最初と最後のダブルクォートを除去し、末尾のカンマも除去
                    if value_part.startswith('"') and value_part.endswith('",'):
                        book_info['author'] = value_part[1:-2]
                    elif value_part.startswith('"') and value_part.endswith('"'):
                        book_info['author'] = value_part[1:-1]
            elif line.startswith('title'):
                if '=' in line:
                    value_part = line.split('=', 1)[1].strip()
                    if value_part.startswith('"') and value_part.endswith('",'):
                        book_info['title'] = value_part[1:-2]
                    elif value_part.startswith('"') and value_part.endswith('"'):
                        book_info['title'] = value_part[1:-1]
            elif line.startswith('publisher'):
                if '=' in line:
                    value_part = line.split('=', 1)[1].strip()
                    if value_part.startswith('"') and value_part.endswith('",'):
                        book_info['publisher'] = value_part[1:-2]
                    elif value_part.startswith('"') and value_part.endswith('"'):
                        book_info['publisher'] = value_part[1:-1]
        
        # tqdm.write(f"BibTeXパース結果: {book_info}")  # デバッグ情報
        return book_info if book_info else None
    except Exception as e:
        # tqdm.write(f"BibTeXパースに失敗: {str(e)}")
        return None

def get_book_info_from_bibtex(isbn: str) -> Optional[Dict[str, str]]:
    """既存JSONからBNを抽出し、BibTeXから書籍情報を取得"""
    try:
        # 1. 既存JSONファイルからBNを抽出
        json_file = f"src/books/json/{isbn}.json"
        if not os.path.exists(json_file):
            return None
            
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        bn = extract_bn_from_cinii_json(data)
        if not bn:
            return None
        
        # 2. 既存のBibTeXファイルをチェック
        bibtex_file = f"src/books/bib/{bn}.bib"
        bibtex_content = None
        
        if os.path.exists(bibtex_file):
            # 既存のBibTeXファイルを読み込み
            # tqdm.write(f"既存のBibTeXファイルを使用: {bibtex_file}")
            with open(bibtex_file, 'r', encoding='utf-8') as f:
                bibtex_content = f.read()
        else:
            # 2. BNからBibTeXファイルを取得
            bibtex_content = get_bibtex_from_bn(bn)
            if bibtex_content:
                # 3. BibTeXファイルを保存
                save_bibtex_file(bn, bibtex_content)
        
        if not bibtex_content:
            return None
        
        # 4. BibTeXから書籍情報を抽出
        return parse_bibtex(bibtex_content)
        
    except Exception as e:
        # tqdm.write(f"BibTeX経由の書籍情報取得に失敗: {isbn} - {str(e)}")
        return None

def normalize_author(author_str: str) -> str:
    """著者名を正規化する"""
    if not author_str:
        return ''
    
    # 前後の空白を除去
    author_str = author_str.strip()
    
    # 複数の区切り文字に対応（カンマ、セミコロン、and、ほか）
    import re
    # カンマ、セミコロン、and、ほかで分割
    authors = re.split(r'[,;]|\s+and\s+|\s+ほか\s*', author_str)
    
    # 各著者名を正規化
    normalized_authors = []
    for author in authors:
        author = author.strip()
        if author:  # 空でない場合のみ追加
            # 前後の空白を除去
            author = author.strip()
            # 連続する空白を1つに
            author = re.sub(r'\s+', ' ', author)
            normalized_authors.append(author)
    
    # 重複を除去してカンマ区切りで結合
    unique_authors = list(dict.fromkeys(normalized_authors))  # 順序を保持して重複除去
    return ', '.join(unique_authors)

def main():
    """メイン処理"""
    session = None
    try:
        # 年度の取得
        year = get_year_from_user()
        tqdm.write(f"\n{'='*60}")
        tqdm.write(f"書籍情報抽出処理開始 - 対象年度: {year}")
        tqdm.write(f"{'='*60}")
        
        # 書籍情報の取得
        tqdm.write("\n📚 書籍情報の取得を開始します...")
        books, books_uncategorized = get_book_info(year)
        
        # 結果サマリー
        tqdm.write(f"\n{'='*60}")
        tqdm.write("📊 抽出結果サマリー")
        tqdm.write(f"{'='*60}")
        tqdm.write(f"✅ 正常書籍: {len(books)}件")
        tqdm.write(f"⚠️  未分類書籍: {len(books_uncategorized)}件")
        tqdm.write(f"📈 合計: {len(books) + len(books_uncategorized)}件")
        
        # JSONファイルの作成
        tqdm.write(f"\n💾 JSONファイルの作成を開始します...")
        if books:
            book_output_file = create_book_json(books)
            tqdm.write(f"✅ 正常書籍JSONファイルを作成しました: {book_output_file}")
        else:
            tqdm.write("ℹ️  正常書籍は0件でした")
            
        if books_uncategorized:
            uncategorized_output_file = create_book_uncategorized_json(books_uncategorized)
            tqdm.write(f"⚠️  未分類書籍JSONファイルを作成しました: {uncategorized_output_file}")
        else:
            tqdm.write("ℹ️  未分類書籍は0件でした")
        
        tqdm.write(f"\n{'='*60}")
        tqdm.write("🎉 処理が完了しました！")
        tqdm.write(f"{'='*60}")
        
    except Exception as e:
        tqdm.write(f"\n❌ エラーが発生しました: {str(e)}")
        import traceback
        tqdm.write(f"📋 エラーの詳細: {traceback.format_exc()}")
        raise
    finally:
        # データベース接続を閉じる
        if session:
            session.close()

if __name__ == "__main__":
    # 類似度テスト
    test_similarity()
    
    # メイン処理
    main() 