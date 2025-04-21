import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models import Base
from backend.memory import MemoryManager
from backend.apps.pension_guru.extract import extract_user_data

@pytest.fixture(scope="function")
def test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()

def test_extract_party_size(test_db):
    user_id = "test_user_1"
    memory = MemoryManager(test_db)
    extract_user_data(user_id, "I'd like a table for 4 at 7pm tonight.")
    profile = memory.get_user_profile(user_id)

    assert profile is not None
    assert profile.party_size == 4
    assert profile.time is not None
    assert profile.date == "today"

def test_extract_cuisine(test_db):
    user_id = "test_user_2"
    memory = MemoryManager(test_db)
    extract_user_data(user_id, "We want vegan food tomorrow night at 8")
    profile = memory.get_user_profile(user_id)

    assert profile.cuisine == "vegan"
    assert profile.date == "tomorrow"
