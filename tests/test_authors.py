import pytest
from fastapi.testclient import TestClient

from app.db import TestingSessionLocal, dev_engine
from app.main import app, get_db
from app import models
from app.schemas import AuthorCreate, AuthorUpdate


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture()
def db_session():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture()
def client():
    client = TestClient(app)
    return client


@pytest.fixture()
def db_cleanup():
    models.Base.metadata.drop_all(bind=dev_engine)


@pytest.fixture()
def author_one():
    author = AuthorCreate(
        first_name="george",
        last_name="costanza"
    ).dict()

    return author


@pytest.fixture()
def author_two(db_session):
    db = db_session
    author = models.Author(
        first_name="John",
        last_name="Doe"
    )
    
    db.add(author)
    db.commit()


@pytest.fixture()
def author_three(db_session):
    db = db_session
    author = models.Author(
        first_name="Cosmo",
        last_name="Kramer"
    )

    db.add(author)
    db.commit()


@pytest.fixture()
def author_four():
    author = AuthorUpdate(
        first_name="Wayne",
        last_name="Knight"
    ).dict()

    return author


def test_create_author(client, author_one):

    response = client.post("/authors/", json=author_one)
    assert response.status_code == 201
    data = response.json()

    assert data["first_name"] == "George"
    assert data["last_name"] == "Costanza"


def test_get_author_two(client, author_two):

    response = client.get("/authors/2")
    assert response.status_code == 200
    data = response.json()

    assert data["first_name"] == "John"
    assert data["last_name"] == "Doe"


def test_get_author_three(client, author_three):

    response = client.get("/authors/3")
    assert response.status_code == 200
    data = response.json()

    assert data["first_name"] == "Cosmo"
    assert data["last_name"] == "Kramer"


def test_get_authors(client):

    response = client.get("/authors/")
    assert response.status_code == 200
    data = response.json()

    first_names = ["George", "John", "Cosmo"]

    assert len(data) == 3
    for i in range(len(data)):
        assert data[i]["first_name"] == first_names[i]


def test_update_author(client, author_four):

    response = client.patch("/authors/1", json=author_four)
    data = response.json()

    assert data["first_name"] == "Wayne"
    assert data["last_name"] == "Knight"


def test_delete_author(client):

    response = client.delete("/authors/3")
    assert response.json() == {"message": "Cosmo Kramer was deleted"}


def test_delete_author_not_exist(client):

    response = client.delete("/authors/100")
    assert response.json() == {"detail": "Author not found"}

def test_db_cleanup(db_cleanup):
    pass