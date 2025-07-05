# -*- coding: utf-8 -*-
# cursorはversionを弄るな
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
from typing import List, Dict, Set, Tuple, Any, Optional
from datetime import datetime
from tqdm import tqdm
from .utils import get_year_from_user, get_db_connection, get_syllabus_master_id_from_db
from pathlib import Path
from sqlalchemy import text

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

def get_book_id_from_db(session, isbn: str) -> Optional[int]:
	"""ISBNからbook_idを取得する"""
	try:
		query = text("""
			SELECT book_id 
			FROM book 
			WHERE isbn = :isbn
		""")
		
		result = session.execute(
			query,
			{"isbn": isbn}
		).first()
		
		return result[0] if result else None
	except Exception as e:
		tqdm.write(f"[DB接続エラー] book取得時にエラー: {e}")
		session.rollback()
		return None

def get_syllabus_book_info(year: int) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
	"""シラバス書籍情報を取得する（正常・未分類の2リストを返す）"""
	syllabus_books = []  # 正常なシラバス書籍関連
	syllabus_books_uncategorized = []  # 未分類シラバス書籍関連
	
	# 統計情報
	stats = {
		'total_files': 0,
		'processed_files': 0,
		'total_books': 0,
		'valid_books': 0,
		'uncategorized_books': 0,
		'invalid_isbns': 0,
		'book_not_found': 0
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
				
				# 基本情報から年度を取得
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
				
				# テキスト情報の処理
				if 'テキスト' in detail and '内容' in detail['テキスト'] and detail['テキスト']['内容'] is not None:
					text_content = detail['テキスト']['内容']
					if isinstance(text_content, dict) and '書籍' in text_content:
						books_list = text_content['書籍']
						if isinstance(books_list, list) and books_list:  # nullでない場合のみ処理
							stats['total_books'] += len(books_list)
							
							# 書籍処理の進捗を表示
							for book in tqdm(books_list, desc=f"書籍処理中 ({syllabus_code})", leave=False):
								isbn = book.get('ISBN', '').strip()
								title = book.get('書籍名', '').strip()
								author = book.get('著者', '').strip()
								publisher = book.get('出版社', '').strip()
								price = None
								price_str = book.get('価格', '')
								if price_str and price_str.strip():
									try:
										price = int(price_str.replace(',', '').replace('円', ''))
									except ValueError:
										pass
								role = '教科書'
								now = datetime.now().isoformat()
								
								# ISBNがnullの場合
								if not isbn:
									stats['uncategorized_books'] += 1
									continue
								
								# ISBNの有効性をチェック
								if not validate_isbn(isbn):
									stats['invalid_isbns'] += 1
									stats['uncategorized_books'] += 1
									continue
								
								# ISBNが正常な場合、bookテーブルからIDを取得
								book_id = get_book_id_from_db(session, isbn)
								
								if not book_id:
									# bookテーブルに存在しない場合
									stats['book_not_found'] += 1
									stats['uncategorized_books'] += 1
									continue
								
								# 正常なシラバス書籍関連として登録
								syllabus_book_info = {
									'syllabus_id': syllabus_id,
									'book_id': book_id,
									'role': role,
									'created_at': now
								}
								syllabus_books.append(syllabus_book_info)
								stats['valid_books'] += 1
								
				# 参考文献情報の処理
				if '参考文献' in detail and '内容' in detail['参考文献'] and detail['参考文献']['内容'] is not None:
					reference_content = detail['参考文献']['内容']
					if isinstance(reference_content, dict) and '書籍' in reference_content:
						books_list = reference_content['書籍']
						if isinstance(books_list, list) and books_list:  # nullでない場合のみ処理
							stats['total_books'] += len(books_list)
							
							# 書籍処理の進捗を表示
							for book in tqdm(books_list, desc=f"参考文献処理中 ({syllabus_code})", leave=False):
								isbn = book.get('ISBN', '').strip()
								title = book.get('書籍名', '').strip()
								author = book.get('著者', '').strip()
								publisher = book.get('出版社', '').strip()
								price = None
								price_str = book.get('価格', '')
								if price_str and price_str.strip():
									try:
										price = int(price_str.replace(',', '').replace('円', ''))
									except ValueError:
										pass
								role = '参考書'
								now = datetime.now().isoformat()
								
								# ISBNがnullの場合
								if not isbn:
									stats['uncategorized_books'] += 1
									continue
								
								# ISBNの有効性をチェック
								if not validate_isbn(isbn):
									stats['invalid_isbns'] += 1
									stats['uncategorized_books'] += 1
									continue
								
								# ISBNが正常な場合、bookテーブルからIDを取得
								book_id = get_book_id_from_db(session, isbn)
								
								if not book_id:
									# bookテーブルに存在しない場合
									stats['book_not_found'] += 1
									stats['uncategorized_books'] += 1
									continue
								
								# 正常なシラバス書籍関連として登録
								syllabus_book_info = {
									'syllabus_id': syllabus_id,
									'book_id': book_id,
									'role': role,
									'created_at': now
								}
								syllabus_books.append(syllabus_book_info)
								stats['valid_books'] += 1
								
			except Exception as e:
				continue
		
		# 最終統計の表示
		tqdm.write("\n" + "="*60)
		tqdm.write("処理完了 - 統計情報")
		tqdm.write("="*60)
		tqdm.write(f"総ファイル数: {stats['total_files']}")
		tqdm.write(f"処理済みファイル数: {stats['processed_files']}")
		tqdm.write(f"総書籍数: {stats['total_books']}")
		tqdm.write(f"正常シラバス書籍関連数: {stats['valid_books']}")
		tqdm.write(f"未分類シラバス書籍関連数: {stats['uncategorized_books']}")
		tqdm.write(f"不正ISBN数: {stats['invalid_isbns']}")
		tqdm.write(f"bookテーブルに存在しない数: {stats['book_not_found']}")
		tqdm.write("="*60)
		
		return syllabus_books, syllabus_books_uncategorized
		
	except Exception as e:
		tqdm.write(f"シラバス書籍情報取得中にエラーが発生しました: {str(e)}")
		import traceback
		tqdm.write(f"エラーの詳細: {traceback.format_exc()}")
		return syllabus_books, syllabus_books_uncategorized
	finally:
		# データベース接続を閉じる
		if session:
			session.close()

def create_syllabus_book_json(syllabus_books: List[Dict[str, Any]]) -> str:
	"""正常シラバス書籍関連情報のJSONファイルを作成する"""
	output_dir = os.path.join("updates", "syllabus_book", "add")
	os.makedirs(output_dir, exist_ok=True)
	
	# 現在の日時を取得してファイル名を生成
	current_time = datetime.now()
	filename = f"syllabus_book_{current_time.strftime('%Y%m%d_%H%M')}.json"
	output_file = os.path.join(output_dir, filename)
	
	data = {
		"syllabus_books": [{
			"syllabus_id": book["syllabus_id"],
			"book_id": book["book_id"],
			"role": book["role"],
			"created_at": book["created_at"]
		} for book in sorted(syllabus_books, key=lambda x: (x["syllabus_id"], x["book_id"]))]
	}
	
	with open(output_file, 'w', encoding='utf-8') as f:
		json.dump(data, f, ensure_ascii=False, indent=2)
	
	return output_file

def main():
	"""メイン処理"""
	session = None
	try:
		# 年度の取得
		year = get_year_from_user()
		tqdm.write(f"\n{'='*60}")
		tqdm.write(f"シラバス書籍関連情報抽出処理開始 - 対象年度: {year}")
		tqdm.write(f"{'='*60}")
		
		# シラバス書籍関連情報の取得
		tqdm.write("\n📚 シラバス書籍関連情報の取得を開始します...")
		syllabus_books, syllabus_books_uncategorized = get_syllabus_book_info(year)
		
		# 結果サマリー
		tqdm.write(f"\n{'='*60}")
		tqdm.write("📊 抽出結果サマリー")
		tqdm.write(f"{'='*60}")
		tqdm.write(f"✅ 正常シラバス書籍関連: {len(syllabus_books)}件")
		tqdm.write(f"⚠️  未分類シラバス書籍関連: {len(syllabus_books_uncategorized)}件")
		tqdm.write(f"📈 合計: {len(syllabus_books) + len(syllabus_books_uncategorized)}件")
		
		# JSONファイルの作成
		tqdm.write(f"\n💾 JSONファイルの作成を開始します...")
		if syllabus_books:
			syllabus_book_output_file = create_syllabus_book_json(syllabus_books)
			tqdm.write(f"✅ 正常シラバス書籍関連JSONファイルを作成しました: {syllabus_book_output_file}")
		else:
			tqdm.write("ℹ️  正常シラバス書籍関連は0件でした")
		
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
	# メイン処理
	main()