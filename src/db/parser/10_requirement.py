from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Requirement:
    requirement_code: str
    requirement_name: str
    requirement_name_en: str
    created_at: datetime
    updated_at: datetime

class RequirementParser:
    @staticmethod
    def parse(raw_data: Dict[str, Any]) -> Optional[Requirement]:
        try:
            return Requirement(
                requirement_code=raw_data.get('requirement_code', ''),
                requirement_name=raw_data.get('requirement_name', ''),
                requirement_name_en=raw_data.get('requirement_name_en', ''),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        except Exception as e:
            print(f"Error parsing requirement data: {e}")
            return None 