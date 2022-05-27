import pytest
from fastapi.testclient import TestClient

from tests.pytest_db import engine, TestingSessionLocal, Base
from app import models
from app.main import app, get_db
from app.schemas import AuthorCreate, BookCreate, ReadingListCreate

models.Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    except:
        db.close()

app.dependency_overrides[get_db] = override_get_db


@pytest.fixture()
def client():
    client = TestClient(app)
    return client


@pytest.fixture()
def author():
    author = AuthorCreate(
        first_name="John",
        last_name="Doe"
    ).dict()
    return author


@pytest.fixture()
def book(author):
    book = BookCreate(
        title="Awesome Book",
        publisher="Self",
        published_year=2021,
        description="must read book",
        page_count=100,
        average_rating=4.6,
        authors=[author]
    ).dict()
    return book


@pytest.fixture()
def reading_list(book):
    reading_list = ReadingListCreate(
        title="My list",
        books=["Awesome Book"]
    ).dict()
    return reading_list


@pytest.fixture()
def reading_list_request():
    request = ReadingListCreate(
        title="My List",
        books=["book that doesn't exist"]
    ).dict()
    return request


def test_create_list_book_not_found(client, reading_list_request):
    response = client.post("/lists/", json=reading_list_request)
    assert response.status_code == 404
    assert response.json() == {"detail": f"Book not found. Please create a Book entry for {reading_list_request['books'][0].title()}"}


def test_create_list(client, author, book, reading_list):
    author_response = client.post("/authors/", json=author)
    assert author_response.status_code == 201

    book_response = client.post("/books/", json=book)
    assert book_response.status_code == 201

    list_response = client.post("/lists/", json=reading_list)
    assert list_response.status_code == 201
    data = list_response.json()
    assert data["title"] == "My List"
    books = data["books"][0]
    assert books["title"] == book["title"]
    assert books["publisher"] == book["publisher"]
    assert books["published_year"] == book["published_year"]
    assert books["description"] == book["description"]
    assert books["page_count"] == book["page_count"]
    assert books["average_rating"] == book["average_rating"]


def test_delete_list_not_found(client):
    response = client.delete("/lists/5")
    assert response.status_code == 404
    assert response.json() == {"detail": "Reading List not found"}