from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, TIMESTAMP, Index, CheckConstraint, ForeignKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, List

Base = declarative_base()

# SQLAlchemyモデル
class Subject(Base):
    __tablename__ = 'subject'

    syllabus_code = Column(Text, primary_key=True)
    name = Column(Text, nullable=False)
    class_name = Column(Text, nullable=False)
    subclass_name = Column(Text)
    class_note = Column(Text)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)
    updated_at = Column(TIMESTAMP)

class Syllabus(Base):
    __tablename__ = 'syllabus'

    syllabus_code = Column(Text, primary_key=True)
    year = Column(Integer, primary_key=True)
    subtitle = Column(Text)
    term = Column(String(10), nullable=False)
    grade_b1 = Column(Boolean, nullable=False)
    grade_b2 = Column(Boolean, nullable=False)
    grade_b3 = Column(Boolean, nullable=False)
    grade_b4 = Column(Boolean, nullable=False)
    grade_m1 = Column(Boolean, nullable=False)
    grade_m2 = Column(Boolean, nullable=False)
    grade_d1 = Column(Boolean, nullable=False)
    grade_d2 = Column(Boolean, nullable=False)
    grade_d3 = Column(Boolean, nullable=False)
    campus = Column(Text, nullable=False)
    credits = Column(Integer, nullable=False)
    lecture_code = Column(Text, nullable=False)
    summary = Column(Text)
    goals = Column(Text)
    methods = Column(Text)
    outside_study = Column(Text)
    notes = Column(Text)
    remarks = Column(Text)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)
    updated_at = Column(TIMESTAMP)

    __table_args__ = (
        ForeignKeyConstraint(['syllabus_code'], ['subject.syllabus_code'], ondelete='CASCADE'),
    )

class SyllabusTime(Base):
    __tablename__ = 'syllabus_time'

    id = Column(Integer, primary_key=True)
    syllabus_code = Column(Text, ForeignKey('subject.syllabus_code', ondelete='CASCADE'), nullable=False)
    day_of_week = Column(Integer, nullable=False)
    period = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)

class Instructor(Base):
    __tablename__ = 'instructor'

    instructor_code = Column(Text, primary_key=True)
    last_name = Column(Text, nullable=False)
    first_name = Column(Text, nullable=False)
    last_name_kana = Column(Text)
    first_name_kana = Column(Text)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)
    updated_at = Column(TIMESTAMP)

    __table_args__ = (
        Index('idx_instructor_name', 'last_name', 'first_name'),
        Index('idx_instructor_name_kana', 'last_name_kana', 'first_name_kana'),
    )

class Book(Base):
    __tablename__ = 'book'

    id = Column(Integer, primary_key=True)
    author = Column(Text)
    title = Column(Text, nullable=False)
    publisher = Column(Text)
    price = Column(Integer)
    isbn = Column(String(20))
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)
    updated_at = Column(TIMESTAMP)

    __table_args__ = (
        Index('idx_book_title', 'title'),
        Index('idx_book_author', 'author'),
    )

class SyllabusInstructor(Base):
    __tablename__ = 'syllabus_instructor'

    id = Column(Integer, primary_key=True)
    syllabus_code = Column(Text, ForeignKey('subject.syllabus_code', ondelete='CASCADE'), nullable=False)
    instructor_code = Column(Text, ForeignKey('instructor.instructor_code', ondelete='CASCADE'), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)

    __table_args__ = (
        Index('idx_syllabus_instructor_syllabus', 'syllabus_code'),
        Index('idx_syllabus_instructor_instructor', 'instructor_code'),
    )

class LectureSession(Base):
    __tablename__ = 'lecture_session'

    id = Column(Integer, primary_key=True)
    syllabus_code = Column(Text, ForeignKey('syllabus.syllabus_code', ondelete='CASCADE'), nullable=False)
    day_of_week = Column(Integer, nullable=False)
    period = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)

    __table_args__ = (
        Index('idx_lecture_session_day_period', 'day_of_week', 'period'),
        Index('idx_lecture_session_syllabus', 'syllabus_code'),
    )

class SyllabusBook(Base):
    __tablename__ = 'syllabus_book'

    id = Column(Integer, primary_key=True)
    syllabus_code = Column(Text, ForeignKey('subject.syllabus_code', ondelete='CASCADE'), nullable=False)
    book_id = Column(Integer, ForeignKey('book.id', ondelete='CASCADE'), nullable=False)
    role = Column(Integer, nullable=False)  # 1: 教科書, 2: 参考書
    note = Column(Text)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)

    __table_args__ = (
        Index('idx_syllabus_book_syllabus', 'syllabus_code'),
        Index('idx_syllabus_book_book', 'book_id'),
    )

class GradingCriterion(Base):
    __tablename__ = 'grading_criterion'

    id = Column(Integer, primary_key=True)
    syllabus_code = Column(Text, ForeignKey('syllabus.syllabus_code', ondelete='CASCADE'), nullable=False)
    criteria_type = Column(Text, nullable=False)
    ratio = Column(Integer)
    note = Column(Text)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)

    __table_args__ = (
        Index('idx_grading_criterion_type', 'criteria_type'),
        Index('idx_grading_criterion_syllabus_type', 'syllabus_code', 'criteria_type'),
        CheckConstraint(
            "criteria_type IN ('平常', '小テ', '定期', 'レポ', '他', '自由')",
            name='check_grading_criterion_type_valid'
        ),
    )

