import pytest
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import Session, sessionmaker
from fastapi.testclient import TestClient

from app.db import engine
from app.main import app, get_db
from app import models

@pytest.fixture()
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
    yield client