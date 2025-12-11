from typing import List, Optional
from sqlalchemy.exc import SQLAlchemyError
from db_project.db_session import get_session
from db_project.orm_models import User


def get_all_users() -> List[User]:
    session = get_session()
    try:
        users: List[User] = session.query(User).all()
        return users
    except SQLAlchemyError as e:
        print("Error:", e)
        return []
    finally:
        session.close()


def find_user_by_name(username: str) -> Optional[User]:
    session = get_session()
    try:
        user: Optional[User] = session.query(User).filter(User.name == username).first()
        return user
    except SQLAlchemyError as e:
        print("Error:", e)
        return None
    finally:
        session.close()
