from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, Type, TypeVar
from .models import Base
import logging

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

    def add_records(self, models: list[T]) -> bool:
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