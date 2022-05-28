import pytest
from fastapi.testclient import TestClient

from app.db import TestingSessionLocal
from app.main import app, get_db
from app.models import Author, Book
from app.schemas import ReadingListCreate


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture()
def db_session():
    return TestingSessionLocal()


@pytest.fixture()
def client():
    client = TestClient(app)
    return client


@pytest.fixture()
def author(db_session):
    db = db_session
    author = Author(
        id=1,
        first_name="John",
        last_name="Doe"
    )
    
    db.add(author)
    db.commit()
    db.refresh(author)

    return author


@pytest.fixture()
def book(author, db_session):
    db = db_session
    book = Book(
        id=1,
        title="Awesome Book",
        publisher="Self",
        published_year=2021,
        description="must read book",
        page_count=100,
        average_rating=4.6,
        authors=[author]
    )

    db.add(book)
    db.commit()
    db.refresh(book)
    
    return book


@pytest.fixture()
def reading_list():
    request = ReadingListCreate(
        title="my list",
        books=["Awesome Book"]
    ).dict()

    return request


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


def test_create_list(client, book, reading_list):
    list_response = client.post("/lists/", json=reading_list)
    assert list_response.status_code == 201
    data = list_response.json()
    assert data["title"] == "my list"
    books = data["books"][0]
    assert books["title"] == book.title
    assert books["publisher"] == book.publisher
    assert books["published_year"] == book.published_year
    assert books["description"] == book.description
    assert books["page_count"] == book.page_count
    assert books["average_rating"] == book.average_rating


def test_delete_list_not_found(client):
    response = client.delete("/lists/5")
    assert response.status_code == 404
    assert response.json() == {"detail": "Reading List not found"}


def test_delete_list(client):
    response = client.delete("/lists/1")
    assert response.json() == {"message": "my list was deleted"}