class SyllabusFaculty(Base):
    __tablename__ = 'syllabus_faculty'

    id = Column(Integer, primary_key=True)
    syllabus_code = Column(Text, ForeignKey('subject.syllabus_code', ondelete='CASCADE'), nullable=False)
    faculty = Column(String(60), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)

    __table_args__ = (
        Index('idx_syllabus_faculty_syllabus', 'syllabus_code'),
        Index('idx_syllabus_faculty_faculty', 'faculty'),
    )

class Requirement(Base):
    __tablename__ = 'requirement'

    requirement_code = Column(Text, primary_key=True)
    subject_name = Column(Text, nullable=False)
    requirement_type = Column(Text, nullable=False)
    applied_science_available = Column(Boolean, nullable=False)
    graduation_credit_limit = Column(Boolean, nullable=False)
    year_restriction = Column(Boolean, nullable=False)
    first_year_only = Column(Boolean, nullable=False)
    up_to_second_year = Column(Boolean, nullable=False)
    guidance_required = Column(Boolean, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)
    updated_at = Column(TIMESTAMP)

    __table_args__ = (
        Index('idx_requirement_type', 'requirement_type'),
        Index('idx_requirement_restrictions', 'applied_science_available', 'graduation_credit_limit', 'year_restriction'),
    )

class SubjectRequirement(Base):
    __tablename__ = 'subject_requirement'

    id = Column(Integer, primary_key=True)
    syllabus_code = Column(Text, ForeignKey('subject.syllabus_code', ondelete='CASCADE'), nullable=False)
    requirement_code = Column(Text, ForeignKey('requirement.requirement_code', ondelete='CASCADE'), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)

    __table_args__ = (
        Index('idx_subject_requirement_syllabus', 'syllabus_code'),
        Index('idx_subject_requirement_requirement', 'requirement_code'),
    )

class SubjectProgram(Base):
    __tablename__ = 'subject_program'

    id = Column(Integer, primary_key=True)
    syllabus_code = Column(Text, ForeignKey('subject.syllabus_code', ondelete='CASCADE'), nullable=False)
    program_code = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)

    __table_args__ = (
        Index('idx_subject_program_syllabus', 'syllabus_code'),
        Index('idx_subject_program_program', 'program_code'),
    )

# データクラス（JSONシリアライズ用）
@dataclass
class Subject:
    """科目基本情報モデル"""
    syllabus_code: str
    name: str
    class_name: str
    subclass_name: Optional[str]
    class_note: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

@dataclass
class Syllabus:
    """シラバス情報モデル"""
    syllabus_code: str
    year: int
    subtitle: Optional[str]
    term: str
    grade_b1: bool
    grade_b2: bool
    grade_b3: bool
    grade_b4: bool
    grade_m1: bool
    grade_m2: bool
    grade_d1: bool
    grade_d2: bool
    grade_d3: bool
    campus: str
    credits: int
    lecture_code: str
    summary: Optional[str]
    goals: Optional[str]
    methods: Optional[str]
    outside_study: Optional[str]
    notes: Optional[str]
    remarks: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

@dataclass
class SyllabusTime:
    """講義時間モデル"""
    syllabus_code: str
    day_of_week: int
    period: int
    id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class Instructor:
    """教員モデル"""
    instructor_code: str
    last_name: str
    first_name: str
    last_name_kana: Optional[str]
    first_name_kana: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

@dataclass
class Book:
    """書籍モデル"""
    id: int
    author: Optional[str]
    title: str
    publisher: Optional[str]
    price: Optional[int]
    isbn: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

@dataclass
class SyllabusBook:
    """シラバス-書籍関連モデル"""
    id: int
    syllabus_code: str
    book_id: int
    role: int
    note: Optional[str]
    created_at: datetime

@dataclass
class GradingCriterion:
    """成績評価基準モデル"""
    id: int
    syllabus_code: str
    criteria_type: str
    ratio: Optional[int]
    note: Optional[str]
    created_at: datetime

@dataclass
class SyllabusInstructor:
    """シラバス-教員関連モデル"""
    id: int
    syllabus_code: str
    instructor_code: str
    created_at: datetime

@dataclass
class SyllabusFaculty:
    """シラバス-学部/課程関連モデル"""
    id: int
    syllabus_code: str
    faculty: str
    created_at: datetime

@dataclass
class Requirement:
    """科目要件・属性モデル"""
    requirement_code: str
    subject_name: str
    requirement_type: str
    applied_science_available: bool
    graduation_credit_limit: bool
    year_restriction: bool
    first_year_only: bool
    up_to_second_year: bool
    guidance_required: bool
    created_at: datetime
    updated_at: Optional[datetime]

@dataclass
class SubjectRequirement:
    """科目-要綱関連モデル"""
    id: int
    syllabus_code: str
    requirement_code: str
    created_at: datetime

@dataclass
class SubjectProgram:
    """科目-学習プログラム関連モデル"""
    id: int
    syllabus_code: str
    program_code: str
    created_at: datetime 