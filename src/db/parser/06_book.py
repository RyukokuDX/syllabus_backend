#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
書籍情報抽出スクリプト
File Version: v1.3.6
Project Version: v1.3.10
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

def log_warning(message: str, json_file: str, year: int, isbn: str = "", recorded_warnings: set = None):
    """警告をCSVファイルに記録"""
    # 重複警告を防ぐ
    if recorded_warnings is not None and isbn:
        warning_key = f"{isbn}:{message}"
        if warning_key in recorded_warnings:
            return  # 既に記録済みの場合はスキップ
        recorded_warnings.add(warning_key)
    
    # 現在の日時を取得してファイル名を生成
    current_time = datetime.now()
    filename = f"book_{current_time.strftime('%Y%m%d_%H%M')}.csv"
    warning_file = f"warning/{year}/{filename}"
    os.makedirs(os.path.dirname(warning_file), exist_ok=True)
    
    # ファイルが存在しない場合はヘッダーを書き込む
    if not os.path.exists(warning_file):
        with open(warning_file, 'w', encoding='utf-8') as f:
            f.write('"{projectルートからのシラバスjsonのpath}", "ISBN", "error message", "time"\n')
    
    # 警告を追記（ファイル名をプロジェクトルートからの相対パスに変換）
    relative_path = str(Path(json_file).relative_to(Path.cwd())) if json_file else ""
    with open(warning_file, 'a', encoding='utf-8') as f:
        f.write(f'"{relative_path}", "{isbn}", "{message}", "{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}"\n')

