#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
書籍情報抽出スクリプト
File Version: v1.3.5
Project Version: v1.3.5
"""

import os
import json
import glob
import csv
import re
import requests
import xml.etree.ElementTree as ET
import time
from typing import List, Dict, Set, Tuple, Any, Optional
from datetime import datetime
from tqdm import tqdm
from .utils import get_year_from_user
from pathlib import Path

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

def get_current_year() -> int:
    """現在の年度を取得する"""
    return datetime.now().year

def validate_isbn(isbn: str) -> bool:
    """ISBNのチェックディジットを検証する"""
    if not isbn:
        return False
    
    # 数字以外の文字を除去（Xは除く）
    isbn = ''.join(c for c in isbn if c.isdigit() or c.upper() == 'X')
    
    # ISBN-10の場合
    if len(isbn) == 10:
        total = 0
        for i in range(9):
            total += int(isbn[i]) * (10 - i)
        check_digit = (11 - (total % 11)) % 11
        # チェックデジットが10の場合は'X'
        expected_check = 'X' if check_digit == 10 else str(check_digit)
        return expected_check.upper() == isbn[9].upper()
    
    # ISBN-13の場合
    elif len(isbn) == 13:
        total = 0
        for i in range(12):
            weight = 1 if i % 2 == 0 else 3
            total += int(isbn[i]) * weight
        check_digit = (10 - (total % 10)) % 10
        return str(check_digit) == isbn[12]
    
    return False

def normalize_isbn(isbn: str) -> str:
    """ISBNを正規化する（ISBN-10をISBN-13に変換）"""
    if not isbn:
        return isbn
    
    # ハイフンを除去
    isbn = isbn.replace('-', '')
    
    # ISBN-10の場合、ISBN-13に変換
    if len(isbn) == 10:
        # 978を先頭に追加
        isbn = '978' + isbn[:-1]
        
        # チェックディジットを計算
        total = 0
        for i, digit in enumerate(isbn):
            weight = 1 if i % 2 == 0 else 3
            total += int(digit) * weight
        
        check_digit = (10 - (total % 10)) % 10
        isbn = isbn + str(check_digit)
    
    return isbn

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

def check_isbn_database(isbn: str, book_info: Dict, year: int) -> Tuple[bool, str]:
    """ISBNデータベースで書籍情報を検証"""
    try:
        # ISBNデータベースのパスを設定
        isbn_db_path = Path(f"src/db/isbn/{year}/isbn.json")
        if not isbn_db_path.exists():
            return True, ""  # データベースが存在しない場合は検証をスキップ
        
        # ISBNデータベースを読み込む
        with open(isbn_db_path, 'r', encoding='utf-8') as f:
            isbn_db = json.load(f)
        
        # ISBNで検索
        if isbn in isbn_db:
            db_book = isbn_db[isbn]
            # 書籍名の類似度を計算（閾値を0.2に変更）
            similarity = calculate_similarity(book_info['name'], db_book['title'])
            if similarity < 0.2:
                return False, f"ISBNデータ不一致: シラバス書籍名「{book_info['name']}」、ISBNデータ書籍名「{db_book['title']}」"
            return True, ""
        
        return True, ""  # ISBNが存在しない場合は検証をスキップ
    
    except Exception as e:
        print(f"ISBNデータベースの検証中にエラーが発生しました: {str(e)}")
        return True, ""  # エラーの場合は検証をスキップ

def log_warning(message: str, json_file: str, year: int):
    """警告をCSVファイルに記録"""
    # 現在の日時を取得してファイル名を生成
    current_time = datetime.now()
    filename = f"book_{current_time.strftime('%Y%m%d_%H%M')}.csv"
    warning_file = f"warning/{year}/{filename}"
    os.makedirs(os.path.dirname(warning_file), exist_ok=True)
    
    # ファイルが存在しない場合はヘッダーを書き込む
    if not os.path.exists(warning_file):
        with open(warning_file, 'w', encoding='utf-8') as f:
            f.write('"{projectルートからのシラバスjsonのpath}", "error message", "time"\n')
    
    # 警告を追記（ファイル名をプロジェクトルートからの相対パスに変換）
    relative_path = str(Path(json_file).relative_to(Path.cwd())) if json_file else ""
    with open(warning_file, 'a', encoding='utf-8') as f:
        f.write(f'"{relative_path}", "{message}", "{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}"\n')

def collect_valid_isbns(year: int) -> Set[str]:
    """シラバスから正規のISBNを収集する"""
    valid_isbns = set()
    script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    json_pattern = os.path.join(script_dir, 'syllabus', str(year), 'json', '*.json')
    
    # JSONファイルの検索
    json_files = glob.glob(json_pattern)
    if not json_files:
        error_msg = f"JSONファイルが見つかりません: {json_pattern}"
        log_warning(error_msg, "", year)
        raise FileNotFoundError(error_msg)
    
    print(f"処理対象ファイル数: {len(json_files)}")
    
    # 各JSONファイルを処理
    for json_file in tqdm(json_files, desc="ISBN収集中"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 詳細情報の取得
            if '詳細情報' not in data:
                continue
                
            detail = data['詳細情報']
            
            # テキスト情報の処理
            if 'テキスト' in detail and '内容' in detail['テキスト'] and detail['テキスト']['内容'] is not None:
                text_content = detail['テキスト']['内容']
                if isinstance(text_content, dict) and '書籍' in text_content:
                    books_list = text_content['書籍']
                    if isinstance(books_list, list):
                        print(f"テキスト書籍数: {len(books_list)}")  # デバッグ情報
                        for book in books_list:
                            isbn = book.get('ISBN', '').strip()
                            print(f"ISBN: {isbn}, 書籍名: {book.get('書籍名', '')}")  # デバッグ情報
                            if not isbn or not validate_isbn(isbn):
                                print(f"無効なISBNまたは空のISBN: {isbn}")  # デバッグ情報
                                if not isbn:
                                    log_warning("不正ISBN: 桁数違反", json_file, year)
                                else:
                                    log_warning("不正ISBN: cd違反", json_file, year)
                                continue
                            if isbn and validate_isbn(isbn):
                                valid_isbns.add(isbn)
            
            # 参考文献情報の処理
            if '参考文献' in detail and '内容' in detail['参考文献'] and detail['参考文献']['内容'] is not None:
                ref_content = detail['参考文献']['内容']
                if isinstance(ref_content, dict) and '書籍' in ref_content:
                    books_list = ref_content['書籍']
                    if isinstance(books_list, list):
                        for book in books_list:
                            isbn = book.get('ISBN', '')
                            if isbn and validate_isbn(isbn):
                                valid_isbns.add(isbn)
                            
        except Exception as e:
            log_warning(f"ファイル処理エラー: {str(e)}", json_file, year)
            continue
    
    return valid_isbns

def get_book_info(year: int) -> List[Dict[str, Any]]:
    """書籍情報を取得する"""
    books = []
    
    # 既存の書籍JSONファイルのパスを設定
    books_json_dir = Path("src/books/json")
    
    # シラバスから書籍情報を取得
    script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    json_pattern = os.path.join(script_dir, 'syllabus', str(year), 'json', '*.json')
    
    for json_file in tqdm(glob.glob(json_pattern), desc="シラバスから書籍情報取得中"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if '詳細情報' not in data:
                continue
                
            detail = data['詳細情報']
            
            # テキスト情報の処理
            if 'テキスト' in detail and '内容' in detail['テキスト'] and detail['テキスト']['内容'] is not None:
                text_content = detail['テキスト']['内容']
                if isinstance(text_content, dict) and '書籍' in text_content:
                    books_list = text_content['書籍']
                    if isinstance(books_list, list):
                        print(f"テキスト書籍数: {len(books_list)}")  # デバッグ情報
                        for book in books_list:
                            isbn = book.get('ISBN', '').strip()
                            print(f"ISBN: {isbn}, 書籍名: {book.get('書籍名', '')}")  # デバッグ情報
                            if not isbn or not validate_isbn(isbn):
                                print(f"無効なISBNまたは空のISBN: {isbn}")  # デバッグ情報
                                if not isbn:
                                    log_warning("不正ISBN: 桁数違反", json_file, year)
                                else:
                                    log_warning("不正ISBN: cd違反", json_file, year)
                                continue
                                
                            # シラバスから価格情報を取得
                            price = None
                            price_str = book.get('価格', '')
                            if price_str:
                                try:
                                    price = int(price_str.replace(',', ''))
                                except ValueError:
                                    pass
                            
                            # シラバスから書籍名を取得（類似度比較用）
                            syllabus_title = book.get('書籍名', '').strip()
                            
                            # 既存のJSONファイルの存在確認
                            book_json_path = books_json_dir / f"{isbn}.json"
                            if book_json_path.exists():
                                print(f"既存JSONファイル発見: {book_json_path}")  # デバッグ情報
                                try:
                                    with open(book_json_path, 'r', encoding='utf-8') as f:
                                        existing_data = json.load(f)
                                    
                                    # CiNii APIレスポンス形式から書籍情報を抽出
                                    if '@graph' in existing_data and len(existing_data['@graph']) > 0:
                                        channel = existing_data['@graph'][0]
                                        if 'items' in channel and len(channel['items']) > 0:
                                            item = channel['items'][0]
                                            print(f"CiNiiデータ: title={item.get('title', '')}, author={item.get('dc:creator', '')}, publisher={item.get('dc:publisher', '')}")  # デバッグ情報
                                            
                                            # 書籍名の類似度比較
                                            existing_title = item.get('title', '')
                                            if syllabus_title and existing_title:
                                                similarity = calculate_similarity(syllabus_title, existing_title)
                                                print(f"類似度: {similarity:.3f} (シラバス: {syllabus_title}, CiNii: {existing_title})")  # デバッグ情報
                                                if similarity < 0.2:
                                                    log_warning("問題レコード: 書籍名類似度低", json_file, year)
                                                    continue
                                            
                                            # 書籍情報を作成（既存JSONから取得、priceのみシラバスから）
                                            book_info = {
                                                'title': item.get('title', ''),
                                                'isbn': isbn,
                                                'author': item.get('dc:creator', ''),
                                                'publisher': item.get('dc:publisher', ''),
                                                'price': price,  # シラバスから取得
                                                'created_at': datetime.now().isoformat()
                                            }
                                            
                                            # publisherが配列の場合は最初の要素を使用
                                            if isinstance(book_info['publisher'], list):
                                                book_info['publisher'] = book_info['publisher'][0] if book_info['publisher'] else ''
                                            
                                            print(f"作成された書籍情報: {book_info}")  # デバッグ情報
                                            books.append(book_info)
                                        else:
                                            print(f"CiNii JSONにitemsが見つかりません: {book_json_path}")  # デバッグ情報
                                    else:
                                        print(f"CiNii JSONに@graphが見つかりません: {book_json_path}")  # デバッグ情報
                                        
                                except Exception as e:
                                    print(f"警告: 既存JSONファイル {book_json_path} の読み込みに失敗: {str(e)}")
                                    # エラーの場合はシラバスデータのみで作成
                                    book_info = {
                                        'title': syllabus_title,
                                        'isbn': isbn,
                                        'author': book.get('著者', '').strip(),
                                        'publisher': book.get('出版社', '').strip(),
                                        'price': price,
                                        'created_at': datetime.now().isoformat()
                                    }
                                    books.append(book_info)
                            else:
                                print(f"既存JSONファイルが存在しません: {book_json_path}")  # デバッグ情報
                                # 既存JSONファイルが存在しない場合はCiNiiから取得
                                try:
                                    cinii_data = get_cinii_data(isbn)
                                    if cinii_data:
                                        # 書籍情報を作成
                                        book_info = {
                                            'title': cinii_data.get('title', syllabus_title),
                                            'isbn': isbn,
                                            'author': cinii_data.get('author', book.get('著者', '').strip()),
                                            'publisher': cinii_data.get('publisher', book.get('出版社', '').strip()),
                                            'price': price,
                                            'created_at': datetime.now().isoformat()
                                        }
                                        books.append(book_info)
                                    else:
                                        log_warning("問題ISBN: ciniiデータ不在", json_file, year)
                                        # CiNiiデータがない場合はシラバスデータのみで作成
                                        book_info = {
                                            'title': syllabus_title,
                                            'isbn': isbn,
                                            'author': book.get('著者', '').strip(),
                                            'publisher': book.get('出版社', '').strip(),
                                            'price': price,
                                            'created_at': datetime.now().isoformat()
                                        }
                                        books.append(book_info)
                                except Exception as e:
                                    print(f"警告: ISBN {isbn} の情報取得中にエラーが発生しました: {str(e)}")
                                    # エラーの場合はシラバスデータのみで作成
                                    book_info = {
                                        'title': syllabus_title,
                                        'isbn': isbn,
                                        'author': book.get('著者', '').strip(),
                                        'publisher': book.get('出版社', '').strip(),
                                        'price': price,
                                        'created_at': datetime.now().isoformat()
                                    }
                                    books.append(book_info)
            
            # 参考文献情報の処理（テキスト情報と同じ処理）
            if '参考文献' in detail and '内容' in detail['参考文献'] and detail['参考文献']['内容'] is not None:
                ref_content = detail['参考文献']['内容']
                if isinstance(ref_content, dict) and '書籍' in ref_content:
                    books_list = ref_content['書籍']
                    if isinstance(books_list, list):
                        print(f"参考文献数: {len(books_list)}")  # デバッグ情報
                        for book in books_list:
                            isbn = book.get('ISBN', '').strip()
                            print(f"参考文献 ISBN: {isbn}, 書籍名: {book.get('書籍名', '')}")  # デバッグ情報
                            if not isbn or not validate_isbn(isbn):
                                print(f"無効なISBNまたは空のISBN: {isbn}")  # デバッグ情報
                                if not isbn:
                                    log_warning("不正ISBN: 桁数違反", json_file, year)
                                else:
                                    log_warning("不正ISBN: cd違反", json_file, year)
                                continue
                                
                            # シラバスから価格情報を取得
                            price = None
                            price_str = book.get('価格', '')
                            if price_str:
                                try:
                                    price = int(price_str.replace(',', ''))
                                except ValueError:
                                    pass
                            
                            # シラバスから書籍名を取得（類似度比較用）
                            syllabus_title = book.get('書籍名', '').strip()
                            
                            # 既存のJSONファイルの存在確認
                            book_json_path = books_json_dir / f"{isbn}.json"
                            if book_json_path.exists():
                                print(f"既存JSONファイル発見: {book_json_path}")  # デバッグ情報
                                try:
                                    with open(book_json_path, 'r', encoding='utf-8') as f:
                                        existing_data = json.load(f)
                                    
                                    # CiNii APIレスポンス形式から書籍情報を抽出
                                    if '@graph' in existing_data and len(existing_data['@graph']) > 0:
                                        channel = existing_data['@graph'][0]
                                        if 'items' in channel and len(channel['items']) > 0:
                                            item = channel['items'][0]
                                            
                                            # 書籍名の類似度比較
                                            existing_title = item.get('title', '')
                                            if syllabus_title and existing_title:
                                                similarity = calculate_similarity(syllabus_title, existing_title)
                                                if similarity < 0.2:
                                                    log_warning("問題レコード: 書籍名類似度低", json_file, year)
                                                    continue
                                            
                                            # 書籍情報を作成（既存JSONから取得、priceのみシラバスから）
                                            book_info = {
                                                'title': item.get('title', ''),
                                                'isbn': isbn,
                                                'author': item.get('dc:creator', ''),
                                                'publisher': item.get('dc:publisher', ''),
                                                'price': price,  # シラバスから取得
                                                'created_at': datetime.now().isoformat()
                                            }
                                            
                                            # publisherが配列の場合は最初の要素を使用
                                            if isinstance(book_info['publisher'], list):
                                                book_info['publisher'] = book_info['publisher'][0] if book_info['publisher'] else ''
                                            
                                            print(f"作成された書籍情報: {book_info}")  # デバッグ情報
                                            books.append(book_info)
                                        
                                except Exception as e:
                                    print(f"警告: 既存JSONファイル {book_json_path} の読み込みに失敗: {str(e)}")
                                    # エラーの場合はシラバスデータのみで作成
                                    book_info = {
                                        'title': syllabus_title,
                                        'isbn': isbn,
                                        'author': book.get('著者', '').strip(),
                                        'publisher': book.get('出版社', '').strip(),
                                        'price': price,
                                        'created_at': datetime.now().isoformat()
                                    }
                                    books.append(book_info)
                            else:
                                # 既存JSONファイルが存在しない場合はCiNiiから取得
                                try:
                                    cinii_data = get_cinii_data(isbn)
                                    if cinii_data:
                                        # 書籍情報を作成
                                        book_info = {
                                            'title': cinii_data.get('title', syllabus_title),
                                            'isbn': isbn,
                                            'author': cinii_data.get('author', book.get('著者', '').strip()),
                                            'publisher': cinii_data.get('publisher', book.get('出版社', '').strip()),
                                            'price': price,
                                            'created_at': datetime.now().isoformat()
                                        }
                                        books.append(book_info)
                                    else:
                                        log_warning("問題ISBN: ciniiデータ不在", json_file, year)
                                        # CiNiiデータがない場合はシラバスデータのみで作成
                                        book_info = {
                                            'title': syllabus_title,
                                            'isbn': isbn,
                                            'author': book.get('著者', '').strip(),
                                            'publisher': book.get('出版社', '').strip(),
                                            'price': price,
                                            'created_at': datetime.now().isoformat()
                                        }
                                        books.append(book_info)
                                except Exception as e:
                                    print(f"警告: ISBN {isbn} の情報取得中にエラーが発生しました: {str(e)}")
                                    # エラーの場合はシラバスデータのみで作成
                                    book_info = {
                                        'title': syllabus_title,
                                        'isbn': isbn,
                                        'author': book.get('著者', '').strip(),
                                        'publisher': book.get('出版社', '').strip(),
                                        'price': price,
                                        'created_at': datetime.now().isoformat()
                                    }
                                    books.append(book_info)
                            
        except Exception as e:
            log_warning(f"ファイル処理エラー: {str(e)}", json_file, year)
            continue
    
    return books

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
            return {
                'title': book_data.get('dc:title', ''),
                'author': book_data.get('dc:creator', ''),
                'publisher': book_data.get('dc:publisher', '')
            }
        
        return None
    
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            print(f"警告: CiNii BooksのAPIアクセスが制限されています。ISBN {isbn} の書籍情報を取得できませんでした。")
        else:
            print(f"警告: CiNii BooksのAPIでエラーが発生しました。ISBN {isbn} の書籍情報を取得できませんでした。")
        return None
    except Exception as e:
        print(f"警告: ISBN {isbn} の書籍情報を取得中にエラーが発生しました: {str(e)}")
        return None

def create_book_json(books: List[Dict[str, Any]]) -> str:
    """書籍情報のJSONファイルを作成する"""
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

def process_book_info(book: dict, json_file: str, year: int) -> Optional[dict]:
    """書籍情報を処理"""
    if not book or not isinstance(book, dict):
        return None
    
    # 書籍名の取得
    book_name = book.get('書籍名', '').strip()
    if not book_name:
        return None
    
    # ISBNの取得と検証
    isbn = book.get('ISBN', '').strip()
    if isbn:
        if not validate_isbn(isbn):
            log_warning(f"無効なISBN: {isbn}", json_file, year)
        else:
            # ISBNデータベースとの整合性チェック
            is_valid, error_msg = check_isbn_database(isbn, {'name': book_name}, year)
            if not is_valid:
                log_warning(error_msg, json_file, year)
    
    # 著者名の取得
    author = book.get('著者名', '').strip()
    
    # 出版社の取得
    publisher = book.get('出版社', '').strip()
    
    # 出版年の取得と検証
    year_str = book.get('出版年', '').strip()
    if year_str and not year_str.isdigit():
        log_warning(f"無効な出版年: {year_str}", json_file, year)
        year_str = None
    
    # 書籍情報の作成
    book_info = {
        "name": book_name,
        "isbn": isbn if isbn else None,
        "author": author if author else None,
        "publisher": publisher if publisher else None,
        "year": int(year_str) if year_str else None
    }
    
    return book_info

def process_json_file(json_file: Path, year: int) -> List[dict]:
    """JSONファイルを処理して書籍情報を抽出"""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, dict):
            log_warning("JSONデータが辞書形式ではありません", str(json_file), year)
            return []
        
        # 詳細情報の取得
        detail_info = data.get('詳細情報', {})
        if not detail_info:
            return []
        
        books = []
        processed_names = set()  # 書籍名の重複チェック用
        processed_isbns = set()  # ISBNの重複チェック用
        
        # テキスト情報の処理
        text_content = detail_info.get('テキスト情報', {})
        if text_content and isinstance(text_content, dict):
            book_list = text_content.get('書籍', [])
            if isinstance(book_list, list):
                for book in book_list:
                    if book is None or not isinstance(book, dict):
                        continue
                    
                    book_info = process_book_info(book, str(json_file), year)
                    if not book_info:
                        continue
                    
                    # ISBNの重複チェック
                    if book_info['isbn'] and book_info['isbn'] in processed_isbns:
                        log_warning(f"重複するISBN: {book_info['isbn']} ({book_info['name']})", str(json_file), year)
                        continue
                    
                    # 書籍名の重複チェック
                    if book_info['name'] not in processed_names:
                        # 類似度チェック（閾値0.2に変更）
                        is_duplicate = False
                        for existing_book in books:
                            if calculate_similarity(book_info['name'], existing_book['name']) > 0.2:
                                is_duplicate = True
                                break
                        
                        if not is_duplicate:
                            books.append(book_info)
                            processed_names.add(book_info['name'])
                            if book_info['isbn']:
                                processed_isbns.add(book_info['isbn'])
        
        # 参考文献情報の処理
        ref_content = detail_info.get('参考文献情報', {})
        if ref_content and isinstance(ref_content, dict):
            book_list = ref_content.get('書籍', [])
            if isinstance(book_list, list):
                for book in book_list:
                    if book is None or not isinstance(book, dict):
                        continue
                    
                    book_info = process_book_info(book, str(json_file), year)
                    if not book_info:
                        continue
                    
                    # ISBNの重複チェック
                    if book_info['isbn'] and book_info['isbn'] in processed_isbns:
                        log_warning(f"重複するISBN: {book_info['isbn']} ({book_info['name']})", str(json_file), year)
                        continue
                    
                    # 書籍名の重複チェック
                    if book_info['name'] not in processed_names:
                        # 類似度チェック（閾値0.2に変更）
                        is_duplicate = False
                        for existing_book in books:
                            if calculate_similarity(book_info['name'], existing_book['name']) > 0.2:
                                is_duplicate = True
                                break
                        
                        if not is_duplicate:
                            books.append(book_info)
                            processed_names.add(book_info['name'])
                            if book_info['isbn']:
                                processed_isbns.add(book_info['isbn'])
        
        return books
    
    except json.JSONDecodeError as e:
        log_warning(f"JSONの解析に失敗: {str(e)}", str(json_file), year)
        return []
    except Exception as e:
        log_warning(f"ファイル処理エラー: {str(e)}", str(json_file), year)
        return []

def main():
    """メイン処理"""
    try:
        # 年度の取得
        year = get_year_from_user()
        print(f"処理対象年度: {year}")
        
        # 書籍情報の取得
        print("書籍情報の取得を開始します...")
        books = get_book_info(year)
        print(f"抽出された書籍情報: {len(books)}件")
        
        # JSONファイルの作成
        print("JSONファイルの作成を開始します...")
        output_file = create_book_json(books)
        print(f"JSONファイルを作成しました: {output_file}")
        
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        import traceback
        print(f"エラーの詳細: {traceback.format_exc()}")
        raise

if __name__ == "__main__":
    main() 