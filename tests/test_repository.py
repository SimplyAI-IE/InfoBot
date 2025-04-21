import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models import Base
from backend.repository import SessionRepository

@pytest.fixture(scope="function")
def test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    yield TestingSessionLocal()
    Base.metadata.drop_all(bind=engine)

def test_user_profile_roundtrip(test_db):
    session = test_db()
    repo = SessionRepository(session)
    repo.upsert_user_profile("abc123", {"pending_action": "init"})
    profile = repo.get_user_profile("abc123")
    assert profile.pending_action == "init"

def test_chat_history_ordering(test_db):
    session = test_db()
    repo = SessionRepository(session)
    uid = "user_x"
    repo.add_chat_message(uid, "user", "Hi")
    repo.add_chat_message(uid, "assistant", "Welcome")
    history = repo.get_chat_history(uid)
    assert history[0]["role"] == "user"
    assert history[1]["role"] == "assistant"
