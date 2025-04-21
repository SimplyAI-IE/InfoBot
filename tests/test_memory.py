import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models import Base
from backend.memory import MemoryManager


@pytest.fixture(scope="function")
def test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    yield TestingSessionLocal()
    Base.metadata.drop_all(bind=engine)


def test_profile_upsert_and_get(test_db):
    memory = MemoryManager(test_db)
    user_id = "test_user"
    memory.save_user_profile(user_id, {"pending_action": "offer_tips"})
    profile = memory.get_user_profile(user_id)
    assert profile is not None
    assert profile.pending_action == "offer_tips"


def test_chat_history_saving(test_db):
    memory = MemoryManager(test_db)
    user_id = "test_user"
    memory.save_chat_message(user_id, "user", "Hello world!")
    history = memory.get_chat_history(user_id)
    assert len(history) == 1
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Hello world!"
