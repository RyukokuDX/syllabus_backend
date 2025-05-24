from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.sql import func

class SyllabusGrade(Base):
    """シラバス履修可能学年"""
    __tablename__ = 'syllabus_grade'

    id = Column(Integer, primary_key=True)
    syllabus_code = Column(Text, ForeignKey('subject.syllabus_code', ondelete='CASCADE'), nullable=False)
    syllabus_year = Column(Integer, ForeignKey('subject.syllabus_year', ondelete='CASCADE'), nullable=False)
    grade = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())

    __table_args__ = (
        UniqueConstraint('syllabus_code', 'syllabus_year', 'grade', name='uix_syllabus_grade'),
        Index('idx_syllabus_grade_syllabus', 'syllabus_code', 'syllabus_year'),
        Index('idx_syllabus_grade_grade', 'grade'),
    )

    def __repr__(self):
        return f"<SyllabusGrade(syllabus_code='{self.syllabus_code}', syllabus_year='{self.syllabus_year}', grade='{self.grade}')>" 