def get_book_info(year: int) -> List[Dict[str, Any]]:
    """書籍情報を取得する"""
    books = []
    # 重複警告を防ぐためのセット
    recorded_warnings = set()
    
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
            
            # テキスト情報の処理（仕様書準拠）
            if 'テキスト' in detail and '内容' in detail['テキスト'] and detail['テキスト']['内容'] is not None:
                text_content = detail['テキスト']['内容']
                if isinstance(text_content, dict) and '書籍' in text_content:
                    books_list = text_content['書籍']
                    if isinstance(books_list, list):
                        for book in books_list:
                            isbn = book.get('ISBN', '').strip()
                            tqdm.write(f"処理中の書籍: ISBN={isbn}, 書籍名={book.get('書籍名', '')}, 著者={book.get('著者', '')}")  # デバッグ情報
                            if not isbn:
                                # ISBNがnullの場合：シラバスJSONのデータから出力JSONに追記
                                book_info = {
                                    'title': book.get('書籍名', '').strip(),
                                    'isbn': None,
                                    'author': book.get('著者', '').strip(),
                                    'publisher': book.get('出版社', '').strip(),
                                    'price': None,
                                    'created_at': datetime.now().isoformat()
                                }
                                books.append(book_info)
                                continue
                            
                            # ISBNが存在する場合の処理
                            if not validate_isbn(isbn):
                                # 数字以外の文字を除去した後の長さでチェック
                                cleaned_isbn = ''.join(c for c in isbn if c.isdigit() or c.upper() == 'X')
                                tqdm.write(f"不正ISBN検出: {isbn} -> クリーンアップ後: {cleaned_isbn} (長さ: {len(cleaned_isbn)})")
                                if len(cleaned_isbn) != 10 and len(cleaned_isbn) != 13:
                                    log_warning("不正ISBN: 桁数違反", json_file, year, isbn, recorded_warnings)
                                    tqdm.write(f"桁数違反: {len(cleaned_isbn)}桁 (期待: 10または13桁)")
                                else:
                                    log_warning("不正ISBN: cd違反", json_file, year, isbn, recorded_warnings)
                                    tqdm.write(f"チェックディジット違反: {cleaned_isbn}")
                                # シラバスJSONの対象レコードから出力JSONに追記
                                book_info = {
                                    'title': book.get('書籍名', '').strip(),
                                    'isbn': isbn,
                                    'author': book.get('著者', '').strip(),
                                    'publisher': book.get('出版社', '').strip(),
                                    'price': None,
                                    'created_at': datetime.now().isoformat()
                                }
                                books.append(book_info)
                                continue
                            
                            # ISBNが正常な場合
                            # シラバスから価格情報を取得
                            price = None
                            price_str = book.get('価格', '')
                            if price_str and price_str.strip():  # 空文字列でない場合のみ処理
                                try:
                                    price = int(price_str.replace(',', '').replace('円', ''))
                                except ValueError:
                                    pass
                            
                            # シラバスから書籍名を取得（類似度比較用）
                            syllabus_title = book.get('書籍名', '').strip()
                            
                            # src/books/json/{ISBN}.jsonの存在確認（仕様書準拠）
                            book_json_path = Path(f"src/books/json/{isbn}.json")
                            if book_json_path.exists():
                                tqdm.write(f"既存JSONファイル発見: {book_json_path}")  # デバッグ情報
                                try:
                                    with open(book_json_path, 'r', encoding='utf-8') as f:
                                        existing_data = json.load(f)
                                    
                                    # CiNii APIレスポンス形式から書籍情報を抽出
                                    if '@graph' in existing_data and len(existing_data['@graph']) > 0:
                                        channel = existing_data['@graph'][0]
                                        if 'items' in channel and len(channel['items']) > 0:
                                            item = channel['items'][0]
                                            tqdm.write(f"CiNiiデータ: title={item.get('title', '')}, author={item.get('dc:creator', '')}, publisher={item.get('dc:publisher', '')}")  # デバッグ情報
                                            
                                            # BibTeX経由で書籍情報を取得
                                            bibtex_book_info = get_book_info_from_bibtex(isbn)
                                            if bibtex_book_info:
                                                tqdm.write(f"BibTeXから取得した書籍情報: {bibtex_book_info}")  # デバッグ情報
                                                tqdm.write(f"BibTeXデータ詳細: title='{bibtex_book_info.get('title', '')}', author='{bibtex_book_info.get('author', '')}', publisher='{bibtex_book_info.get('publisher', '')}'")  # デバッグ情報
                                                
                                                # 書籍名の類似度比較
                                                existing_title = bibtex_book_info.get('title', '')
                                                if syllabus_title and existing_title:
                                                    similarity = calculate_similarity(syllabus_title, existing_title)
                                                    tqdm.write(f"類似度: {similarity:.3f} (シラバス: {syllabus_title}, BibTeX: {existing_title})")  # デバッグ情報
                                                    if similarity < 0.05:  # 閾値を0.05に変更
                                                        log_warning(f"問題レコード: 書籍名類似度低 - シラバス書籍名「{syllabus_title}」、BibTeX書籍名「{existing_title}」", json_file, year, isbn, recorded_warnings)
                                                        continue
                                                
                                                # BibTeXデータで空の項目がある場合はwarningに記載
                                                empty_fields = []
                                                if not bibtex_book_info.get('title', ''):
                                                    empty_fields.append('タイトル')
                                                if not bibtex_book_info.get('author', ''):
                                                    empty_fields.append('著者')
                                                if not bibtex_book_info.get('publisher', ''):
                                                    empty_fields.append('出版社')
                                                if empty_fields:
                                                    log_warning(f"不正BibTeX データ: Null検知 - {', '.join(empty_fields)}が空", json_file, year, isbn, recorded_warnings)
                                                
                                                # 書籍情報を作成（BibTeXから取得、priceのみシラバスから）
                                                book_info = {
                                                    'title': bibtex_book_info.get('title', '') if bibtex_book_info.get('title', '') else syllabus_title,
                                                    'isbn': isbn,
                                                    'author': bibtex_book_info.get('author', '') if bibtex_book_info.get('author', '') else book.get('著者', '').strip(),
                                                    'publisher': bibtex_book_info.get('publisher', '') if bibtex_book_info.get('publisher', '') else book.get('出版社', '').strip(),
                                                    'price': price,  # シラバスから取得
                                                    'created_at': datetime.now().isoformat()
                                                }
                                                
                                                tqdm.write(f"作成された書籍情報: {book_info}")  # デバッグ情報
                                                books.append(book_info)
                                            else:
                                                # BibTeX取得に失敗した場合は既存のCiNiiデータを使用
                                                tqdm.write(f"BibTeX取得に失敗、既存CiNiiデータを使用: {isbn}")  # デバッグ情報
                                                
                                                # 書籍名の類似度比較
                                                existing_title = item.get('title', '')
                                                if syllabus_title and existing_title:
                                                    similarity = calculate_similarity(syllabus_title, existing_title)
                                                    tqdm.write(f"類似度: {similarity:.3f} (シラバス: {syllabus_title}, CiNii: {existing_title})")  # デバッグ情報
                                                    if similarity < 0.05:  # 閾値を0.05に変更
                                                        log_warning(f"問題レコード: 書籍名類似度低 - シラバス書籍名「{syllabus_title}」、CiNii書籍名「{existing_title}」", json_file, year, isbn, recorded_warnings)
                                                        continue
                                                
                                                # CiNiiデータで空の項目がある場合はwarningに記載
                                                empty_fields = []
                                                if not item.get('title', ''):
                                                    empty_fields.append('タイトル')
                                                if not item.get('dc:creator', ''):
                                                    empty_fields.append('著者')
                                                if not item.get('dc:publisher', ''):
                                                    empty_fields.append('出版社')
                                                if empty_fields:
                                                    log_warning(f"不正CiNii データ: Null検知 - {', '.join(empty_fields)}が空", json_file, year, isbn, recorded_warnings)
                                                
                                                # 書籍情報を作成（既存JSONから取得、priceのみシラバスから）
                                                # CiNiiデータが空の場合はシラバスデータを優先
                                                cinii_title = item.get('title', '')
                                                cinii_author = item.get('dc:creator', '')
                                                cinii_publisher = item.get('dc:publisher', '')
                                                
                                                tqdm.write(f"CiNiiデータ確認: title='{cinii_title}', author='{cinii_author}', publisher='{cinii_publisher}'")  # デバッグ情報
                                                
                                                book_info = {
                                                    'title': cinii_title if cinii_title else syllabus_title,
                                                    'isbn': isbn,
                                                    'author': cinii_author if cinii_author else book.get('著者', '').strip(),
                                                    'publisher': cinii_publisher if cinii_publisher else book.get('出版社', '').strip(),
                                                    'price': price,  # シラバスから取得
                                                    'created_at': datetime.now().isoformat()
                                                }
                                                
                                                # publisherが配列の場合は最初の要素を使用
                                                if isinstance(book_info['publisher'], list):
                                                    book_info['publisher'] = book_info['publisher'][0] if book_info['publisher'] else ''
                                                
                                                tqdm.write(f"作成された書籍情報: {book_info}")  # デバッグ情報
                                                tqdm.write(f"元のCiNiiデータ: title={item.get('title', '')}, author={item.get('dc:creator', '')}, publisher={item.get('dc:publisher', '')}")  # デバッグ情報
                                                books.append(book_info)
                                        else:
                                            tqdm.write(f"CiNii JSONにitemsが見つかりません: {book_json_path}")  # デバッグ情報
                                            # itemsが見つからない場合はシラバスデータのみで作成
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
                                        tqdm.write(f"CiNii JSONに@graphが見つかりません: {book_json_path}")  # デバッグ情報
                                        # @graphが見つからない場合はシラバスデータのみで作成
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
                                    tqdm.write(f"警告: 既存JSONファイル {book_json_path} の読み込みに失敗: {str(e)}")  # デバッグ情報
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
                                tqdm.write(f"既存JSONファイルが存在しません: {book_json_path}")  # デバッグ情報
                                # 既存JSONファイルが存在しない場合はCiNiiから取得
                                try:
                                    cinii_data = get_cinii_data(isbn)
                                    if cinii_data:
                                        tqdm.write(f"CiNiiから取得成功: {isbn}")  # デバッグ情報
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
                                        tqdm.write(f"CiNiiから取得失敗: {isbn}")  # デバッグ情報
                                        log_warning("問題ISBN: ciniiデータ不在", json_file, year, isbn, recorded_warnings)
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
                                    tqdm.write(f"CiNii取得中にエラー: {isbn} - {str(e)}")  # デバッグ情報
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
            
            # 参考文献情報の処理（仕様書準拠）
            if '参考文献' in detail and '内容' in detail['参考文献'] and detail['参考文献']['内容'] is not None:
                ref_content = detail['参考文献']['内容']
                if isinstance(ref_content, dict) and '書籍' in ref_content:
                    books_list = ref_content['書籍']
                    if isinstance(books_list, list):
                        for book in books_list:
                            isbn = book.get('ISBN', '').strip()
                            tqdm.write(f"処理中の書籍: ISBN={isbn}, 書籍名={book.get('書籍名', '')}, 著者={book.get('著者', '')}")  # デバッグ情報
                            if not isbn:
                                # ISBNがnullの場合：シラバスJSONのデータから出力JSONに追記
                                book_info = {
                                    'title': book.get('書籍名', '').strip(),
                                    'isbn': None,
                                    'author': book.get('著者', '').strip(),
                                    'publisher': book.get('出版社', '').strip(),
                                    'price': None,
                                    'created_at': datetime.now().isoformat()
                                }
                                books.append(book_info)
                                continue
                            
                            # ISBNが存在する場合の処理
                            if not validate_isbn(isbn):
                                # 数字以外の文字を除去した後の長さでチェック
                                cleaned_isbn = ''.join(c for c in isbn if c.isdigit() or c.upper() == 'X')
                                tqdm.write(f"不正ISBN検出: {isbn} -> クリーンアップ後: {cleaned_isbn} (長さ: {len(cleaned_isbn)})")
                                if len(cleaned_isbn) != 10 and len(cleaned_isbn) != 13:
                                    log_warning("不正ISBN: 桁数違反", json_file, year, isbn, recorded_warnings)
                                    tqdm.write(f"桁数違反: {len(cleaned_isbn)}桁 (期待: 10または13桁)")
                                else:
                                    log_warning("不正ISBN: cd違反", json_file, year, isbn, recorded_warnings)
                                    tqdm.write(f"チェックディジット違反: {cleaned_isbn}")
                                # シラバスJSONの対象レコードから出力JSONに追記
                                book_info = {
                                    'title': book.get('書籍名', '').strip(),
                                    'isbn': isbn,
                                    'author': book.get('著者', '').strip(),
                                    'publisher': book.get('出版社', '').strip(),
                                    'price': None,
                                    'created_at': datetime.now().isoformat()
                                }
                                books.append(book_info)
                                continue
                            
                            # ISBNが正常な場合
                            # シラバスから価格情報を取得
                            price = None
                            price_str = book.get('価格', '')
                            if price_str and price_str.strip():  # 空文字列でない場合のみ処理
                                try:
                                    price = int(price_str.replace(',', '').replace('円', ''))
                                except ValueError:
                                    pass
                            
                            # シラバスから書籍名を取得（類似度比較用）
                            syllabus_title = book.get('書籍名', '').strip()
                            
                            # src/books/json/{ISBN}.jsonの存在確認（仕様書準拠）
                            book_json_path = Path(f"src/books/json/{isbn}.json")
                            if book_json_path.exists():
                                tqdm.write(f"既存JSONファイル発見: {book_json_path}")  # デバッグ情報
                                try:
                                    with open(book_json_path, 'r', encoding='utf-8') as f:
                                        existing_data = json.load(f)
                                    
                                    # CiNii APIレスポンス形式から書籍情報を抽出
                                    if '@graph' in existing_data and len(existing_data['@graph']) > 0:
                                        channel = existing_data['@graph'][0]
                                        if 'items' in channel and len(channel['items']) > 0:
                                            item = channel['items'][0]
                                            tqdm.write(f"CiNiiデータ: title={item.get('title', '')}, author={item.get('dc:creator', '')}, publisher={item.get('dc:publisher', '')}")  # デバッグ情報
                                            
                                            # BibTeX経由で書籍情報を取得
                                            bibtex_book_info = get_book_info_from_bibtex(isbn)
                                            if bibtex_book_info:
                                                tqdm.write(f"BibTeXから取得した書籍情報: {bibtex_book_info}")  # デバッグ情報
                                                tqdm.write(f"BibTeXデータ詳細: title='{bibtex_book_info.get('title', '')}', author='{bibtex_book_info.get('author', '')}', publisher='{bibtex_book_info.get('publisher', '')}'")  # デバッグ情報
                                                
                                                # 書籍名の類似度比較
                                                existing_title = bibtex_book_info.get('title', '')
                                                if syllabus_title and existing_title:
                                                    similarity = calculate_similarity(syllabus_title, existing_title)
                                                    tqdm.write(f"類似度: {similarity:.3f} (シラバス: {syllabus_title}, BibTeX: {existing_title})")  # デバッグ情報
                                                    if similarity < 0.05:  # 閾値を0.05に変更
                                                        log_warning(f"問題レコード: 書籍名類似度低 - シラバス書籍名「{syllabus_title}」、BibTeX書籍名「{existing_title}」", json_file, year, isbn, recorded_warnings)
                                                        continue
                                                
                                                # BibTeXデータで空の項目がある場合はwarningに記載
                                                empty_fields = []
                                                if not bibtex_book_info.get('title', ''):
                                                    empty_fields.append('タイトル')
                                                if not bibtex_book_info.get('author', ''):
                                                    empty_fields.append('著者')
                                                if not bibtex_book_info.get('publisher', ''):
                                                    empty_fields.append('出版社')
                                                if empty_fields:
                                                    log_warning(f"不正BibTeX データ: Null検知 - {', '.join(empty_fields)}が空", json_file, year, isbn, recorded_warnings)
                                                
                                                # 書籍情報を作成（BibTeXから取得、priceのみシラバスから）
                                                book_info = {
                                                    'title': bibtex_book_info.get('title', '') if bibtex_book_info.get('title', '') else syllabus_title,
                                                    'isbn': isbn,
                                                    'author': bibtex_book_info.get('author', '') if bibtex_book_info.get('author', '') else book.get('著者', '').strip(),
                                                    'publisher': bibtex_book_info.get('publisher', '') if bibtex_book_info.get('publisher', '') else book.get('出版社', '').strip(),
                                                    'price': price,  # シラバスから取得
                                                    'created_at': datetime.now().isoformat()
                                                }
                                                
                                                tqdm.write(f"作成された書籍情報: {book_info}")  # デバッグ情報
                                                books.append(book_info)
                                            else:
                                                # BibTeX取得に失敗した場合は既存のCiNiiデータを使用
                                                tqdm.write(f"BibTeX取得に失敗、既存CiNiiデータを使用: {isbn}")  # デバッグ情報
                                                
                                                # 書籍名の類似度比較
                                                existing_title = item.get('title', '')
                                                if syllabus_title and existing_title:
                                                    similarity = calculate_similarity(syllabus_title, existing_title)
                                                    tqdm.write(f"類似度: {similarity:.3f} (シラバス: {syllabus_title}, CiNii: {existing_title})")  # デバッグ情報
                                                    if similarity < 0.05:  # 閾値を0.05に変更
                                                        log_warning(f"問題レコード: 書籍名類似度低 - シラバス書籍名「{syllabus_title}」、CiNii書籍名「{existing_title}」", json_file, year, isbn, recorded_warnings)
                                                        continue
                                                
                                                # CiNiiデータで空の項目がある場合はwarningに記載
                                                empty_fields = []
                                                if not item.get('title', ''):
                                                    empty_fields.append('タイトル')
                                                if not item.get('dc:creator', ''):
                                                    empty_fields.append('著者')
                                                if not item.get('dc:publisher', ''):
                                                    empty_fields.append('出版社')
                                                if empty_fields:
                                                    log_warning(f"不正CiNii データ: Null検知 - {', '.join(empty_fields)}が空", json_file, year, isbn, recorded_warnings)
                                                
                                                # 書籍情報を作成（既存JSONから取得、priceのみシラバスから）
                                                # CiNiiデータが空の場合はシラバスデータを優先
                                                cinii_title = item.get('title', '')
                                                cinii_author = item.get('dc:creator', '')
                                                cinii_publisher = item.get('dc:publisher', '')
                                                
                                                tqdm.write(f"CiNiiデータ確認: title='{cinii_title}', author='{cinii_author}', publisher='{cinii_publisher}'")  # デバッグ情報
                                                
                                                book_info = {
                                                    'title': cinii_title if cinii_title else syllabus_title,
                                                    'isbn': isbn,
                                                    'author': cinii_author if cinii_author else book.get('著者', '').strip(),
                                                    'publisher': cinii_publisher if cinii_publisher else book.get('出版社', '').strip(),
                                                    'price': price,  # シラバスから取得
                                                    'created_at': datetime.now().isoformat()
                                                }
                                                
                                                # publisherが配列の場合は最初の要素を使用
                                                if isinstance(book_info['publisher'], list):
                                                    book_info['publisher'] = book_info['publisher'][0] if book_info['publisher'] else ''
                                                
                                                tqdm.write(f"作成された書籍情報: {book_info}")  # デバッグ情報
                                                tqdm.write(f"元のCiNiiデータ: title={item.get('title', '')}, author={item.get('dc:creator', '')}, publisher={item.get('dc:publisher', '')}")  # デバッグ情報
                                                books.append(book_info)
                                        else:
                                            tqdm.write(f"CiNii JSONにitemsが見つかりません: {book_json_path}")  # デバッグ情報
                                            # itemsが見つからない場合はシラバスデータのみで作成
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
                                        tqdm.write(f"CiNii JSONに@graphが見つかりません: {book_json_path}")  # デバッグ情報
                                        # @graphが見つからない場合はシラバスデータのみで作成
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
                                    tqdm.write(f"警告: 既存JSONファイル {book_json_path} の読み込みに失敗: {str(e)}")  # デバッグ情報
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
                                        tqdm.write(f"CiNiiから取得成功: {isbn}")  # デバッグ情報
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
                                        tqdm.write(f"CiNiiから取得失敗: {isbn}")  # デバッグ情報
                                        log_warning("問題ISBN: ciniiデータ不在", json_file, year, isbn, recorded_warnings)
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
                                    tqdm.write(f"CiNii取得中にエラー: {isbn} - {str(e)}")  # デバッグ情報
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
    
    tqdm.write(f"BibTeXファイルを保存しました: {bibtex_file}")

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
        tqdm.write(f"BN抽出に失敗: {str(e)}")
        return None

