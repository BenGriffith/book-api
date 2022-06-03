import pytest
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from tests.conftest import db_setup, db_session, client
from app.models import Author, Book
from app.schemas import BookCreate, BookUpdate


@pytest.fixture()
def author(session: Session):
    db = session
    author = Author(
        first_name="John",
        last_name="Doe"
    )
    
    db.add(author)
    db.commit()
    yield author


@pytest.fixture()
def book(author: Author, session: Session):
    db = session
    book = Book(
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
    yield book


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
    yield book.dict()


@pytest.fixture()
def book_three(book_two):
    book = book_two
    book["authors"][0]["first_name"] = "Marcus"
    book["authors"][0]["last_name"] = "Smart"

    yield book


@pytest.fixture()
def book_updates():
    updates = BookUpdate(
        publisher = "Apple",
        published_year = 1989,
        average_rating = 4.8
    ).dict()
    yield updates


def test_get_book(db_setup, session: Session, client: TestClient, book: Book):

    db_book = session.query(Book).filter(
        Book.title == book.title
    ).one()

    response = client.get(f"/books/{db_book.id}")
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


def test_create_book(client: TestClient, author: Author, book_two: BookCreate):

    response = client.post("/books/", json=book_two)
    assert response.status_code == 201
    data = response.json()

    assert data["title"] == "Band Of Brothers"
    assert data["publisher"] == "Amazon"
    assert data["published_year"] == 2000
    assert data["description"] == "World War II"
    assert data["page_count"] == 483
    assert data["average_rating"] == 4.9


def test_create_book_no_author(client: TestClient, book_three: BookCreate):

    response = client.post("/books/", json=book_three)
    assert response.status_code == 404
    assert response.json() == {"detail": "Author not found. Please create an Author entry for Marcus Smart"}


def test_update_book(session: Session, client: TestClient, book: Book, book_updates: BookUpdate):
    
    db_book = session.query(Book).filter(
        Book.title == book.title
    ).one()

    response = client.patch(f"/books/{db_book.id}", json=book_updates)
    data = response.json()

    assert data["id"] == db_book.id
    assert data["publisher"] == "Apple"
    assert data["published_year"] == 1989
    assert data["average_rating"] == 4.8


def test_delete_book(session: Session, client: TestClient, book: Book):

    db_book = session.query(Book).filter(
        Book.title == book.title
    ).first()

    response = client.delete(f"/books/{db_book.id}")
    assert response.json() == {"message": "Awesome Book was deleted"}