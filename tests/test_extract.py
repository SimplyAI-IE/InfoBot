import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models import Base
from backend.memory import MemoryManager

@pytest.fixture(scope="function")
def test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()