def get_bibtex_from_bn(bn: str) -> Optional[str]:
    """BNからBibTeXファイルを取得"""
    try:
        url = f"https://ci.nii.ac.jp/ncid/{bn}.bib"
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except Exception as e:
        tqdm.write(f"BibTeX取得に失敗: {bn} - {str(e)}")
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
        
        tqdm.write(f"BibTeXパース結果: {book_info}")  # デバッグ情報
        return book_info if book_info else None
    except Exception as e:
        tqdm.write(f"BibTeXパースに失敗: {str(e)}")
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
            tqdm.write(f"既存のBibTeXファイルを使用: {bibtex_file}")
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
        tqdm.write(f"BibTeX経由の書籍情報取得に失敗: {isbn} - {str(e)}")
        return None

def main():
    """メイン処理"""
    try:
        # 年度の取得
        year = get_year_from_user()
        tqdm.write(f"処理対象年度: {year}")
        
        # 書籍情報の取得
        tqdm.write("書籍情報の取得を開始します...")
        books = get_book_info(year)
        tqdm.write(f"抽出された書籍情報: {len(books)}件")
        
        # JSONファイルの作成
        tqdm.write("JSONファイルの作成を開始します...")
        output_file = create_book_json(books)
        tqdm.write(f"JSONファイルを作成しました: {output_file}")
        
    except Exception as e:
        tqdm.write(f"エラーが発生しました: {str(e)}")
        import traceback
        tqdm.write(f"エラーの詳細: {traceback.format_exc()}")
        raise

if __name__ == "__main__":
    # 類似度テスト
    test_similarity()
    
    # メイン処理
    main() 