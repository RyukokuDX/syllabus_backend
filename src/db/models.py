# File Version: v2.1.1
# Project Version: v2.1.2
# Last Updated: 2025-07-01
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, TIMESTAMP, Index, CheckConstraint, ForeignKeyConstraint, UniqueConstraint, SmallInteger, func, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, List

Base = declarative_base()

# SQLAlchemyモデル
class Instructor(Base):
    __tablename__ = 'instructor'

    instructor_id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    name_kana = Column(Text)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)

    __table_args__ = (
        Index('idx_instructor_name', 'name'),
        Index('idx_instructor_name_kana', 'name_kana'),
    )

class SyllabusMaster(Base):
    __tablename__ = 'syllabus_master'

    syllabus_id = Column(Integer, primary_key=True)
    syllabus_code = Column(Text, nullable=False)
    syllabus_year = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)
    updated_at = Column(TIMESTAMP)

    __table_args__ = (
        UniqueConstraint('syllabus_code', 'syllabus_year', name='uix_syllabus_master_code_year'),
        Index('idx_syllabus_master_code', 'syllabus_code'),
        Index('idx_syllabus_master_year', 'syllabus_year'),
    )

    lecture_times = relationship("LectureTime", back_populates="syllabus", cascade="all, delete-orphan")
    source_study_systems = relationship("SyllabusStudySystem", foreign_keys="SyllabusStudySystem.source_syllabus_id", back_populates="source_syllabus")

class Book(Base):
    __tablename__ = 'book'

    book_id = Column(Integer, primary_key=True)
    title = Column(Text, nullable=False)
    author = Column(Text)
    publisher = Column(Text)
    price = Column(Integer)
    isbn = Column(Text)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)

    __table_args__ = (
        Index('idx_book_title', 'title'),
        Index('idx_book_isbn', 'isbn'),
        UniqueConstraint('isbn', name='uix_book_isbn'),
    )

class Class(Base):
    __tablename__ = 'class'

    class_id = Column(Integer, primary_key=True)
    class_name = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)

    __table_args__ = (
        Index('idx_class_name', 'class_name'),
        UniqueConstraint('class_name', name='uix_class_name'),
    )

class Subclass(Base):
    __tablename__ = 'subclass'

    subclass_id = Column(Integer, primary_key=True)
    subclass_name = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)

    __table_args__ = (
        Index('idx_subclass_name', 'subclass_name'),
        UniqueConstraint('subclass_name', name='uix_subclass_name'),
    )

class ClassNote(Base):
    __tablename__ = 'class_note'

    class_note_id = Column(Integer, primary_key=True)
    class_note = Column(Text, nullable=False)

class Faculty(Base):
    __tablename__ = 'faculty'

    faculty_id = Column(Integer, primary_key=True)
    faculty_name = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)

    __table_args__ = (
        Index('idx_faculty_name', 'faculty_name'),
        UniqueConstraint('faculty_name', name='uix_faculty_name'),
    )

    syllabus_enrollment_years = relationship("SyllabusEnrollmentYear", back_populates="faculty", cascade="all, delete-orphan")
    requirement_headers = relationship("RequirementHeaderModel", back_populates="faculty")

class BookUncategorized(Base):
    __tablename__ = 'book_uncategorized'

    id = Column(Integer, primary_key=True)
    syllabus_id = Column(Integer, ForeignKey('syllabus_master.syllabus_id', ondelete='CASCADE'), nullable=False)
    title = Column(Text, nullable=False)
    author = Column(Text)
    publisher = Column(Text)
    price = Column(Integer)
    role = Column(Text, nullable=False)
    isbn = Column(Text)
    categorization_status = Column(Text)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)
    updated_at = Column(TIMESTAMP)

    __table_args__ = (
        Index('idx_book_uncategorized_syllabus', 'syllabus_id'),
        Index('idx_book_uncategorized_title', 'title'),
        Index('idx_book_uncategorized_isbn', 'isbn'),
        Index('idx_book_uncategorized_status', 'categorization_status'),
    )

class BookAuthor(Base):
    __tablename__ = 'book_author'

    book_author_id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('book.book_id', ondelete='CASCADE'), nullable=False)
    author_name = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)

    __table_args__ = (
        Index('idx_book_author_book', 'book_id'),
    )

class SubjectName(Base):
    __tablename__ = 'subject_name'

    subject_name_id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)

    __table_args__ = (
        UniqueConstraint('name', name='uix_subject_name'),
    )

    requirement_headers = relationship("RequirementHeaderModel", back_populates="subject_name")

