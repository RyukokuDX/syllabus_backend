from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class SyllabusFaculty:
    syllabus_code: str
    faculty: str
    faculty_en: str
    created_at: datetime
    updated_at: datetime

class SyllabusFacultyParser:
    @staticmethod
    def parse(raw_data: Dict[str, Any]) -> Optional[SyllabusFaculty]:
        try:
            return SyllabusFaculty(
                syllabus_code=raw_data.get('syllabus_code', ''),
                faculty=raw_data.get('faculty', ''),
                faculty_en=raw_data.get('faculty_en', ''),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        except Exception as e:
            print(f"Error parsing syllabus faculty data: {e}")
            return None 