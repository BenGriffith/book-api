import pytest
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.db import engine
from app.main import app, get_db, get_current_user
from app.crud import pwd_context
from app import models
from app import schemas


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


@pytest.fixture(name="current_user")
def current_user(client: TestClient, session: Session):

    user = schemas.UserCreate(
        username="testuser",
        email="test@email.io",
        first_name="John",
        last_name="Doe",
        password="quarantine"
    ).dict()

    user_create_response = client.post("/users/", json=user)

    token_response = client.post(
            "/token", 
            data={"username": "testuser", "password": "quarantine"},
            headers={"content-type": "application/x-www-form-urlencoded"})

    yield {"Authorization": f"Bearer {token_response.json()['access_token']}"}