class Syllabus(Base):
    __tablename__ = 'syllabus'

    syllabus_id = Column(Integer, ForeignKey('syllabus_master.syllabus_id', ondelete='CASCADE'), primary_key=True)
    subject_name_id = Column(Integer, ForeignKey('subject_name.subject_name_id', ondelete='CASCADE'), nullable=False)
    subtitle = Column(Text)
    term = Column(Text, nullable=False)
    campus = Column(Text, nullable=False)
    credits = Column(Integer, nullable=False)
    goals = Column(Text)
    summary = Column(Text)
    attainment = Column(Text)
    methods = Column(Text)
    outside_study = Column(Text)
    textbook_comment = Column(Text)
    reference_comment = Column(Text)
    grading_comment = Column(Text)
    advice = Column(Text)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)
    updated_at = Column(TIMESTAMP)

    __table_args__ = (
        Index('idx_syllabus_term', 'term'),
        Index('idx_syllabus_campus', 'campus'),
        Index('idx_syllabus_subject_name', 'subject_name_id'),
    )

class SubjectGrade(Base):
    __tablename__ = 'subject_grade'

    id = Column(Integer, primary_key=True)
    syllabus_id = Column(Integer, ForeignKey('syllabus_master.syllabus_id', ondelete='CASCADE'), nullable=False)
    grade = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)
    updated_at = Column(TIMESTAMP)

    __table_args__ = (
        UniqueConstraint('syllabus_id', 'grade', name='uix_subject_grade_syllabus_grade'),
        Index('idx_subject_grade_grade', 'grade'),
        Index('idx_subject_grade_syllabus', 'syllabus_id'),
    )

class LectureTime(Base):
    __tablename__ = 'lecture_time'

    id = Column(Integer, primary_key=True)
    syllabus_id = Column(Integer, ForeignKey('syllabus_master.syllabus_id', ondelete='CASCADE'), nullable=False)
    day_of_week = Column(Text, nullable=False)
    period = Column(SmallInteger, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)
    updated_at = Column(TIMESTAMP)

    __table_args__ = (
        UniqueConstraint('syllabus_id', 'day_of_week', 'period', name='uix_lecture_time_syllabus_day_period'),
        Index('idx_lecture_time_day_period', 'day_of_week', 'period'),
        Index('idx_lecture_time_syllabus', 'syllabus_id'),
    )

class LectureSession(Base):
    __tablename__ = 'lecture_session'

    lecture_session_id = Column(Integer, primary_key=True)
    syllabus_id = Column(Integer, ForeignKey('syllabus_master.syllabus_id', ondelete='CASCADE'), nullable=False)
    session_number = Column(Integer, nullable=False)
    contents = Column(Text)
    other_info = Column(Text)
    lecture_format = Column(Text)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)
    updated_at = Column(TIMESTAMP)

    __table_args__ = (
        UniqueConstraint('syllabus_id', 'session_number', name='uix_lecture_session_syllabus_number'),
        Index('idx_lecture_session_syllabus', 'syllabus_id'),
        Index('idx_lecture_session_number', 'session_number'),
    )

class LectureSessionIrregular(Base):
    __tablename__ = 'lecture_session_irregular'

    lecture_session_irregular_id = Column(Integer, primary_key=True)
    syllabus_id = Column(Integer, ForeignKey('syllabus_master.syllabus_id', ondelete='CASCADE'), nullable=False)
    session_pattern = Column(Text, nullable=False)
    contents = Column(Text)
    other_info = Column(Text)
    instructor = Column(Text)
    error_message = Column(Text, nullable=False)
    lecture_format = Column(Text)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)
    updated_at = Column(TIMESTAMP)

    __table_args__ = (
        Index('idx_lecture_session_irregular_syllabus', 'syllabus_id'),
        Index('idx_lecture_session_irregular_pattern', 'session_pattern'),
    )

class SyllabusInstructor(Base):
    __tablename__ = 'syllabus_instructor'

    id = Column(Integer, primary_key=True)
    syllabus_id = Column(Integer, ForeignKey('syllabus_master.syllabus_id', ondelete='CASCADE'), nullable=False)
    instructor_id = Column(Integer, ForeignKey('instructor.instructor_id', ondelete='CASCADE'), nullable=False)
    role = Column(Text)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)
    updated_at = Column(TIMESTAMP)

    __table_args__ = (
        Index('idx_syllabus_instructor_syllabus', 'syllabus_id'),
        Index('idx_syllabus_instructor_instructor', 'instructor_id'),
        UniqueConstraint('syllabus_id', 'instructor_id', name='uix_syllabus_instructor_unique'),
    )

class LectureSessionInstructor(Base):
    __tablename__ = 'lecture_session_instructor'

    id = Column(Integer, primary_key=True)
    lecture_session_id = Column(Integer, ForeignKey('lecture_session.lecture_session_id', ondelete='CASCADE'), nullable=False)
    instructor_id = Column(Integer, ForeignKey('instructor.instructor_id', ondelete='CASCADE'), nullable=False)
    role = Column(Text)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)
    updated_at = Column(TIMESTAMP)

    __table_args__ = (
        Index('idx_lecture_session_instructor_session', 'lecture_session_id'),
        Index('idx_lecture_session_instructor_instructor', 'instructor_id'),
        UniqueConstraint('lecture_session_id', 'instructor_id', name='uix_lecture_session_instructor_unique'),
    )

