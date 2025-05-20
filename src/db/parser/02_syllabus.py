from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Syllabus:
    syllabus_code: str
    subject_code: str
    year: int
    term: str
    term_en: str
    course_number: str
    class_number: str
    title: str
    title_en: str
    subtitle: str
    subtitle_en: str
    course_description: str
    course_description_en: str
    course_objectives: str
    course_objectives_en: str
    course_keywords: str
    course_keywords_en: str
    course_notes: str
    course_notes_en: str
    course_url: str
    course_url_en: str
    created_at: datetime
    updated_at: datetime

class SyllabusParser:
    @staticmethod
    def parse(raw_data: Dict[str, Any]) -> Optional[Syllabus]:
        try:
            return Syllabus(
                syllabus_code=raw_data.get('syllabus_code', ''),
                subject_code=raw_data.get('subject_code', ''),
                year=raw_data.get('year', 0),
                term=raw_data.get('term', ''),
                term_en=raw_data.get('term_en', ''),
                course_number=raw_data.get('course_number', ''),
                class_number=raw_data.get('class_number', ''),
                title=raw_data.get('title', ''),
                title_en=raw_data.get('title_en', ''),
                subtitle=raw_data.get('subtitle', ''),
                subtitle_en=raw_data.get('subtitle_en', ''),
                course_description=raw_data.get('course_description', ''),
                course_description_en=raw_data.get('course_description_en', ''),
                course_objectives=raw_data.get('course_objectives', ''),
                course_objectives_en=raw_data.get('course_objectives_en', ''),
                course_keywords=raw_data.get('course_keywords', ''),
                course_keywords_en=raw_data.get('course_keywords_en', ''),
                course_notes=raw_data.get('course_notes', ''),
                course_notes_en=raw_data.get('course_notes_en', ''),
                course_url=raw_data.get('course_url', ''),
                course_url_en=raw_data.get('course_url_en', ''),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        except Exception as e:
            print(f"Error parsing syllabus data: {e}")
            return None 