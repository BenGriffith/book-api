import pytest
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from passlib.context import CryptContext

from app.models import User, Author, Book, ReadingList
from app.schemas import UserCreate, UserUpdate, ReadingListCreate
from app.crud import get_user


@pytest.fixture()
def user_one(pwd: CryptContext):
    user = UserCreate(
        username="elainebenes",
        email="user_one@test.com",
        first_name="Elaine",
        last_name="Benes",
        password="rhodeisland"
    ).dict()
    yield user


@pytest.fixture()
def user_two(session: Session, pwd: CryptContext):
    db = session
    user = User(
        username="jerryseinfeld",
        email="user_two@test.com",
        first_name="Jerry",
        last_name="Seinfeld",
        password=pwd.hash("newyork")
    )
    db.add(user)
    db.commit()
    yield user


@pytest.fixture()
def user_three():
    user = UserCreate(
        username="newmanthemailman",
        email="user_TWO@test.com",
        first_name="Newman",
        last_name="USPS",
        password="foreveryoung"
    ).dict()
    yield user


@pytest.fixture()
def user_two_update():
    user = UserUpdate(
        username="benstiller",
        email="new_email@test.com",
        first_name="Ben",
        last_name="Stiller",
        password="password123"
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
        username="jerryrice"
    ).dict()

    yield reading_list


def test_create_user(session: Session, client: TestClient, user_one: UserCreate, pwd: CryptContext):

    response = client.post("/users/", json=user_one)
    assert response.status_code == 201
    data = response.json()

    assert data["username"] == user_one["username"]
    assert data["email"] == user_one["email"]
    assert data["first_name"] == user_one["first_name"]
    assert data["last_name"] == user_one["last_name"]

    user = get_user(db=session, username=data["username"])

    assert pwd.verify(user_one["password"], user.password)


def test_get_user(session: Session, client: TestClient, user_two: User, pwd: CryptContext):

    user = get_user(db=session, username=user_two.username)

    response = client.get(f"/users/{user.id}")
    assert response.status_code == 200
    data = response.json()

    assert data["username"] == user_two.username
    assert data["email"] == user_two.email
    assert data["first_name"] == user_two.first_name
    assert data["last_name"] == user_two.last_name
    assert pwd.verify("newyork", user.password)


def test_create_user_same_email(session: Session, client: TestClient, user_three: User, pwd: CryptContext):

    user = User(
        username="joejackson",
        email="user_TWO@test.com",
        first_name="Joe",
        last_name="Jackson",
        password=pwd.hash("whitesox")
    )
    db = session
    db.add(user)
    db.commit()

    response = client.post("/users/", json=user_three)
    assert response.status_code == 400
    assert response.json() == {"detail": "Please use different email address"}


def test_update_user(session: Session, client: TestClient, user_two: User, user_two_update: UserUpdate, pwd: CryptContext):

    user = get_user(db=session, username=user_two.username)

    response = client.put(f"/users/{user.id}", json=user_two_update)
    data = response.json()

    assert data["id"] == user.id
    assert data["email"] == user_two.email
    assert data["first_name"] == user_two.first_name
    assert data["last_name"] == user_two.last_name
    assert data["username"] == user_two.username
    assert pwd.verify("password123", user.password)


def test_delete_user(session: Session, client: TestClient, user_two: User):

    user = get_user(db=session, username=user_two.username)

    response = client.delete(f"/users/{user.id}")
    assert response.json() == {"message": f"{user.first_name} {user.last_name} was deleted"}


def test_delete_user_not_exist(client):

    response = client.delete("/users/100")
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


def test_assign_user_to_reading_list(session: Session, client: TestClient, assign_user_to_reading_list: ReadingListCreate, pwd: CryptContext):

    user = User(
        username="jerryrice",
        email="new_email@test.com",
        first_name="Jerry",
        last_name="Rice",
        password="proform"
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