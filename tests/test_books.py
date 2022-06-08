import pytest
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.models import Author, Book, User
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
def book(author: Author, session: Session, user: User):
    db = session
    book = Book(
        title="Awesome Book",
        publisher="Self",
        published_year=2021,
        description="must read book",
        page_count=100,
        average_rating=4.6,
        authors=[author],
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
        publisher = "Amazon",
        published_year = 2000,
        description = "World War II",
        page_count = 483,
        average_rating = 4.9,
        authors = [{"first_name":"John", "last_name": "Doe"}],
        user_id=response.json()["id"]
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
    assert book_data["published_year"] == book.published_year
    assert book_data["description"] == book.description
    assert book_data["page_count"] == book.page_count
    assert book_data["average_rating"] == book.average_rating
    assert book_data["authors"][0]["first_name"] == book.authors[0].first_name
    assert book_data["authors"][0]["last_name"] == book.authors[0].last_name
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


def test_create_book(client: TestClient, author: Author, book_two: BookCreate, current_user: User):

    response = client.post("/books/", json=book_two, headers=current_user)

    assert response.status_code == 201
    data = response.json()

    assert data["title"] == "Band Of Brothers"
    assert data["publisher"] == "Amazon"
    assert data["published_year"] == 2000
    assert data["description"] == "World War II"
    assert data["page_count"] == 483
    assert data["average_rating"] == 4.9
    assert data["user_id"] == book_two["user_id"]


def test_create_book_locked(client: TestClient, author: Author, book_two: BookCreate):

    response = client.post("/books/", json=book_two)

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_create_book_no_author(client: TestClient, book_three: BookCreate, current_user: User):

    response = client.post("/books/", json=book_three, headers=current_user)
    assert response.status_code == 404
    assert response.json() == {"detail": "Author not found. Please create an Author entry for Marcus Smart"}


def test_update_book(session: Session, client: TestClient, book: Book, book_updates: BookUpdate, current_user: User):

    db_book = session.query(Book).filter(
        Book.title == book.title
    ).one()

    response = client.patch(f"/books/{db_book.id}", json=book_updates, headers=current_user)
    data = response.json()

    assert data["id"] == db_book.id
    assert data["publisher"] == "Apple"
    assert data["published_year"] == 1989
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