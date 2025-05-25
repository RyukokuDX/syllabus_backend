from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, TIMESTAMP, Index, CheckConstraint, ForeignKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, List

Base = declarative_base()

# SQLAlchemyモデル
class Class(Base):
    __tablename__ = 'class'

    class_id = Column(Integer, primary_key=True)
    class_name = Column(Text, nullable=False)

class Subclass(Base):
    __tablename__ = 'subclass'

    subclass_id = Column(Integer, primary_key=True)
    subclass_name = Column(Text, nullable=False)

class ClassNote(Base):
    __tablename__ = 'class_note'

    class_note_id = Column(Integer, primary_key=True)
    class_note = Column(Text, nullable=False)

class Faculty(Base):
    __tablename__ = 'faculty'

    faculty_id = Column(Integer, primary_key=True)
    faculty_name = Column(Text, nullable=False)

    __table_args__ = (
        Index('idx_faculty_name', 'faculty_name'),
    )

class SubjectName(Base):
    __tablename__ = 'subject_name'

    subject_name_id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)

    __table_args__ = (
        Index('idx_subject_name', 'name', unique=True),
    )

class Syllabus(Base):
    __tablename__ = 'syllabus'

    syllabus_code = Column(String, primary_key=True)
    subject_name_id = Column(Integer, ForeignKey("subject_name.subject_name_id", ondelete="RESTRICT"), nullable=False)
    subtitle = Column(String)
    term = Column(String, nullable=False)
    campus = Column(String, nullable=False)
    credits = Column(Integer, nullable=False)
    summary = Column(String)
    goals = Column(String)
    methods = Column(String)
    outside_study = Column(String)
    notes = Column(String)
    remarks = Column(String)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.now)

    # インデックス
    __table_args__ = (
        Index("idx_syllabus_term", "term"),
        Index("idx_syllabus_campus", "campus"),
        Index("idx_syllabus_subject_name", "subject_name_id"),
    )

    # リレーション
    subject_name = relationship("SubjectName", back_populates="syllabi")
    subjects = relationship("Subject", back_populates="syllabus")
    lecture_sessions = relationship("LectureSession", back_populates="syllabus", cascade="all, delete-orphan")
    syllabus_faculties = relationship("SyllabusFaculty", back_populates="syllabus", cascade="all, delete-orphan")
    syllabus_instructors = relationship("SyllabusInstructor", back_populates="syllabus", cascade="all, delete-orphan")
    syllabus_books = relationship("SyllabusBook", back_populates="syllabus", cascade="all, delete-orphan")
    grading_criteria = relationship("GradingCriterion", back_populates="syllabus", cascade="all, delete-orphan")
    syllabus_eligible_grades = relationship("SyllabusEligibleGrade", back_populates="syllabus", cascade="all, delete-orphan")
    syllabus_enrollment_years = relationship("SyllabusEnrollmentYear", back_populates="syllabus", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Syllabus(syllabus_code='{self.syllabus_code}', term='{self.term}')>"

    @property
    def available_grades(self) -> List[str]:
        """履修可能学年のリストを返す"""
        return [grade.grade for grade in self.syllabus_eligible_grades]

class Subject(Base):
    __tablename__ = 'subject'

    subject_id = Column(Integer, primary_key=True)
    syllabus_code = Column(Text, ForeignKey('syllabus.syllabus_code'), nullable=False)
    syllabus_year = Column(Integer, nullable=False)
    faculty_id = Column(Integer, ForeignKey('faculty.faculty_id'), nullable=False)
    class_id = Column(Integer, ForeignKey('class.class_id'), nullable=False)
    subclass_id = Column(Integer, ForeignKey('subclass.subclass_id'))
    class_note_id = Column(Integer, ForeignKey('class_note.class_note_id'))
    lecture_code = Column(Text)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)
    updated_at = Column(TIMESTAMP)

    __table_args__ = (
        Index('idx_subject_syllabus', 'syllabus_code'),
        Index('idx_subject_class', 'class_id'),
        Index('idx_subject_faculty', 'faculty_id'),
        Index('idx_subject_unique', 'syllabus_code', 'syllabus_year', 'faculty_id', 'class_id', 'subclass_id', 'class_note_id', unique=True),
    )

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

    book_id = Column(Integer, primary_key=True)
    title = Column(Text, nullable=False)
    publisher = Column(Text)
    price = Column(Integer)
    isbn = Column(Text)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)
    updated_at = Column(TIMESTAMP)

    __table_args__ = (
        Index('idx_book_title', 'title'),
        Index('idx_book_isbn', 'isbn', unique=True),
    )

