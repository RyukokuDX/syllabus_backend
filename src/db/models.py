from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, TIMESTAMP, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Subject(Base):
    __tablename__ = 'subject'

    subject_code = Column(Text, primary_key=True)
    name = Column(Text, nullable=False)
    class_name = Column(Text, nullable=False)
    subclass_name = Column(Text)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)
    updated_at = Column(TIMESTAMP)

    __table_args__ = (
        Index('idx_subject_name', name),
        Index('idx_subject_class', class_name),
    )

class Syllabus(Base):
    __tablename__ = 'syllabus'

    subject_code = Column(Text, ForeignKey('subject.subject_code', ondelete='CASCADE'), primary_key=True)
    year = Column(Integer, nullable=False)
    subtitle = Column(Text)
    term = Column(Text, nullable=False)
    grade_b1 = Column(Boolean, nullable=False)
    grade_b2 = Column(Boolean, nullable=False)
    grade_b3 = Column(Boolean, nullable=False)
    grade_b4 = Column(Boolean, nullable=False)
    grade_m1 = Column(Boolean, nullable=False)
    grade_m2 = Column(Boolean, nullable=False)
    grade_d1 = Column(Boolean, nullable=False)
    grade_d2 = Column(Boolean, nullable=False)
    grade_d3 = Column(Boolean, nullable=False)
    campus = Column(String(6), nullable=False)
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
        Index('idx_syllabus_year', year),
        Index('idx_syllabus_term', term),
        Index('idx_syllabus_grades', grade_b1, grade_b2, grade_b3, grade_b4, 
              grade_m1, grade_m2, grade_d1, grade_d2, grade_d3),
        Index('idx_syllabus_campus', campus),
    )

class SyllabusTime(Base):
    __tablename__ = 'syllabus_time'

    id = Column(Integer, primary_key=True)
    subject_code = Column(Text, ForeignKey('subject.subject_code', ondelete='CASCADE'), nullable=False)
    day_of_week = Column(Text, nullable=False)
    period = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)

    __table_args__ = (
        Index('idx_syllabus_time_day_period', day_of_week, period),
        Index('idx_syllabus_time_subject', subject_code),
    )

class Instructor(Base):
    __tablename__ = 'instructor'

    instructor_code = Column(Text, primary_key=True)
    name = Column(Text, nullable=False)
    name_kana = Column(Text)
    name_en = Column(Text)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)
    updated_at = Column(TIMESTAMP)

    __table_args__ = (
        Index('idx_instructor_name', name),
        Index('idx_instructor_name_kana', name_kana),
    )

class SyllabusInstructor(Base):
    __tablename__ = 'syllabus_instructor'

    id = Column(Integer, primary_key=True)
    subject_code = Column(Text, ForeignKey('subject.subject_code', ondelete='CASCADE'), nullable=False)
    instructor_code = Column(Text, ForeignKey('instructor.instructor_code', ondelete='CASCADE'), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)

class LectureSession(Base):
    __tablename__ = 'lecture_session'

    id = Column(Integer, primary_key=True)
    subject_code = Column(Text, ForeignKey('subject.subject_code', ondelete='CASCADE'), nullable=False)
    session_number = Column(Integer, nullable=False)
    description = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)

class Book(Base):
    __tablename__ = 'book'

    id = Column(Integer, primary_key=True)
    author = Column(Text)
    title = Column(Text, nullable=False)
    publisher = Column(Text)
    price = Column(Integer)
    isbn = Column(Text, unique=True)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)
    updated_at = Column(TIMESTAMP)

class SyllabusTextbook(Base):
    __tablename__ = 'syllabus_textbook'

    id = Column(Integer, primary_key=True)
    subject_code = Column(Text, ForeignKey('subject.subject_code', ondelete='CASCADE'), nullable=False)
    book_id = Column(Integer, ForeignKey('book.id', ondelete='CASCADE'), nullable=False)
    note = Column(Text)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)

class SyllabusReference(Base):
    __tablename__ = 'syllabus_reference'

    id = Column(Integer, primary_key=True)
    subject_code = Column(Text, ForeignKey('subject.subject_code', ondelete='CASCADE'), nullable=False)
    book_id = Column(Integer, ForeignKey('book.id', ondelete='CASCADE'), nullable=False)
    note = Column(Text)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)

class GradingCriterion(Base):
    __tablename__ = 'grading_criterion'

    id = Column(Integer, primary_key=True)
    subject_code = Column(Text, ForeignKey('subject.subject_code', ondelete='CASCADE'), nullable=False)
    criteria_type = Column(String(4), nullable=False)
    ratio = Column(Integer)
    note = Column(Text)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)

class SyllabusFaculty(Base):
    __tablename__ = 'syllabus_faculty'

    id = Column(Integer, primary_key=True)
    subject_code = Column(Text, ForeignKey('subject.subject_code', ondelete='CASCADE'), nullable=False)
    faculty = Column(String(60), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)

class SubjectRequirement(Base):
    __tablename__ = 'subject_requirement'

    subject_code = Column(Text, ForeignKey('subject.subject_code', ondelete='CASCADE'), primary_key=True)
    requirement_type = Column(Text, nullable=False)
    applied_science_available = Column(Boolean, nullable=False)
    graduation_credit_limit = Column(Boolean, nullable=False)
    year_restriction = Column(Boolean, nullable=False)
    first_year_only = Column(Boolean, nullable=False)
    up_to_second_year = Column(Boolean, nullable=False)
    guidance_required = Column(Boolean, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)
    updated_at = Column(TIMESTAMP)

class SubjectProgram(Base):
    __tablename__ = 'subject_program'

    id = Column(Integer, primary_key=True)
    subject_code = Column(Text, ForeignKey('subject.subject_code', ondelete='CASCADE'), nullable=False)
    program_code = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now) 