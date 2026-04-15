import os
import sys
from pathlib import Path

# Добавляем папку backend в sys.path, чтобы импортировать app
sys.path.insert(0, str(Path(__file__).parent.parent))

# Переопределяем DATABASE_URL на SQLite in-memory ДО импорта app
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app, get_db
from app.models import Base

# Тестовая БД
test_engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Переопределяем зависимость get_db
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Создаём таблицы
Base.metadata.create_all(bind=test_engine)

@pytest.fixture(scope="function")
def db_session():
    """Фикстура сессии с откатом транзакции после теста."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db_session):
    """Тестовый клиент FastAPI с изолированной БД."""
    def _get_test_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = _get_test_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()