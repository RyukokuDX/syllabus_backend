from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class SubjectProgram:
    syllabus_code: str
    program: str
    program_en: str
    created_at: datetime
    updated_at: datetime

class SubjectProgramParser:
    @staticmethod
    def parse(raw_data: Dict[str, Any]) -> Optional[SubjectProgram]:
        try:
            return SubjectProgram(
                syllabus_code=raw_data.get('syllabus_code', ''),
                program=raw_data.get('program', ''),
                program_en=raw_data.get('program_en', ''),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        except Exception as e:
            print(f"Error parsing subject program data: {e}")
            return None 