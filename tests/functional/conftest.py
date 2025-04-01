import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database import Base, get_db
from src.main import app
from src.models import User
from src.security import get_password_hash
from src.redis_client import redis_client

# Тестовая база
TEST_DATABASE_URL = "sqlite:///././tests/test.db"

engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Переопределим зависимость
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Подключим переопределение
app.dependency_overrides[get_db] = override_get_db


# Очистка Redis перед каждым тестом
@pytest.fixture(autouse=True)
def clear_redis():
    redis_client.flushall()


# Подключение клиента
@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)


# Создание пользователя
@pytest.fixture
def test_user(client):
    from src.schemas import UserCreate
    db = next(override_get_db())
    user = User(
        email="user@example.com",
        hashed_password=get_password_hash("password123")
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
