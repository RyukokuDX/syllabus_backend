from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class SyllabusInstructor:
    syllabus_code: str
    instructor_id: str
    created_at: datetime
    updated_at: datetime

class SyllabusInstructorParser:
    @staticmethod
    def parse(raw_data: Dict[str, Any]) -> Optional[SyllabusInstructor]:
        try:
            return SyllabusInstructor(
                syllabus_code=raw_data.get('syllabus_code', ''),
                instructor_id=raw_data.get('instructor_id', ''),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        except Exception as e:
            print(f"Error parsing syllabus instructor data: {e}")
            return None 