class SyllabusBook(Base):
    __tablename__ = 'syllabus_book'

    id = Column(Integer, primary_key=True)
    syllabus_id = Column(Integer, ForeignKey('syllabus_master.syllabus_id', ondelete='CASCADE'), nullable=False)
    book_id = Column(Integer, ForeignKey('book.book_id', ondelete='CASCADE'), nullable=False)
    role = Column(Text, nullable=False)
    note = Column(Text)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)

    __table_args__ = (
        Index('idx_syllabus_book_syllabus', 'syllabus_id'),
        Index('idx_syllabus_book_book', 'book_id'),
        UniqueConstraint('syllabus_id', 'book_id', name='uix_syllabus_book_unique'),
    )

class GradingCriterion(Base):
    __tablename__ = 'grading_criterion'

    id = Column(Integer, primary_key=True)
    syllabus_id = Column(Integer, ForeignKey('syllabus_master.syllabus_id', ondelete='CASCADE'), nullable=False)
    criteria_type = Column(Text, nullable=False)
    criteria_description = Column(Text)
    ratio = Column(Integer)
    note = Column(Text)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)

    __table_args__ = (
        Index('idx_grading_criterion_type', 'criteria_type'),
        Index('idx_grading_criterion_syllabus', 'syllabus_id'),
        UniqueConstraint('syllabus_id', 'criteria_type', name='uix_grading_criterion_syllabus_type'),
    )

class SubjectAttribute(Base):
    __tablename__ = 'subject_attribute'

    attribute_id = Column(Integer, primary_key=True)
    attribute_name = Column(Text, nullable=False)
    description = Column(Text)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)

    __table_args__ = (
        UniqueConstraint('attribute_name', name='uix_subject_attribute_name'),
    )

class Subject(Base):
    __tablename__ = 'subject'

    subject_id = Column(Integer, primary_key=True)
    subject_name_id = Column(Integer, ForeignKey('subject_name.subject_name_id', ondelete='RESTRICT'), nullable=False)
    faculty_id = Column(Integer, ForeignKey('faculty.faculty_id', ondelete='RESTRICT'), nullable=False)
    curriculum_year = Column(Integer, nullable=False)
    class_id = Column(Integer, ForeignKey('class.class_id', ondelete='RESTRICT'), nullable=False)
    subclass_id = Column(Integer, ForeignKey('subclass.subclass_id', ondelete='RESTRICT'))
    requirement_type = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)
    updated_at = Column(TIMESTAMP)

    __table_args__ = (
        UniqueConstraint('subject_name_id', 'faculty_id', 'class_id', 'subclass_id', 'curriculum_year', name='idx_subject_unique'),
        Index('idx_subject_subject_name', 'subject_name_id'),
        Index('idx_subject_class', 'class_id'),
        Index('idx_subject_faculty', 'faculty_id'),
        Index('idx_subject_curriculum_year', 'curriculum_year'),
    )

class SubjectAttributeValue(Base):
    __tablename__ = 'subject_attribute_value'

    id = Column(Integer, primary_key=True)
    subject_id = Column(Integer, ForeignKey('subject.subject_id', ondelete='CASCADE'), nullable=False)
    attribute_id = Column(Integer, ForeignKey('subject_attribute.attribute_id', ondelete='RESTRICT'), nullable=False)
    value = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)
    updated_at = Column(TIMESTAMP)

    __table_args__ = (
        UniqueConstraint('subject_id', 'attribute_id', name='uix_subject_attribute_value_unique'),
        Index('idx_subject_attribute_value_subject', 'subject_id'),
        Index('idx_subject_attribute_value_attribute', 'attribute_id'),
    )

class SyllabusFaculty(Base):
    __tablename__ = 'syllabus_faculty'

    id = Column(Integer, primary_key=True)
    syllabus_id = Column(Integer, ForeignKey('syllabus_master.syllabus_id', ondelete='CASCADE'), nullable=False)
    faculty_id = Column(Integer, ForeignKey('faculty.faculty_id', ondelete='CASCADE'), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)
    updated_at = Column(TIMESTAMP)

    __table_args__ = (
        Index('idx_syllabus_faculty_syllabus', 'syllabus_id'),
        Index('idx_syllabus_faculty_faculty', 'faculty_id'),
        UniqueConstraint('syllabus_id', 'faculty_id', name='uix_syllabus_faculty_syllabus_faculty'),
    )