class BookAuthor(Base):
    __tablename__ = 'book_author'

    book_author_id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('book.book_id', ondelete='CASCADE'), nullable=False)
    author_name = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)

    __table_args__ = (
        Index('idx_book_author_book', 'book_id'),
        Index('idx_book_author_name', 'author_name'),
    )

class LectureSession(Base):
    __tablename__ = 'lecture_session'

    id = Column(Integer, primary_key=True)
    syllabus_code = Column(Text, ForeignKey('syllabus.syllabus_code', ondelete='CASCADE'), nullable=False)
    syllabus_year = Column(Integer, nullable=False)
    day_of_week = Column(Text, nullable=False)
    period = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)
    updated_at = Column(TIMESTAMP)

    __table_args__ = (
        Index('idx_lecture_session_day_period', 'day_of_week', 'period'),
        Index('idx_lecture_session_syllabus', 'syllabus_code', 'syllabus_year'),
    )

class SyllabusFaculty(Base):
    __tablename__ = 'syllabus_faculty'

    id = Column(Integer, primary_key=True)
    syllabus_code = Column(Text, ForeignKey('syllabus.syllabus_code', ondelete='CASCADE'), nullable=False)
    faculty_id = Column(Integer, ForeignKey('faculty.faculty_id', ondelete='CASCADE'), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)

    __table_args__ = (
        Index('idx_syllabus_faculty_syllabus', 'syllabus_code'),
        Index('idx_syllabus_faculty_faculty', 'faculty_id'),
    )

class SyllabusInstructor(Base):
    __tablename__ = 'syllabus_instructor'

    id = Column(Integer, primary_key=True)
    syllabus_code = Column(Text, ForeignKey('syllabus.syllabus_code', ondelete='CASCADE'), nullable=False)
    instructor_code = Column(Text, ForeignKey('instructor.instructor_code', ondelete='CASCADE'), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)

    __table_args__ = (
        Index('idx_syllabus_instructor_syllabus', 'syllabus_code'),
        Index('idx_syllabus_instructor_instructor', 'instructor_code'),
    )

class SyllabusBook(Base):
    __tablename__ = 'syllabus_book'

    id = Column(Integer, primary_key=True)
    syllabus_code = Column(Text, ForeignKey('syllabus.syllabus_code', ondelete='CASCADE'), nullable=False)
    book_id = Column(Integer, ForeignKey('book.book_id', ondelete='CASCADE'), nullable=False)
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
        Index('idx_grading_criterion_syllabus', 'syllabus_code'),
    )

class Program(Base):
    __tablename__ = 'program'

    program_id = Column(Integer, primary_key=True)
    program_name = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)
    updated_at = Column(TIMESTAMP)

    __table_args__ = (
        Index('idx_program_name', 'program_name'),
    )

class Requirement(Base):
    __tablename__ = 'requirement'

    requirement_id = Column(Integer, primary_key=True)
    requirement_year = Column(Integer, nullable=False)
    faculty_id = Column(Integer, ForeignKey('faculty.faculty_id'), nullable=False)
    subject_name_id = Column(Integer, ForeignKey('subject_name.subject_name_id'), nullable=False)
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
        Index('idx_requirement_subject', 'subject_name_id'),
    )

class SubjectProgram(Base):
    __tablename__ = 'subject_program'

    id = Column(Integer, primary_key=True)
    requirement_id = Column(Integer, ForeignKey('requirement.requirement_id', ondelete='CASCADE'), nullable=False)
    program_id = Column(Integer, ForeignKey('program.program_id', ondelete='CASCADE'), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)

    __table_args__ = (
        Index('idx_subject_program_requirement', 'requirement_id'),
        Index('idx_subject_program_program', 'program_id'),
    )

