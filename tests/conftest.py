import pytest
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from passlib.context import CryptContext

from app.db import engine
from app.main import app, get_db, pwd_context
from app import models


@pytest.fixture(scope="session", autouse=True)
def db_setup():

    if not database_exists(engine.url):
        create_database(engine.url)

    models.Base.metadata.create_all(bind=engine)


@pytest.fixture(name="session")
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    db = Session(bind=connection)

    yield db

    db.rollback()
    connection.close()


@pytest.fixture(name="client")
def client(session: Session):
    def override_get_db():
        return session

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    return client


@pytest.fixture(name="pwd")
def pwd():
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    yield pwd_context