import pytest
from fastapi.testclient import TestClient

from app.db import TestingSessionLocal, dev_engine
from app.main import app, get_db
from app import models
from app.schemas import BookCreate, BookUpdate


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
def author(db_session):
    db = db_session
    author = models.Author(
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
    book = models.Book(
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
def book_two():
    book = BookCreate(
        title = "Band Of Brothers",
        publisher = "Amazon",
        published_year = 2000,
        description = "World War II",
        page_count = 483,
        average_rating = 4.9,
        authors = [{"first_name":"John", "last_name": "Doe"}]
    )
    return book.dict()


@pytest.fixture()
def book_three(book_two):
    book = book_two
    book["authors"][0]["first_name"] = "Marcus"
    book["authors"][0]["last_name"] = "Smart"

    return book


@pytest.fixture()
def book_updates():
    updates = BookUpdate(
        publisher = "Apple",
        published_year = 1989,
        average_rating = 4.8
    ).dict()
    return updates


def test_get_book(client, book):

    response = client.get("/books/1")
    assert response.status_code == 200
    book_data = response.json()

    assert book_data["title"] == book.title
    assert book_data["publisher"] == book.publisher
    assert book_data["published_year"] == book.published_year
    assert book_data["description"] == book.description
    assert book_data["page_count"] == book.page_count
    assert book_data["average_rating"] == book.average_rating
    assert book_data["authors"][0]["first_name"] == book.authors[0].first_name
    assert book_data["authors"][0]["last_name"] == book.authors[0].last_name


def test_get_book_unknown(client):

    response = client.get("/books/102")
    assert response.status_code == 404
    assert response.json() == {"detail": "Book not found"}


def test_create_book(client, book_two):

    response = client.post("/books/", json=book_two)
    assert response.status_code == 201
    data = response.json()

    assert data["title"] == "Band Of Brothers"
    assert data["publisher"] == "Amazon"
    assert data["published_year"] == 2000
    assert data["description"] == "World War II"
    assert data["page_count"] == 483
    assert data["average_rating"] == 4.9


def test_create_book_no_author(client, book_three):

    response = client.post("/books/", json=book_three)
    assert response.status_code == 404
    assert response.json() == {"detail": "Author not found. Please create an Author entry for Marcus Smart"}


def test_update_book(client, book_updates):
    
    response = client.patch("/books/1", json=book_updates)
    data = response.json()

    assert data["id"] == 1
    assert data["publisher"] == "Apple"
    assert data["published_year"] == 1989
    assert data["average_rating"] == 4.8


def test_delete_book(client):

    response = client.delete("/books/1")
    assert response.json() == {"message": "Awesome Book was deleted"}


def test_db_cleanup(db_cleanup):
    pass