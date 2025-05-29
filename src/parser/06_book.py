import os
import sys
import json
from pathlib import Path
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

# プロジェクトのルートディレクトリをPYTHONPATHに追加
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from src.db.models import Book, BookAuthor
from src.db.database import Database

@dataclass
class BookData:
    """書籍データ"""
    title: str
    publisher: Optional[str]
    price: Optional[int]
    isbn: Optional[str]
    authors: List[str]

def parse_book_info(html_content: str) -> List[BookData]:
    """HTMLから書籍情報を解析"""
    soup = BeautifulSoup(html_content, "html.parser")
    books = []

    # 教科書・参考書のセクションを探す
    book_sections = soup.find_all("div", class_="book-section")
    for section in book_sections:
        # 書籍情報を取得
        title_elem = section.find("div", class_="book-title")
        if not title_elem:
            continue

        title = title_elem.get_text(strip=True)
        if not title:
            continue

        # 出版社情報を取得
        publisher = None
        publisher_elem = section.find("div", class_="book-publisher")
        if publisher_elem:
            publisher = publisher_elem.get_text(strip=True)

        # 価格情報を取得
        price = None
        price_elem = section.find("div", class_="book-price")
        if price_elem:
            price_text = price_elem.get_text(strip=True)
            try:
                # "¥1,234" のような形式から数値のみを抽出
                price = int(price_text.replace("¥", "").replace(",", ""))
            except ValueError:
                pass

        # ISBN情報を取得
        isbn = None
        isbn_elem = section.find("div", class_="book-isbn")
        if isbn_elem:
            isbn = isbn_elem.get_text(strip=True)

        # 著者情報を取得
        authors = []
        author_elems = section.find_all("div", class_="book-author")
        for author_elem in author_elems:
            author = author_elem.get_text(strip=True)
            if author:
                authors.append(author)

        books.append(BookData(
            title=title,
            publisher=publisher,
            price=price,
            isbn=isbn,
            authors=authors
        ))

    return books

def save_books_to_db(books: List[BookData], db: Database) -> None:
    """書籍情報をデータベースに保存"""
    for book_data in books:
        # 書籍情報を保存
        book = Book(
            title=book_data.title,
            publisher=book_data.publisher,
            price=book_data.price,
            isbn=book_data.isbn
        )
        db.add(book)
        db.flush()  # book_idを取得するためにflush

        # 著者情報を保存
        for author_name in book_data.authors:
            author = BookAuthor(
                book_id=book.book_id,
                author_name=author_name
            )
            db.add(author)

    db.commit()

def is_duplicate_book(book: BookData, existing_books: List[Book], db: Database) -> bool:
    """書籍の重複チェック
    
    1. ISBNが存在する場合はISBNで比較
    2. ISBNが存在しない場合は、タイトル、出版社、価格、著者で比較
    """
    # ISBNで重複チェック
    if book.isbn:
        for existing_book in existing_books:
            if existing_book.isbn == book.isbn:
                return True

    # ISBNがない場合は全属性で比較
    for existing_book in existing_books:
        # 基本情報の比較
        if (existing_book.title != book.title or
            existing_book.publisher != book.publisher or
            existing_book.price != book.price):
            continue

        # 著者情報の比較
        existing_authors = [author.author_name for author in 
                          db.query(BookAuthor).filter(BookAuthor.book_id == existing_book.book_id).all()]
        if set(existing_authors) != set(book.authors):
            continue

        return True

    return False

def process_html_files(html_dir: str, db: Database) -> None:
    """HTMLファイルを処理して書籍情報を抽出・保存"""
    html_dir_path = Path(html_dir)
    if not html_dir_path.exists():
        print(f"Error: Directory {html_dir} does not exist")
        return

    # 既存の書籍情報を取得（重複チェック用）
    existing_books = db.query(Book).all()

    for html_file in html_dir_path.glob("*.html"):
        print(f"Processing {html_file.name}...")
        with open(html_file, "r", encoding="utf-8") as f:
            html_content = f.read()

        books = parse_book_info(html_content)
        if not books:
            print(f"No book information found in {html_file.name}")
            continue

        # 重複チェックを行い、新しい書籍のみを保存
        new_books = []
        for book in books:
            if not is_duplicate_book(book, existing_books, db):
                new_books.append(book)

        if new_books:
            save_books_to_db(new_books, db)
            print(f"Saved {len(new_books)} new books from {html_file.name}")
        else:
            print(f"No new books found in {html_file.name}")

def main():
    """メイン処理"""
    if len(sys.argv) != 2:
        print("Usage: python 06_book.py <year>")
        sys.exit(1)

    year = sys.argv[1]
    html_dir = f"src/syllabus/{year}/pretty_html"

    db = Database()
    try:
        process_html_files(html_dir, db)
    finally:
        db.close()

if __name__ == "__main__":
    main() 