from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime
from typing import Any
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# SQLAlchemy Base definition using modern DeclarativeBase (if supported)
class Base(DeclarativeBase):  # For SQLAlchemy 2.x
    pass


# If using SQLAlchemy <2.0, fallback:
# Base = declarative_base()

SQLITE_URL = "sqlite:///./memory.db"

engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)


class UserProfile(Base):
    __tablename__ = "user_profiles"

    user_id: Any = Column(String, primary_key=True, index=True)
    age: Any = Column(Integer, nullable=True)
    income: Any = Column(Integer, nullable=True)
    region: Any = Column(String, nullable=True)
    pending_step: Any = Column(String, nullable=True)
    pending_action: Any = Column(String, nullable=True)
    prsi_years: Any = Column(Integer, nullable=True)
    retirement_age: Any = Column(Integer, nullable=True)


class User(Base):
    __tablename__ = "users"

    id: Any = Column(String, primary_key=True, index=True)
    name: Any = Column(String, nullable=True)
    email: Any = Column(String, nullable=True)


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id: Any = Column(Integer, primary_key=True, autoincrement=True)
    user_id: Any = Column(String, index=True)
    role: Any = Column(String)
    content: Any = Column(Text)
    timestamp: Any = Column(DateTime, default=datetime.utcnow)


def init_db() -> None:
    from backend.models import Base
    from backend.models import SessionLocal

    engine = SessionLocal().get_bind()
    Base.metadata.create_all(bind=engine)
