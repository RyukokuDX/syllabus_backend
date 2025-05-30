import os
import json
from typing import List, Dict, Set
from datetime import datetime
from bs4 import BeautifulSoup
from tqdm import tqdm
import re

def get_current_year() -> int:
    """現在の年度を取得する"""
    return datetime.now().year

def get_year_from_user() -> int:
    """ユーザーから年度を入力してもらう"""
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

def get_html_files(year: int) -> List[str]:
    """指定された年度のHTMLファイルのパスを取得する"""
    base_dir = os.path.join("src", "syllabus", str(year), "raw_html")
    if not os.path.exists(base_dir):
        raise FileNotFoundError(f"ディレクトリが見つかりません: {base_dir}")
    
    html_files = [f for f in os.listdir(base_dir) if f.endswith('.html')]
    if not html_files:
        raise FileNotFoundError(f"HTMLファイルが見つかりません: {base_dir}")
    
    return [os.path.join(base_dir, f) for f in html_files]

def create_pretty_html(html_content: str, output_path: str) -> None:
    """HTMLを整形して保存する"""
    soup = BeautifulSoup(html_content, 'html.parser')
    pretty_html = soup.prettify()
    
    # 出力ディレクトリの作成
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(pretty_html)

def find_th_with_text(soup: BeautifulSoup, text: str) -> BeautifulSoup:
    """指定されたテキストを含むthタグを探す"""
    for th in soup.find_all('th'):
        if text in th.text:
            return th
    return None

def get_next_td_content(element: BeautifulSoup) -> str:
    """指定された要素の次のtdタグの内容を取得する"""
    next_td = element.find_next('td')
    if not next_td:
        return ""
    return next_td.text.strip()

def extract_book_info(html_content: str, file_path: str) -> List[Dict]:
    """HTMLから書籍情報を抽出する"""
    soup = BeautifulSoup(html_content, 'html.parser')
    books = []
    
    # 教科書情報を抽出
    textbook_th = find_th_with_text(soup, '教科書')
    if textbook_th:
        textbook_content = get_next_td_content(textbook_th)
        if textbook_content:
            books.append({
                'title': textbook_content,
                'role': '教科書',
                'note': None
            })
    
    # 参考書情報を抽出
    reference_th = find_th_with_text(soup, '参考書')
    if reference_th:
        reference_content = get_next_td_content(reference_th)
        if reference_content:
            books.append({
                'title': reference_content,
                'role': '参考書',
                'note': None
            })
    
    # その他の書籍情報を抽出（必要に応じて追加）
    
    return books

def create_book_json(books: Set[Dict]) -> str:
    """書籍情報のJSONファイルを作成する"""
    output_dir = os.path.join("updates", "book", "add")
    os.makedirs(output_dir, exist_ok=True)
    
    # 現在の日時を取得してファイル名を生成
    current_time = datetime.now()
    filename = f"book_{current_time.strftime('%Y%m%d_%H%M')}.json"
    output_file = os.path.join(output_dir, filename)
    
    # 書籍情報を整理
    book_data = []
    for book in sorted(books, key=lambda x: (x['role'], x['title'])):
        # タイトルから著者名、出版社、価格、ISBNを抽出
        title = book['title']
        author_name = None
        publisher = None
        price = None
        isbn = None
        
        # 著者名の抽出（「著者：」や「編著：」などのパターン）
        author_match = re.search(r'(?:著者|編著|共著|監修|訳者)[：:]\s*([^、。]+)', title)
        if author_match:
            author_name = author_match.group(1).strip()
        
        # 出版社の抽出（「出版社：」や「出版元：」などのパターン）
        publisher_match = re.search(r'(?:出版社|出版元)[：:]\s*([^、。]+)', title)
        if publisher_match:
            publisher = publisher_match.group(1).strip()
        
        # 価格の抽出（「価格：」や「定価：」などのパターン）
        price_match = re.search(r'(?:価格|定価)[：:]\s*(\d+(?:,\d+)*)円', title)
        if price_match:
            price_str = price_match.group(1).replace(',', '')
            try:
                price = int(price_str)
            except ValueError:
                pass
        
        # ISBNの抽出（ISBN-10またはISBN-13のパターン）
        isbn_match = re.search(r'ISBN[：:]\s*(\d{10}|\d{13})', title)
        if isbn_match:
            isbn = isbn_match.group(1)
        
        book_data.append({
            'book': {
                'title': title,
                'publisher': publisher,
                'price': price,
                'isbn': isbn,
                'created_at': current_time.isoformat()
            },
            'book_author': {
                'author_name': author_name
            } if author_name else None,
            'syllabus_book': {
                'role': book['role'],
                'note': book['note']
            }
        })
    
    data = {
        'books': book_data,
        'created_at': current_time.isoformat()
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return output_file

def get_pretty_html_path(raw_html_path: str) -> str:
    """raw_htmlのパスからpretty_htmlのパスを生成する"""
    return raw_html_path.replace('raw_html', 'pretty_html')

def process_html_file(html_file: str) -> List[Dict]:
    """HTMLファイルを処理して書籍情報を抽出する"""
    # 元のHTMLファイルを読み込む
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # pretty_htmlのパスを生成
    pretty_html_path = get_pretty_html_path(html_file)
    
    # pretty_htmlが存在しない場合、または元のHTMLファイルより新しい場合は作成
    if not os.path.exists(pretty_html_path) or \
       os.path.getmtime(html_file) > os.path.getmtime(pretty_html_path):
        create_pretty_html(html_content, pretty_html_path)
        html_content = BeautifulSoup(html_content, 'html.parser').prettify()
    else:
        # 既存のpretty_htmlを読み込む
        with open(pretty_html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
    
    # 書籍情報を抽出
    return extract_book_info(html_content, html_file)

def main():
    """メイン処理"""
    try:
        # 年度の取得
        year = get_year_from_user()
        print(f"処理対象年度: {year}")
        
        # HTMLファイルの取得
        html_files = get_html_files(year)
        print(f"処理対象ファイル: {len(html_files)}件")
        
        # 書籍情報の抽出
        all_books = set()
        for html_file in tqdm(html_files, desc="書籍情報を抽出中"):
            try:
                books = process_html_file(html_file)
                # 各書籍の情報をタプルに変換してセットに追加（重複を防ぐため）
                for book in books:
                    book_tuple = tuple(sorted(book.items()))
                    all_books.add(book_tuple)
            except Exception as e:
                print(f"エラー: {html_file}の処理中にエラーが発生しました: {str(e)}")
                raise  # エラーを発生させて処理を停止
        
        # タプルを辞書に戻す
        book_dicts = [dict(t) for t in all_books]
        print(f"抽出された書籍情報: {len(book_dicts)}件")
        
        # JSONファイルの作成
        output_file = create_book_json(book_dicts)
        print(f"JSONファイルを作成しました: {output_file}")
        
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        raise

if __name__ == "__main__":
    main() 