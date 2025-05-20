from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class SubjectRequirement:
    syllabus_code: str
    requirement_code: str
    created_at: datetime
    updated_at: datetime

class SubjectRequirementParser:
    @staticmethod
    def parse(raw_data: Dict[str, Any]) -> Optional[SubjectRequirement]:
        try:
            return SubjectRequirement(
                syllabus_code=raw_data.get('syllabus_code', ''),
                requirement_code=raw_data.get('requirement_code', ''),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        except Exception as e:
            print(f"Error parsing subject requirement data: {e}")
            return None 