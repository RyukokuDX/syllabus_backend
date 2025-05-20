from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class GradingCriterion:
    criterion_id: str
    syllabus_code: str
    criteria_type: str
    criteria_type_en: str
    percentage: int
    created_at: datetime
    updated_at: datetime

class GradingCriterionParser:
    @staticmethod
    def parse(raw_data: Dict[str, Any]) -> Optional[GradingCriterion]:
        try:
            return GradingCriterion(
                criterion_id=raw_data.get('criterion_id', ''),
                syllabus_code=raw_data.get('syllabus_code', ''),
                criteria_type=raw_data.get('criteria_type', ''),
                criteria_type_en=raw_data.get('criteria_type_en', ''),
                percentage=raw_data.get('percentage', 0),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        except Exception as e:
            print(f"Error parsing grading criterion data: {e}")
            return None 