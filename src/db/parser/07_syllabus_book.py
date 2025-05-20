from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class SyllabusBook:
    syllabus_code: str
    book_id: str
    role: str
    role_en: str
    created_at: datetime
    updated_at: datetime

class SyllabusBookParser:
    @staticmethod
    def parse(raw_data: Dict[str, Any]) -> Optional[SyllabusBook]:
        try:
            return SyllabusBook(
                syllabus_code=raw_data.get('syllabus_code', ''),
                book_id=raw_data.get('book_id', ''),
                role=raw_data.get('role', ''),
                role_en=raw_data.get('role_en', ''),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        except Exception as e:
            print(f"Error parsing syllabus book data: {e}")
            return None 