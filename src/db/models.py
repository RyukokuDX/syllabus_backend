from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, TIMESTAMP, Index, CheckConstraint, ForeignKeyConstraint, UniqueConstraint
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

    syllabus_enrollment_years = relationship("SyllabusEnrollmentYear", back_populates="faculty", cascade="all, delete-orphan")
    requirement_headers = relationship("RequirementHeaderModel", back_populates="faculty")

class SubjectName(Base):
    __tablename__ = 'subject_name'

    subject_name_id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)

    __table_args__ = (
        Index('idx_subject_name', 'name', unique=True),
    )

    requirement_headers = relationship("RequirementHeaderModel", back_populates="subject_name")

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
    syllabus_instructors = relationship("SyllabusInstructor", back_populates="syllabus", cascade="all, delete-orphan")
    syllabus_books = relationship("SyllabusBook", back_populates="syllabus", cascade="all, delete-orphan")
    grading_criteria = relationship("GradingCriterion", back_populates="syllabus", cascade="all, delete-orphan")
    syllabus_eligible_grades = relationship("SyllabusEligibleGrade", back_populates="syllabus", cascade="all, delete-orphan")
    syllabus_faculty_enrollments = relationship("SyllabusFacultyEnrollment", back_populates="syllabus", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Syllabus(syllabus_code='{self.syllabus_code}', term='{self.term}')>"

    @property
    def available_grades(self) -> List[str]:
        """履修可能学年のリストを返す"""
        return [grade.grade for grade in self.syllabus_eligible_grades]

class Subject(Base):
    __tablename__ = 'subject'

    id = Column(Integer, primary_key=True)
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

class SyllabusEnrollmentYear(Base):
    __tablename__ = 'syllabus_enrollment_year'

    id = Column(Integer, primary_key=True)
    syllabus_code = Column(Text, ForeignKey('syllabus.syllabus_code', ondelete='CASCADE'), nullable=False)
    enrollment_year = Column(Integer, nullable=False)
    syllabus_year = Column(Integer, nullable=False)
    faculty_id = Column(Integer, ForeignKey('faculty.faculty_id', ondelete='CASCADE'), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)

    __table_args__ = (
        Index('idx_syllabus_enrollment_year_syllabus', 'syllabus_code'),
        Index('idx_syllabus_enrollment_year_faculty', 'faculty_id'),
        Index('idx_syllabus_enrollment_year_syllabus_year', 'syllabus_year'),
        Index('idx_syllabus_enrollment_year_unique', 'syllabus_code', 'enrollment_year', 'syllabus_year', 'faculty_id', unique=True),
    )

    syllabus = relationship("Syllabus", back_populates="syllabus_enrollment_years")
    faculty = relationship("Faculty", back_populates="syllabus_enrollment_years")

class SyllabusFacultyEnrollment(Base):
    __tablename__ = 'syllabus_faculty_enrollment'

    id = Column(Integer, primary_key=True)
    syllabus_code = Column(Text, ForeignKey('syllabus.syllabus_code', ondelete='CASCADE'), nullable=False)
    enrollment_year = Column(Integer, nullable=False)
    syllabus_year = Column(Integer, nullable=False)
    faculty_id = Column(Integer, ForeignKey('faculty.faculty_id', ondelete='CASCADE'), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)

    __table_args__ = (
        Index('idx_syllabus_faculty_enrollment_syllabus', 'syllabus_code'),
        Index('idx_syllabus_faculty_enrollment_faculty', 'faculty_id'),
        Index('idx_syllabus_faculty_enrollment_syllabus_year', 'syllabus_year'),
        Index('idx_syllabus_faculty_enrollment_unique', 'syllabus_code', 'enrollment_year', 'syllabus_year', 'faculty_id', unique=True),
    )

    syllabus = relationship("Syllabus", back_populates="syllabus_faculty_enrollments")
    faculty = relationship("Faculty", back_populates="syllabus_faculty_enrollments")

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
    id: int
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
class RequirementHeader:
    requirement_header_id: int
    requirement_year: int
    faculty_id: int
    subject_name_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

class RequirementHeaderModel(Base):
    __tablename__ = "requirement_header"

    requirement_header_id = Column(Integer, primary_key=True)
    requirement_year = Column(Integer, nullable=False)
    faculty_id = Column(Integer, ForeignKey("faculty.faculty_id"), nullable=False)
    subject_name_id = Column(Integer, ForeignKey("subject_name.subject_name_id"), nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=True)

    # 一意制約
    __table_args__ = (
        UniqueConstraint("requirement_year", "faculty_id", "subject_name_id", name="uix_requirement_header_unique"),
        Index("idx_requirement_header_faculty", "faculty_id"),
        Index("idx_requirement_header_subject", "subject_name_id"),
    )

    # リレーションシップ
    faculty = relationship("Faculty", back_populates="requirement_headers")
    subject_name = relationship("SubjectName", back_populates="requirement_headers")
    requirements = relationship("RequirementModel", back_populates="requirement_header", cascade="all, delete-orphan")

@dataclass
class RequirementAttribute:
    requirement_attribute_id: int
    name: str
    created_at: datetime

class RequirementAttributeModel(Base):
    __tablename__ = "requirement_attribute"

    requirement_attribute_id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False)

    # 一意制約
    __table_args__ = (
        UniqueConstraint("name", name="uix_requirement_attribute_name"),
    )

    # リレーションシップ
    requirements = relationship("RequirementModel", back_populates="requirement_attribute")

@dataclass
class Requirement:
    requirement_id: int
    requirement_header_id: int
    requirement_attribute_id: int
    text: str
    created_at: datetime
    updated_at: Optional[datetime] = None

class RequirementModel(Base):
    __tablename__ = "requirement"

    requirement_id = Column(Integer, primary_key=True)
    requirement_header_id = Column(Integer, ForeignKey("requirement_header.requirement_header_id"), nullable=False)
    requirement_attribute_id = Column(Integer, ForeignKey("requirement_attribute.requirement_attribute_id"), nullable=False)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=True)

    # インデックス
    __table_args__ = (
        Index("idx_requirement_header", "requirement_header_id"),
        Index("idx_requirement_attribute", "requirement_attribute_id"),
    )

    # リレーションシップ
    requirement_header = relationship("RequirementHeaderModel", back_populates="requirements")
    requirement_attribute = relationship("RequirementAttributeModel", back_populates="requirements") 