from sqlalchemy import create_engine, and_, or_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, Type, TypeVar, List, Dict, Any
from .models import Base
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

T = TypeVar('T')

class Database:
    def __init__(self, db_url: str):
        self.engine = create_engine(db_url)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def init_db(self):
        """データベースの初期化"""
        try:
            Base.metadata.create_all(self.engine)
            logger.info("データベースの初期化が完了しました")
        except SQLAlchemyError as e:
            logger.error(f"データベースの初期化中にエラーが発生しました: {e}")
            raise

    def get_session(self):
        """セッションの取得"""
        return self.SessionLocal()

    def add_record(self, model: T) -> Optional[T]:
        """
        レコードの追加
        Args:
            model: 追加するモデルインスタンス
        Returns:
            追加されたモデルインスタンス、エラー時はNone
        """
        session = self.get_session()
        try:
            session.add(model)
            session.commit()
            session.refresh(model)
            return model
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"レコード追加中にエラーが発生しました: {e}")
            return None
        finally:
            session.close()

    def add_records(self, models: List[T]) -> bool:
        """
        複数レコードの一括追加
        Args:
            models: 追加するモデルインスタンスのリスト
        Returns:
            成功時True、失敗時False
        """
        session = self.get_session()
        try:
            session.add_all(models)
            session.commit()
            return True
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"レコード一括追加中にエラーが発生しました: {e}")
            return False
        finally:
            session.close()

    def get_by_id(self, model_class: Type[T], id_value: any) -> Optional[T]:
        """
        IDによるレコードの取得
        Args:
            model_class: モデルクラス
            id_value: 主キーの値
        Returns:
            モデルインスタンス、存在しない場合はNone
        """
        session = self.get_session()
        try:
            return session.query(model_class).get(id_value)
        except SQLAlchemyError as e:
            logger.error(f"レコード取得中にエラーが発生しました: {e}")
            return None
        finally:
            session.close()

    def update_record(self, model: T) -> bool:
        """
        レコードの更新
        Args:
            model: 更新するモデルインスタンス
        Returns:
            成功時True、失敗時False
        """
        session = self.get_session()
        try:
            session.merge(model)
            session.commit()
            return True
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"レコード更新中にエラーが発生しました: {e}")
            return False
        finally:
            session.close()

    def delete_record(self, model: T) -> bool:
        """
        レコードの削除
        Args:
            model: 削除するモデルインスタンス
        Returns:
            成功時True、失敗時False
        """
        session = self.get_session()
        try:
            session.delete(model)
            session.commit()
            return True
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"レコード削除中にエラーが発生しました: {e}")
            return False
        finally:
            session.close()

    def query_records(self, model_class: Type[T], filters: Dict[str, Any] = None, 
                     order_by: List[str] = None, limit: int = None) -> List[T]:
        """
        条件に基づいてレコードを検索
        Args:
            model_class: モデルクラス
            filters: フィルター条件の辞書
            order_by: ソート条件のリスト
            limit: 取得件数の制限
        Returns:
            検索結果のリスト
        """
        session = self.get_session()
        try:
            query = session.query(model_class)
            
            if filters:
                filter_conditions = []
                for key, value in filters.items():
                    if isinstance(value, (list, tuple)):
                        filter_conditions.append(getattr(model_class, key).in_(value))
                    else:
                        filter_conditions.append(getattr(model_class, key) == value)
                query = query.filter(and_(*filter_conditions))

            if order_by:
                for field in order_by:
                    desc = field.startswith('-')
                    field_name = field[1:] if desc else field
                    field_attr = getattr(model_class, field_name)
                    query = query.order_by(field_attr.desc() if desc else field_attr)

            if limit:
                query = query.limit(limit)

            return query.all()
        except SQLAlchemyError as e:
            logger.error(f"レコード検索中にエラーが発生しました: {e}")
            return []
        finally:
            session.close()

    def search_syllabus(self, year: int = None, term: str = None, 
                       class_name: str = None, faculty: str = None,
                       instructor_name: str = None) -> List[Dict[str, Any]]:
        """
        シラバス情報の検索
        Args:
            year: 開講年度
            term: 開講学期
            class_name: 科目区分
            faculty: 開講学部
            instructor_name: 教員名
        Returns:
            検索結果のリスト
        """
        from .models import Subject, Syllabus, SyllabusFaculty, Instructor, SyllabusInstructor

        session = self.get_session()
        try:
            query = session.query(
                Subject.subject_code,
                Subject.name.label('subject_name'),
                Subject.class_name,
                Syllabus.year,
                Syllabus.term,
                Syllabus.credits,
                Syllabus.campus,
                Instructor.name.label('instructor_name'),
                SyllabusFaculty.faculty
            ).join(
                Syllabus, Subject.subject_code == Syllabus.subject_code
            ).join(
                SyllabusFaculty, Subject.subject_code == SyllabusFaculty.subject_code
            ).join(
                SyllabusInstructor, Subject.subject_code == SyllabusInstructor.subject_code
            ).join(
                Instructor, SyllabusInstructor.instructor_code == Instructor.instructor_code
            )

            if year:
                query = query.filter(Syllabus.year == year)
            if term:
                query = query.filter(Syllabus.term == term)
            if class_name:
                query = query.filter(Subject.class_name == class_name)
            if faculty:
                query = query.filter(SyllabusFaculty.faculty == faculty)
            if instructor_name:
                query = query.filter(Instructor.name.like(f"%{instructor_name}%"))

            results = query.all()
            return [dict(zip(result.keys(), result)) for result in results]
        except SQLAlchemyError as e:
            logger.error(f"シラバス検索中にエラーが発生しました: {e}")
            return []
        finally:
            session.close() 