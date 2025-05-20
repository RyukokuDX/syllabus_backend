from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional, Dict, Any
from datetime import datetime
import os
from .models import (
    Subject, Syllabus, LectureSession, Instructor, Book, SyllabusBook,
    GradingCriterion, SyllabusInstructor, SyllabusFaculty, Requirement,
    SubjectRequirement, SubjectProgram
)

# データベース接続設定
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/syllabus')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """データベースセッションを取得"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def save_subject(db, subject_data: Dict[str, Any]) -> Subject:
    """科目基本情報を保存"""
    subject = Subject(
        syllabus_code=subject_data['syllabus_code'],
        name=subject_data['name'],
        class_name=subject_data['class_name'],
        subclass_name=subject_data.get('subclass_name'),
        class_note=subject_data.get('class_note'),
        created_at=datetime.now()
    )
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return subject

def save_syllabus(db, syllabus_data: Dict[str, Any]) -> Syllabus:
    """シラバス情報を保存"""
    syllabus = Syllabus(
        syllabus_code=syllabus_data['syllabus_code'],
        year=syllabus_data['year'],
        subtitle=syllabus_data.get('subtitle'),
        term=syllabus_data['term'],
        grade_b1=syllabus_data['grade_b1'],
        grade_b2=syllabus_data['grade_b2'],
        grade_b3=syllabus_data['grade_b3'],
        grade_b4=syllabus_data['grade_b4'],
        grade_m1=syllabus_data['grade_m1'],
        grade_m2=syllabus_data['grade_m2'],
        grade_d1=syllabus_data['grade_d1'],
        grade_d2=syllabus_data['grade_d2'],
        grade_d3=syllabus_data['grade_d3'],
        campus=syllabus_data['campus'],
        credits=syllabus_data['credits'],
        lecture_code=syllabus_data['lecture_code'],
        summary=syllabus_data.get('summary'),
        goals=syllabus_data.get('goals'),
        methods=syllabus_data.get('methods'),
        outside_study=syllabus_data.get('outside_study'),
        notes=syllabus_data.get('notes'),
        remarks=syllabus_data.get('remarks'),
        created_at=datetime.now()
    )
    db.add(syllabus)
    db.commit()
    db.refresh(syllabus)
    return syllabus

