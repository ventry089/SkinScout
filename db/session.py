from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import DB_PATH
from db.models import Base


_engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
_SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False)


def init_db():
    Base.metadata.create_all(_engine)


def get_session():
    return _SessionLocal()
