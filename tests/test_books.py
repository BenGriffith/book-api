import pytest
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.models import Book, User
from app.schemas import BookCreate, BookUpdate


@pytest.fixture()
def user(session: Session):
    db = session
    user = User(
        username="michaeljordan",
        email="michael@gmail.com",
        first_name="michael",
        last_name="jordan",
        password="password"
    )

    db.add(user)
    db.commit()
    yield user


@pytest.fixture()
def book(session: Session, user: User):
    db = session
    book = Book(
        title="Awesome Book",
        authors="'Tony Parker, Stephen King'",
        publisher="Self",
        published_date="2021-10-01",
        description="must read book",
        page_count=100,
        average_rating=4.6,
        google_books_id=None,
        user_id=user.id
    )

    db.add(book)
    db.commit()
    yield book


@pytest.fixture()
def book_two(client: TestClient, current_user: User):

    response = client.get("/users/me", headers=current_user)

    book = BookCreate(
        title = "Band Of Brothers",
        authors = "Stephen Ambrose",
        publisher = "Amazon",
        published_date = "2000-12-10",
        description = "World War II",
        page_count = 483,
        average_rating = 4.9,
        google_books_id=None,
        user_id=response.json()["id"]
    )
    yield book.dict()


@pytest.fixture()
def book_three(book_two):
    book = book_two
    book["authors"][0] = "Marcus Smart"

    yield book


@pytest.fixture()
def book_updates():
    updates = BookUpdate(
        publisher = "Apple",
        published_date = "1989-01-20",
        average_rating = 4.8
    ).dict()
    yield updates


def test_get_book(session: Session, client: TestClient, book: Book, user: User, current_user: User):

    db_book = session.query(Book).filter(
        Book.title == book.title
    ).one()

    db_user = session.query(User).filter(
        User.username == user.username
    ).first()

    response = client.get(f"/books/{db_book.id}", headers=current_user)
    assert response.status_code == 200
    book_data = response.json()

    assert book_data["title"] == book.title
    assert book_data["publisher"] == book.publisher
    assert book_data["published_date"] == book.published_date
    assert book_data["description"] == book.description
    assert book_data["page_count"] == book.page_count
    assert book_data["average_rating"] == book.average_rating
    assert book_data["authors"][0] == book.authors[0]
    assert book_data["authors"][1] == book.authors[1]
    assert book_data["user_id"] == db_user.id


def test_get_book_locked(session: Session, client: TestClient, book: Book):

    db_book = session.query(Book).filter(
        Book.title == book.title
    ).one()

    response = client.get(f"/books/{db_book.id}")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_get_book_unknown(client, current_user):

    response = client.get("/books/102", headers=current_user)
    assert response.status_code == 404
    assert response.json() == {"detail": "Book not found"}


def test_create_book(client: TestClient, book_two: BookCreate, current_user: User):

    response = client.post("/books/", json=book_two, headers=current_user)

    assert response.status_code == 201
    data = response.json()

    assert data["title"] == "Band Of Brothers"
    assert data["publisher"] == "Amazon"
    assert data["published_date"] == "2000-12-10"
    assert data["description"] == "World War II"
    assert data["page_count"] == 483
    assert data["average_rating"] == 4.9
    assert data["user_id"] == book_two["user_id"]


def test_create_book_locked(client: TestClient, book_two: BookCreate):

    response = client.post("/books/", json=book_two)

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_update_book(session: Session, client: TestClient, book: Book, book_updates: BookUpdate, current_user: User):

    db_book = session.query(Book).filter(
        Book.title == book.title
    ).one()

    response = client.patch(f"/books/{db_book.id}", json=book_updates, headers=current_user)
    data = response.json()

    assert data["id"] == db_book.id
    assert data["publisher"] == "Apple"
    assert data["published_date"] == "1989-01-20"
    assert data["average_rating"] == 4.8


def test_update_book_locked(session: Session, client: TestClient, book: Book, book_updates: BookUpdate):

    db_book = session.query(Book).filter(
        Book.title == book.title
    ).one()

    response = client.patch(f"/books/{db_book.id}", json=book_updates)
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_delete_book(session: Session, client: TestClient, book: Book, current_user: User):

    db_book = session.query(Book).filter(
        Book.title == book.title
    ).first()

    response = client.delete(f"/books/{db_book.id}", headers=current_user)
    assert response.json() == {"message": "Awesome Book was deleted"}

def test_delete_book_locked(session: Session, client: TestClient, book: Book):

    db_book = session.query(Book).filter(
        Book.title == book.title
    ).first()

    response = client.delete(f"/books/{db_book.id}")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}