import pytest
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from tests.conftest import db_setup, db_session, client
from app.models import User, Author, Book, ReadingList
from app.schemas import UserCreate, UserUpdate, ReadingListCreate


@pytest.fixture()
def user_one():
    user = UserCreate(
        email="user_one@test.com",
        first_name="Elaine",
        last_name="Benes"
    ).dict()
    yield user


@pytest.fixture()
def user_two(session: Session):
    db = session
    user = User(
        email="user_two@test.com",
        first_name="Jerry",
        last_name="Seinfeld"
    )
    db.add(user)
    db.commit()
    yield user


@pytest.fixture()
def user_three():
    user = UserCreate(
        email="user_TWO@test.com",
        first_name="Newman",
        last_name="USPS"
    ).dict()
    yield user


@pytest.fixture()
def user_two_update():
    user = UserUpdate(
        email="new_email@test.com",
        first_name="Ben",
        last_name="Stiller"
    ).dict()
    yield user


@pytest.fixture()
def assign_user_to_reading_list(session: Session):
    db = session

    # create Author
    author = Author(
        first_name="Stephen",
        last_name="King"
    )


    # create Book One
    book_one = Book(
        title="It",
        publisher="Company A",
        published_year=1986,
        description="Terrifying",
        page_count=304,
        average_rating=5,
        authors=[author]
    )


    # create Book Two
    book_two = Book(
        title="The Shining",
        publisher="Company A",
        published_year=1977,
        description="Scary",
        page_count=456,
        average_rating=5,
        authors=[author]
    )

    db.add(author)
    db.add(book_one)
    db.add(book_two)
    db.commit()

    # create Reading List assigned to user 
    reading_list = ReadingListCreate(
        title="books to read",
        books=[book_one.title, book_two.title],
        user_email="new_email@test.com"
    ).dict()

    yield reading_list


def test_create_user(client: TestClient, user_one: UserCreate):
    
    response = client.post("/users/", json=user_one)
    assert response.status_code == 201
    data = response.json()

    assert data["email"] == "user_one@test.com"
    assert data["first_name"] == "Elaine"
    assert data["last_name"] == "Benes"


def test_get_user(session: Session, client: TestClient, user_two: User):

    db_user = session.query(User).filter(
        User.email == user_two.email
    ).first()
    
    response = client.get(f"/users/{db_user.id}")
    assert response.status_code == 200
    data = response.json()

    assert data["email"] == "user_two@test.com"
    assert data["first_name"] == "Jerry"
    assert data["last_name"] == "Seinfeld"
    

def test_create_user_same_email(session: Session, client: TestClient, user_three: User):

    user = User(
        email="user_TWO@test.com",
        first_name="Joe",
        last_name="Jackson"
    )
    db = session
    db.add(user)
    db.commit()
    
    response = client.post("/users/", json=user_three)
    assert response.status_code == 400
    assert response.json() == {"detail": "Please use different email address"}


def test_update_user(session: Session, client: TestClient, user_two: User, user_two_update: UserUpdate):

    db_user = session.query(User).filter(
        User.email == user_two.email
    ).first()
    
    response = client.put(f"/users/{db_user.id}", json=user_two_update)
    data = response.json()

    assert data["id"] == db_user.id
    assert data["email"] == "new_email@test.com"
    assert data["first_name"] == "Ben"
    assert data["last_name"] == "Stiller"


def test_delete_user(session: Session, client: TestClient, user_two: User):

    db_user = session.query(User).filter(
        User.email == user_two.email
    ).first()

    response = client.delete(f"/users/{db_user.id}")
    assert response.json() == {"message": f"{db_user.first_name} {db_user.last_name} was deleted"}


def test_delete_user_not_exist(client):
    
    response = client.delete("/users/100")
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


def test_assign_user_to_reading_list(session: Session, client: TestClient, assign_user_to_reading_list: ReadingListCreate):

    user = User(
        email="new_email@test.com",
        first_name="Jerry",
        last_name="Rice"
    )
    db = session
    db.add(user)
    db.commit()

    response = client.post("/lists/", json=assign_user_to_reading_list)

    db_list = db.query(ReadingList).filter(
        ReadingList.title == assign_user_to_reading_list["title"]
    ).first()

    assert response.status_code == 201
    data = response.json()

    assert data["title"] == "books to read"
    assert data["books"][0]["title"] == "It"
    assert data["books"][1]["title"] == "The Shining"
    assert data["user_id"] == db_list.user_id