class SyllabusEligibleGrade(Base):
    __tablename__ = 'syllabus_eligible_grade'

    id = Column(Integer, primary_key=True)
    syllabus_code = Column(Text, ForeignKey('syllabus.syllabus_code', ondelete='CASCADE'), nullable=False)
    syllabus_year = Column(Integer, nullable=False)
    grade = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)
    updated_at = Column(TIMESTAMP)

    __table_args__ = (
        Index('idx_syllabus_eligible_grade_syllabus', 'syllabus_code'),
        Index('idx_syllabus_eligible_grade_unique', 'syllabus_code', 'syllabus_year', 'grade', unique=True),
    )

    syllabus = relationship("Syllabus", back_populates="syllabus_eligible_grades")

class SyllabusEnrollmentYear(Base):
    __tablename__ = 'syllabus_enrollment_year'

    id = Column(Integer, primary_key=True)
    syllabus_code = Column(Text, ForeignKey('syllabus.syllabus_code', ondelete='CASCADE'), nullable=False)
    enrollment_year = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)

    __table_args__ = (
        Index('idx_syllabus_enrollment_year_syllabus', 'syllabus_code'),
        Index('idx_syllabus_enrollment_year_unique', 'syllabus_code', 'enrollment_year', unique=True),
    )

    syllabus = relationship("Syllabus", back_populates="syllabus_enrollment_years")

# データクラス（JSONシリアライズ用）
@dataclass
class Class:
    """科目区分モデル"""
    class_id: int
    class_name: str

@dataclass
class Subclass:
    """科目小区分モデル"""
    subclass_id: int
    subclass_name: str

@dataclass
class ClassNote:
    """科目区分の備考モデル"""
    class_note_id: int
    class_note: str

@dataclass
class Faculty:
    """開講学部・課程モデル"""
    faculty_id: int
    faculty_name: str

@dataclass
class SubjectName:
    """科目名マスタモデル"""
    subject_name_id: int
    name: str

@dataclass
class SyllabusData:
    syllabus_code: str
    subject_name_id: int
    subtitle: Optional[str]
    term: str
    campus: str
    credits: int
    summary: Optional[str]
    goals: Optional[str]
    methods: Optional[str]
    outside_study: Optional[str]
    notes: Optional[str]
    remarks: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    grades: List[str] = field(default_factory=list)

    @property
    def available_grades(self) -> List[str]:
        """履修可能学年のリストを返す"""
        return self.grades

@dataclass
class Subject:
    """科目基本情報モデル"""
    subject_id: int
    syllabus_code: str
    syllabus_year: int
    faculty_id: int
    class_id: int
    subclass_id: Optional[int]
    class_note_id: Optional[int]
    lecture_code: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

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
    book_id: int
    title: str
    publisher: Optional[str]
    price: Optional[int]
    isbn: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

@dataclass
class BookAuthor:
    """書籍著者モデル"""
    book_author_id: int
    book_id: int
    author_name: str
    created_at: datetime

@dataclass
class LectureSession:
    """講義時間モデル"""
    id: int
    syllabus_code: str
    syllabus_year: int
    day_of_week: str
    period: int
    created_at: datetime
    updated_at: Optional[datetime]

@dataclass
class SyllabusFaculty:
    """シラバス-学部課程関連モデル"""
    id: int
    syllabus_code: str
    faculty_id: int
    created_at: datetime

@dataclass
class SyllabusInstructor:
    """シラバス-教員関連モデル"""
    id: int
    syllabus_code: str
    instructor_code: str
    created_at: datetime

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
class Program:
    """学修プログラムモデル"""
    program_id: int
    program_name: str
    created_at: datetime
    updated_at: Optional[datetime]

@dataclass
class Requirement:
    """科目要件属性モデル"""
    requirement_id: int
    requirement_year: int
    faculty_id: int
    subject_name_id: int
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
class SubjectProgram:
    """科目-学習プログラム関連モデル"""
    id: int
    requirement_id: int
    program_id: int
    created_at: datetime

@dataclass
class SyllabusEligibleGrade:
    """シラバス履修可能学年モデル"""
    id: int
    syllabus_code: str
    syllabus_year: int
    grade: str
    created_at: datetime
    updated_at: Optional[datetime]

@dataclass
class SyllabusEnrollmentYear:
    """シラバス入学年度制限モデル"""
    id: int
    syllabus_code: str
    enrollment_year: int
    created_at: datetime 