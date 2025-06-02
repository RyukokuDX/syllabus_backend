from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, TIMESTAMP, Index, CheckConstraint, ForeignKeyConstraint, UniqueConstraint, SmallInteger, func, text
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
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)

class Subclass(Base):
    __tablename__ = 'subclass'

    subclass_id = Column(Integer, primary_key=True)
    subclass_name = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)

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
    )

    syllabus_enrollment_years = relationship("SyllabusEnrollmentYear", back_populates="faculty", cascade="all, delete-orphan")
    requirement_headers = relationship("RequirementHeaderModel", back_populates="faculty")

class SubjectName(Base):
    __tablename__ = 'subject_name'

    subject_name_id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)

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

    subject_id = Column(Integer, primary_key=True)
    subject_name_id = Column(Integer, ForeignKey('subject_name.subject_name_id'), nullable=False)
    faculty_id = Column(Integer, ForeignKey('faculty.faculty_id'), nullable=False)
    class_id = Column(Integer, ForeignKey('class.class_id'), nullable=False)
    subclass_id = Column(Integer, ForeignKey('subclass.subclass_id'), nullable=True)
    curriculum_year = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=True, onupdate=func.now())

    __table_args__ = (
        UniqueConstraint(
            "subject_name_id",
            "faculty_id",
            "class_id",
            "subclass_id",
            "curriculum_year",
            name="idx_subject_unique",
        ),
        Index("idx_subject_subject_name", "subject_name_id"),
        Index("idx_subject_class", "class_id"),
        Index("idx_subject_faculty", "faculty_id"),
        Index("idx_subject_curriculum_year", "curriculum_year"),
    )

class SubjectSyllabus(Base):
    __tablename__ = 'subject_syllabus'

    id = Column(Integer, primary_key=True)
    subject_id = Column(Integer, ForeignKey('subject.subject_id', ondelete='CASCADE'), nullable=False)
    syllabus_code = Column(Text, ForeignKey('syllabus.syllabus_code', ondelete='RESTRICT'), nullable=False)
    syllabus_year = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)
    updated_at = Column(TIMESTAMP)

    __table_args__ = (
        Index('idx_subject_syllabus_unique', 'subject_id', 'syllabus_year', unique=True),
        Index('idx_subject_syllabus_subject', 'subject_id'),
        Index('idx_subject_syllabus_syllabus', 'syllabus_code'),
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

class SubjectAttributeValue(Base):
    __tablename__ = 'subject_attribute_value'

    id = Column(Integer, primary_key=True)
    subject_id = Column(Integer, ForeignKey('subject.subject_id', ondelete='CASCADE'), nullable=False)
    attribute_id = Column(Integer, ForeignKey('subject_attribute.attribute_id', ondelete='RESTRICT'), nullable=False)
    value = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)
    updated_at = Column(TIMESTAMP)

    __table_args__ = (
        Index('idx_subject_attribute_value_unique', 'subject_id', 'attribute_id', unique=True),
        Index('idx_subject_attribute_value_subject', 'subject_id'),
        Index('idx_subject_attribute_value_attribute', 'attribute_id'),
    )

class Instructor(Base):
    __tablename__ = 'instructor'

    instructor_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)  # 名前 (漢字かカナ)
    name_kana = Column(String)  # 名前（カナ）
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))

    __table_args__ = (
        Index('idx_instructor_name', 'name'),
        Index('idx_instructor_name_kana', 'name_kana'),
    )

class Book(Base):
    __tablename__ = 'book'

    book_id = Column(Integer, primary_key=True)
    title = Column(Text, nullable=False)
    publisher = Column(Text)
    price = Column(Integer)
    isbn = Column(Text)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)

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

class LectureTime(Base):
    __tablename__ = 'lecture_time'

    id = Column(Integer, primary_key=True)
    syllabus_id = Column(Integer, ForeignKey('syllabus_master.syllabus_id', ondelete='CASCADE'), nullable=False)
    day_of_week = Column(Text, nullable=False)
    period = Column(SmallInteger, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # インデックス
    __table_args__ = (
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
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # インデックス
    __table_args__ = (
        Index('idx_lecture_session_syllabus', 'syllabus_id'),
        Index('idx_lecture_session_number', 'session_number'),
    )

class LectureSessionInstructor(Base):
    __tablename__ = 'lecture_session_instructor'

    id = Column(Integer, primary_key=True)
    lecture_session_id = Column(Integer, ForeignKey('lecture_session.lecture_session_id', ondelete='CASCADE'), nullable=False)
    instructor_id = Column(Integer, ForeignKey('instructor.instructor_id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # インデックス
    __table_args__ = (
        Index('idx_lecture_session_instructor_session', 'lecture_session_id'),
        Index('idx_lecture_session_instructor_instructor', 'instructor_id'),
    )

class SyllabusInstructor(Base):
    __tablename__ = 'syllabus_instructor'

    id = Column(Integer, primary_key=True)
    syllabus_code = Column(Text, ForeignKey('syllabus.syllabus_code', ondelete='CASCADE'), nullable=False)
    instructor_id = Column(Integer, ForeignKey('instructor.instructor_id', ondelete='CASCADE'), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)

    __table_args__ = (
        Index('idx_syllabus_instructor_syllabus', 'syllabus_code'),
        Index('idx_syllabus_instructor_instructor', 'instructor_id'),
    )

class SyllabusBook(Base):
    __tablename__ = 'syllabus_book'

    id = Column(Integer, primary_key=True)
    syllabus_code = Column(Text, ForeignKey('syllabus.syllabus_code', ondelete='CASCADE'), nullable=False)
    book_id = Column(Integer, ForeignKey('book.book_id', ondelete='CASCADE'), nullable=False)
    role = Column(Text, nullable=False)  # 教科書, 参考書
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
class SubjectName:
    """科目名マスタモデル"""
    subject_name_id: int
    name: str
    created_at: datetime

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
    subject_name_id: int
    faculty_id: int
    class_id: int
    subclass_id: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]

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
    instructor_id: int
    created_at: datetime

@dataclass
class SyllabusBook:
    """シラバス-書籍関連モデル"""
    id: int
    syllabus_code: str
    book_id: int
    role: str
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

class SyllabusStudySystem(Base):
    __tablename__ = 'syllabus_study_system'

    id = Column(Integer, primary_key=True)
    source_syllabus_id = Column(Integer, ForeignKey('syllabus_master.syllabus_id', ondelete='CASCADE'), nullable=False)
    target = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)
    updated_at = Column(TIMESTAMP)

    __table_args__ = (
        UniqueConstraint('source_syllabus_id', 'target', name='uix_syllabus_study_system_source_target'),
        Index('idx_syllabus_study_system_source', 'source_syllabus_id'),
        Index('idx_syllabus_study_system_target', 'target'),
    )

    source_syllabus = relationship("SyllabusMaster", foreign_keys=[source_syllabus_id], back_populates="source_study_systems")

@dataclass
class SyllabusStudySystemData:
    """シラバス系統的履修モデル"""
    id: int
    source_syllabus_id: int
    target: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    source_syllabus: Optional[SyllabusData] = None  # Web Syllabusの情報 