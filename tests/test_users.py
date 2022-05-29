import email
import pytest
from fastapi.testclient import TestClient

from app.db import TestingSessionLocal
from app.main import app, get_db
from app.models import User, Author, Book
from app.schemas import UserCreate, UserUpdate, ReadingListCreate


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
def user_one():
    user = UserCreate(
        email="user_one@test.com",
        first_name="Elaine",
        last_name="Benes"
    ).dict()
    return user


@pytest.fixture()
def user_two(db_session):
    db = db_session
    user = User(
        id=2,
        email="user_two@test.com",
        first_name="Jerry",
        last_name="Seinfeld"
    )

    db.add(user)
    db.commit()


@pytest.fixture()
def user_three():
    user = UserCreate(
        email="user_TWO@test.com",
        first_name="Newman",
        last_name="USPS"
    ).dict()
    return user


@pytest.fixture()
def user_two_update():
    user = UserUpdate(
        email="new_email@test.com",
        first_name="Ben",
        last_name="Stiller"
    ).dict()
    return user


@pytest.fixture()
def assign_user_to_reading_list(db_session):
    db = db_session

    # create Author
    author = Author(
        id=1,
        first_name="Stephen",
        last_name="King"
    )


    # create Book One
    book_one = Book(
        id=1,
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
        id=2,
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
        title=f"books to read",
        books=[book_one.title, book_two.title],
        user_email="new_email@test.com"
    ).dict()

    return reading_list


def test_create_user(client, user_one):
    
    response = client.post("/users/", json=user_one)
    assert response.status_code == 201
    data = response.json()

    assert data["id"] == 1
    assert data["email"] == "user_one@test.com"
    assert data["first_name"] == "Elaine"
    assert data["last_name"] == "Benes"


def test_get_user(client, user_two):
    
    response = client.get("/users/2")
    assert response.status_code == 200
    data = response.json()

    assert data["id"] == 2
    assert data["email"] == "user_two@test.com"
    assert data["first_name"] == "Jerry"
    assert data["last_name"] == "Seinfeld"
    

def test_create_user_same_email(client, user_three):

    response = client.post("/users/", json=user_three)
    assert response.status_code == 404
    assert response.json() == {"detail": "Please use different email address"}


def test_update_user(client, user_two_update):
    
    response = client.put("/users/2", json=user_two_update)
    data = response.json()

    assert data["id"] == 2
    assert data["email"] == "new_email@test.com"
    assert data["first_name"] == "Ben"
    assert data["last_name"] == "Stiller"


def test_delete_user(client):

    response = client.delete("/users/1")
    assert response.json() == {"message": "Elaine Benes was deleted"}


def test_delete_user_not_exist(client):
    
    response = client.delete("/users/100")
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


def test_assign_user_to_reading_list(client, assign_user_to_reading_list):

    response = client.post("/lists/", json=assign_user_to_reading_list)
    assert response.status_code == 201
    data = response.json()

    assert data["id"] == 1
    assert data["title"] == "books to read"
    assert data["books"][0]["title"] == "It"
    assert data["books"][1]["title"] == "The Shining"
    assert data["user_id"] == 2
