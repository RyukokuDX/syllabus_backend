from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Book:
    book_id: str
    title: str
    title_en: str
    author: str
    author_en: str
    publisher: str
    publisher_en: str
    isbn: str
    created_at: datetime
    updated_at: datetime

class BookParser:
    @staticmethod
    def parse(raw_data: Dict[str, Any]) -> Optional[Book]:
        try:
            return Book(
                book_id=raw_data.get('book_id', ''),
                title=raw_data.get('title', ''),
                title_en=raw_data.get('title_en', ''),
                author=raw_data.get('author', ''),
                author_en=raw_data.get('author_en', ''),
                publisher=raw_data.get('publisher', ''),
                publisher_en=raw_data.get('publisher_en', ''),
                isbn=raw_data.get('isbn', ''),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        except Exception as e:
            print(f"Error parsing book data: {e}")
            return None 