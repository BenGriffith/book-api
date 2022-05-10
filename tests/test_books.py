import pytest
from fastapi.testclient import TestClient
from app.main import app, Book, fake_db


@pytest.fixture
def client():
    client = TestClient(app)
    return client


@pytest.fixture
def book():
    book = Book(
        id = 1, 
        title = "Sample Book",
        authors = ["Author 1", "Author 2"]
    )
    return book


@pytest.fixture
def book_payload():
    return dict(
        id = 1,
        title = "Sample Book",
        authors = ["Author 1", "Author 2"]
    )


def test_get_root(client):
    response = client.get("/")
    assert response.json() == {"message": "Welcome to the Book API!"}


def test_create_book(client, book_payload, book):
    response = client.post("/books/", json=book_payload)
    assert response.status_code == 201
    assert response.json() == book
    assert fake_db[book.id] == book_payload


def test_get_book(client, book):
    response = client.get("/books/1")
    assert response.status_code == 200
    assert response.json() == book


@pytest.fixture
def book_update():
    book = Book(
        id = 1,
        title = "A River Runs Through It",
        authors = ["Norman Maclean"]
    )
    return book


@pytest.fixture
def book_update_payload():
    return dict(
        id = 1,
        title = "A River Runs Through It",
        authors = ["Norman Maclean"]
    )


def test_update_book(client, book_update_payload, book_update):
    response = client.put("/books/1", json=book_update_payload)
    assert response.json() == book_update
    assert fake_db[book_update.id] == book_update_payload


def test_delete_book(client):
    response = client.delete("books/1")
    assert response.json() == {"ok": True}
    assert len(fake_db) == 0