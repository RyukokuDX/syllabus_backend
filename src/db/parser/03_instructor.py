from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Instructor:
    instructor_id: str
    name: str
    name_en: str
    created_at: datetime
    updated_at: datetime

class InstructorParser:
    @staticmethod
    def parse(raw_data: Dict[str, Any]) -> Optional[Instructor]:
        try:
            return Instructor(
                instructor_id=raw_data.get('instructor_id', ''),
                name=raw_data.get('name', ''),
                name_en=raw_data.get('name_en', ''),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        except Exception as e:
            print(f"Error parsing instructor data: {e}")
            return None 