class SyllabusStudySystem(Base):
    __tablename__ = 'syllabus_study_system'

    id = Column(Integer, primary_key=True)
    source_syllabus_id = Column(Integer, ForeignKey('syllabus_master.syllabus_id', ondelete='CASCADE'), nullable=False)
    target = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)
    updated_at = Column(TIMESTAMP)

    __table_args__ = (
        Index('idx_syllabus_study_system_source', 'source_syllabus_id'),
        Index('idx_syllabus_study_system_target', 'target'),
        UniqueConstraint('source_syllabus_id', 'target', name='uix_syllabus_study_system_source_target'),
    )

# データクラス（JSONシリアライズ用）
@dataclass
class Class:
    """科目区分モデル"""
    class_id: int
    class_name: str
    created_at: datetime

@dataclass
class Subclass:
    """科目小区分モデル"""
    subclass_id: int
    subclass_name: str
    created_at: datetime

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
    created_at: datetime

@dataclass
class Instructor:
    """教員モデル"""
    instructor_id: int
    name: str
    name_kana: Optional[str]
    created_at: datetime

@dataclass
class Book:
    """書籍モデル"""
    book_id: int
    title: str
    author: Optional[str]
    publisher: Optional[str]
    price: Optional[int]
    isbn: Optional[str]
    created_at: datetime

@dataclass
class BookAuthor:
    """書籍著者モデル"""
    book_author_id: int
    book_id: int
    author_name: str
    created_at: datetime

@dataclass
class SubjectName:
    """科目名マスタモデル"""
    subject_name_id: int
    name: str
    created_at: datetime

@dataclass
class SyllabusMaster:
    """シラバスマスタモデル"""
    syllabus_id: int
    syllabus_code: str
    syllabus_year: int
    created_at: datetime
    updated_at: Optional[datetime] = None

@dataclass
class Syllabus:
    """シラバス情報モデル"""
    syllabus_id: int
    subject_name_id: int
    subtitle: Optional[str]
    term: str
    campus: str
    credits: int
    goals: Optional[str]
    summary: Optional[str]
    attainment: Optional[str]
    methods: Optional[str]
    outside_study: Optional[str]
    textbook_comment: Optional[str]
    reference_comment: Optional[str]
    grading_comment: Optional[str]
    advice: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime] = None

@dataclass
class SubjectGrade:
    """科目履修可能学年モデル"""
    id: int
    syllabus_id: int
    grade: str
    created_at: datetime
    updated_at: Optional[datetime] = None

@dataclass
class LectureTime:
    """講義時間モデル"""
    id: int
    syllabus_id: int
    day_of_week: str
    period: int
    created_at: datetime
    updated_at: Optional[datetime] = None

@dataclass
class LectureSession:
    """講義回数モデル"""
    lecture_session_id: int
    syllabus_id: int
    session_number: int
    contents: Optional[str]
    other_info: Optional[str]
    lecture_format: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime] = None

@dataclass
class SyllabusInstructor:
    """シラバス教員関連モデル"""
    id: int
    syllabus_id: int
    instructor_id: int
    role: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime] = None

@dataclass
class LectureSessionInstructor:
    """講義回数担当者モデル"""
    id: int
    lecture_session_id: int
    instructor_id: int
    role: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime] = None

@dataclass
class LectureSessionIrregular:
    """不定形講義回数モデル"""
    lecture_session_irregular_id: int
    syllabus_id: int
    session_pattern: str
    contents: Optional[str]
    other_info: Optional[str]
    instructor: Optional[str]
    error_message: str
    lecture_format: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime] = None

@dataclass
class SyllabusBook:
    """シラバス教科書関連モデル"""
    id: int
    syllabus_id: int
    book_id: int
    role: str
    note: Optional[str]
    created_at: datetime

@dataclass
class GradingCriterion:
    """成績評価基準モデル"""
    id: int
    syllabus_id: int
    criteria_type: str
    criteria_description: Optional[str]
    ratio: Optional[int]
    note: Optional[str]
    created_at: datetime

@dataclass
class SubjectAttribute:
    """科目属性モデル"""
    attribute_id: int
    attribute_name: str
    description: Optional[str]
    created_at: datetime

@dataclass
class Subject:
    """科目基本情報モデル"""
    subject_id: int
    subject_name_id: int
    faculty_id: int
    curriculum_year: int
    class_id: int
    subclass_id: Optional[int]
    requirement_type: str
    created_at: datetime
    updated_at: Optional[datetime] = None

@dataclass
class SyllabusFaculty:
    """シラバス学部関連モデル"""
    id: int
    syllabus_id: int
    faculty_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

@dataclass
class SyllabusStudySystem:
    """シラバス系統的履修モデル"""
    id: int
    source_syllabus_id: int
    target: str
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