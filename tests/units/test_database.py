import pytest
from sqlalchemy import inspect, text
from src.database import get_db, init_db, Base, engine


def test_get_db_yields_session():
    generator = get_db()
    db = next(generator)
    assert db is not None
    db.execute(text("SELECT 1"))
    try:
        next(generator)
    except StopIteration:
        pass
    else:
        pytest.fail("get_db должен завершиться после закрытия")


def test_init_db_creates_tables():
    Base.metadata.drop_all(bind=engine)
    init_db()
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    assert "users" in tables
    assert "links" in tables
    assert "archived_links" in tables