def save_lecture_session(db, session_data: Dict[str, Any]) -> LectureSession:
    """講義時間を保存"""
    session = LectureSession(
        syllabus_code=session_data['syllabus_code'],
        day_of_week=session_data['day_of_week'],
        period=session_data['period'],
        created_at=datetime.now()
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

def save_instructor(db, instructor_data: Dict[str, Any]) -> Instructor:
    """教員情報を保存"""
    instructor = Instructor(
        instructor_code=instructor_data['instructor_code'],
        last_name=instructor_data['last_name'],
        first_name=instructor_data['first_name'],
        last_name_kana=instructor_data.get('last_name_kana'),
        first_name_kana=instructor_data.get('first_name_kana'),
        created_at=datetime.now()
    )
    db.add(instructor)
    db.commit()
    db.refresh(instructor)
    return instructor

def save_book(db, book_data: Dict[str, Any]) -> Book:
    """書籍情報を保存"""
    book = Book(
        author=book_data.get('author'),
        title=book_data['title'],
        publisher=book_data.get('publisher'),
        price=book_data.get('price'),
        isbn=book_data.get('isbn'),
        created_at=datetime.now()
    )
    db.add(book)
    db.commit()
    db.refresh(book)
    return book

def save_syllabus_book(db, syllabus_book_data: Dict[str, Any]) -> SyllabusBook:
    """シラバス-書籍関連を保存"""
    syllabus_book = SyllabusBook(
        syllabus_code=syllabus_book_data['syllabus_code'],
        book_id=syllabus_book_data['book_id'],
        role=syllabus_book_data['role'],
        note=syllabus_book_data.get('note'),
        created_at=datetime.now()
    )
    db.add(syllabus_book)
    db.commit()
    db.refresh(syllabus_book)
    return syllabus_book

def save_grading_criterion(db, criterion_data: Dict[str, Any]) -> GradingCriterion:
    """成績評価基準を保存"""
    criterion = GradingCriterion(
        syllabus_code=criterion_data['syllabus_code'],
        criteria_type=criterion_data['criteria_type'],
        ratio=criterion_data.get('ratio'),
        note=criterion_data.get('note'),
        created_at=datetime.now()
    )
    db.add(criterion)
    db.commit()
    db.refresh(criterion)
    return criterion

def save_syllabus_instructor(db, instructor_data: Dict[str, Any]) -> SyllabusInstructor:
    """シラバス-教員関連を保存"""
    syllabus_instructor = SyllabusInstructor(
        syllabus_code=instructor_data['syllabus_code'],
        instructor_code=instructor_data['instructor_code'],
        created_at=datetime.now()
    )
    db.add(syllabus_instructor)
    db.commit()
    db.refresh(syllabus_instructor)
    return syllabus_instructor

def save_syllabus_faculty(db, faculty_data: Dict[str, Any]) -> SyllabusFaculty:
    """シラバス-学部/課程関連を保存"""
    syllabus_faculty = SyllabusFaculty(
        syllabus_code=faculty_data['syllabus_code'],
        faculty=faculty_data['faculty'],
        created_at=datetime.now()
    )
    db.add(syllabus_faculty)
    db.commit()
    db.refresh(syllabus_faculty)
    return syllabus_faculty

def save_requirement(db, requirement_data: Dict[str, Any]) -> Requirement:
    """科目要件・属性を保存"""
    requirement = Requirement(
        requirement_code=requirement_data['requirement_code'],
        subject_name=requirement_data['subject_name'],
        requirement_type=requirement_data['requirement_type'],
        applied_science_available=requirement_data['applied_science_available'],
        graduation_credit_limit=requirement_data['graduation_credit_limit'],
        year_restriction=requirement_data['year_restriction'],
        first_year_only=requirement_data['first_year_only'],
        up_to_second_year=requirement_data['up_to_second_year'],
        guidance_required=requirement_data['guidance_required'],
        created_at=datetime.now()
    )
    db.add(requirement)
    db.commit()
    db.refresh(requirement)
    return requirement

def save_subject_requirement(db, subject_requirement_data: Dict[str, Any]) -> SubjectRequirement:
    """科目-要綱関連を保存"""
    subject_requirement = SubjectRequirement(
        syllabus_code=subject_requirement_data['syllabus_code'],
        requirement_code=subject_requirement_data['requirement_code'],
        created_at=datetime.now()
    )
    db.add(subject_requirement)
    db.commit()
    db.refresh(subject_requirement)
    return subject_requirement

def save_subject_program(db, program_data: Dict[str, Any]) -> SubjectProgram:
    """科目-学習プログラム関連を保存"""
    subject_program = SubjectProgram(
        syllabus_code=program_data['syllabus_code'],
        program_code=program_data['program_code'],
        created_at=datetime.now()
    )
    db.add(subject_program)
    db.commit()
    db.refresh(subject_program)
    return subject_program

def get_subject_by_code(db, syllabus_code: str) -> Optional[Subject]:
    """科目コードから科目情報を取得"""
    return db.query(Subject).filter(Subject.syllabus_code == syllabus_code).first()

def get_syllabus_by_code_and_year(db, syllabus_code: str, year: int) -> Optional[Syllabus]:
    """科目コードと年度からシラバス情報を取得"""
    return db.query(Syllabus).filter(
        Syllabus.syllabus_code == syllabus_code,
        Syllabus.year == year
    ).first()

def get_lecture_sessions_by_syllabus(db, syllabus_code: str) -> List[LectureSession]:
    """科目コードから講義時間一覧を取得"""
    return db.query(LectureSession).filter(
        LectureSession.syllabus_code == syllabus_code
    ).all()

def get_instructors_by_syllabus(db, syllabus_code: str) -> List[Instructor]:
    """科目コードから教員一覧を取得"""
    return db.query(Instructor).join(
        SyllabusInstructor,
        Instructor.instructor_code == SyllabusInstructor.instructor_code
    ).filter(
        SyllabusInstructor.syllabus_code == syllabus_code
    ).all()

def get_books_by_syllabus(db, syllabus_code: str) -> List[Book]:
    """科目コードから書籍一覧を取得"""
    return db.query(Book).join(
        SyllabusBook,
        Book.id == SyllabusBook.book_id
    ).filter(
        SyllabusBook.syllabus_code == syllabus_code
    ).all()

def get_grading_criteria_by_syllabus(db, syllabus_code: str) -> List[GradingCriterion]:
    """科目コードから成績評価基準一覧を取得"""
    return db.query(GradingCriterion).filter(
        GradingCriterion.syllabus_code == syllabus_code
    ).all()

def get_faculties_by_syllabus(db, syllabus_code: str) -> List[SyllabusFaculty]:
    """科目コードから学部/課程一覧を取得"""
    return db.query(SyllabusFaculty).filter(
        SyllabusFaculty.syllabus_code == syllabus_code
    ).all()

def get_requirements_by_syllabus(db, syllabus_code: str) -> List[Requirement]:
    """科目コードから要件一覧を取得"""
    return db.query(Requirement).join(
        SubjectRequirement,
        Requirement.requirement_code == SubjectRequirement.requirement_code
    ).filter(
        SubjectRequirement.syllabus_code == syllabus_code
    ).all()

def get_programs_by_syllabus(db, syllabus_code: str) -> List[SubjectProgram]:
    """科目コードから学習プログラム一覧を取得"""
    return db.query(SubjectProgram).filter(
        SubjectProgram.syllabus_code == syllabus_code
    ).all()

def update_subject(db, syllabus_code: str, subject_data: Dict[str, Any]) -> Optional[Subject]:
    """科目情報を更新"""
    subject = get_subject_by_code(db, syllabus_code)
    if subject:
        for key, value in subject_data.items():
            setattr(subject, key, value)
        subject.updated_at = datetime.now()
        db.commit()
        db.refresh(subject)
    return subject

def update_syllabus(db, syllabus_code: str, year: int, syllabus_data: Dict[str, Any]) -> Optional[Syllabus]:
    """シラバス情報を更新"""
    syllabus = get_syllabus_by_code_and_year(db, syllabus_code, year)
    if syllabus:
        for key, value in syllabus_data.items():
            setattr(syllabus, key, value)
        syllabus.updated_at = datetime.now()
        db.commit()
        db.refresh(syllabus)
    return syllabus

def delete_subject(db, syllabus_code: str) -> bool:
    """科目情報を削除"""
    subject = get_subject_by_code(db, syllabus_code)
    if subject:
        db.delete(subject)
        db.commit()
        return True
    return False

def delete_syllabus(db, syllabus_code: str, year: int) -> bool:
    """シラバス情報を削除"""
    syllabus = get_syllabus_by_code_and_year(db, syllabus_code, year)
    if syllabus:
        db.delete(syllabus)
        db.commit()
        return True
    return False 