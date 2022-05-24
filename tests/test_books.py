import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.db import get_session
from app.main import app, Books


@pytest.fixture(name="session")
def session_fixture():

    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture()
def book_one():
    book = Books(
        id = 1,
        title = "Band of Brothers",
        authors = "Stephen Ambrose"
    )
    return book.dict()


@pytest.fixture()
def book_two():
    book = Books(
        id = 2,
        title = "The Republic",
        authors = "Plato"
    )
    return book.dict()


def test_get_root(client):

    response = client.get("/")
    assert response.json() == {"message": "Welcome to the Book API!"}


def test_get_book(client, book_one):

    post_response = client.post("/books/", json=book_one)
    book_one_data = post_response.json()

    book_one_id = book_one_data["id"]
    book_one_title = book_one_data["title"]
    book_one_authors = book_one_data["authors"]

    response = client.get(f"/books/{book_one_id}")
    data = response.json()

    assert response.status_code == 200
    assert book_one_id == data["id"]
    assert book_one_title == data["title"]
    assert book_one_authors == data["authors"]


def test_get_book_unknown(client, book_one):

    post_response = client.post("/books/", json=book_one)
    get_response = client.get("/books/2")
    assert get_response.status_code == 404


def test_create_book(client):

    response = client.post("/books/", json={
        "id": 1,
        "title": "Judge Dredd",
        "authors": "Zach Morris"
    })
    data = response.json()

    assert response.status_code == 201
    assert data["id"] == 1
    assert data["title"] == "Judge Dredd"
    assert data["authors"] == "Zach Morris"


def test_update_book(client):

    response = client.post("/books/", json={
        "id": 2,
        "title": "Huckleberry Finn",
        "authors": "Mark Twain"
    })
    data = response.json()

    assert response.status_code == 201
    assert data["id"] == 2

    response = client.patch("/books/2", json={
        "id": 2,
        "title": "The Great Gatsby",
        "authors": "F. Scott Fitzgerald"
    })
    data = response.json()

    assert data["id"] == 2
    assert data["title"] == "The Great Gatsby"
    assert data["authors"] == "F. Scott Fitzgerald"


def test_delete_book(client, session, book_two):

    post_response = client.post("/books/", json=book_two)
    data = post_response.json()

    delete_response = client.delete("/books/2")

    book_in_db = session.get(Books, data["id"])

    assert delete_response.status_code == 200
    assert book_in_db is None