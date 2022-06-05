import pytest
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.models import Author, Book, ReadingList
from app.schemas import ReadingListCreate


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
def reading_list_one(session: Session):
    db = session
    reading_list = ReadingList(
        title="my list"
    )
    db.add(reading_list)
    db.commit()
    yield reading_list


@pytest.fixture()
def reading_list_two():
    request = ReadingListCreate(
        title="my list",
        books=["Awesome Book"]
    ).dict()
    yield request


@pytest.fixture()
def reading_list_three():
    request = ReadingListCreate(
        title="My List",
        books=["book that doesn't exist"]
    ).dict()
    yield request


def test_create_list_book_not_found(client: TestClient, reading_list_three: ReadingListCreate):
    response = client.post("/lists/", json=reading_list_three)
    assert response.status_code == 404
    assert response.json() == {"detail": f"Book not found. Please create a Book entry for {reading_list_three['books'][0].title()}"}


def test_create_list(client: TestClient, book: Book, reading_list_two: ReadingListCreate):
    list_response = client.post("/lists/", json=reading_list_two)
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


def test_delete_list_not_found(client: TestClient):
    response = client.delete("/lists/5")
    assert response.status_code == 404
    assert response.json() == {"detail": "Reading List not found"}


def test_delete_list(session: Session, client: TestClient, reading_list_one: ReadingList):
    db_reading_list = session.query(ReadingList).filter(
        ReadingList.title == reading_list_one.title
    ).one()

    response = client.delete(f"/lists/{db_reading_list.id}")
    assert response.json() == {"message": "my list was deleted"}
