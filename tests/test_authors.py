import pytest
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.models import Author, User
from app.schemas import AuthorCreate, AuthorUpdate


@pytest.fixture()
def author_one():
    author = AuthorCreate(
        first_name="george",
        last_name="costanza"
    ).dict()

    yield author


@pytest.fixture()
def author_two(session: Session):
    db = session
    author = Author(
        first_name="John",
        last_name="Doe"
    )

    db.add(author)
    db.commit()
    yield author


@pytest.fixture()
def author_three(session: Session):
    db = session
    author = Author(
        first_name="Cosmo",
        last_name="Kramer"
    )

    db.add(author)
    db.commit()
    yield author


@pytest.fixture()
def author_four():
    author = AuthorUpdate(
        first_name="Wayne",
        last_name="Knight"
    ).dict()

    yield author


def test_create_author(client: TestClient, author_one: AuthorCreate, current_user: User):

    response = client.post("/authors/", json=author_one, headers=current_user)
    assert response.status_code == 201
    data = response.json()

    assert data["first_name"] == "George"
    assert data["last_name"] == "Costanza"


def test_create_author_locked(client: TestClient, author_one: AuthorCreate):

    response = client.post("/authors/", json=author_one)
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_get_author_two(session: Session, client: TestClient, author_two: Author, current_user: User):

    db_author = session.query(Author).filter(
        Author.first_name == author_two.first_name,
        Author.last_name == author_two.last_name
        ).first()

    response = client.get(f"/authors/{db_author.id}", headers=current_user)
    assert response.status_code == 200
    data = response.json()

    assert data["id"] == db_author.id
    assert data["first_name"] == "John"
    assert data["last_name"] == "Doe"


def test_get_author_two_locked(session: Session, client: TestClient, author_two: Author):

    db_author = session.query(Author).filter(
        Author.first_name == author_two.first_name,
        Author.last_name == author_two.last_name
        ).first()

    response = client.get(f"/authors/{db_author.id}")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_get_author_three(session: Session, client: TestClient, author_three: Author, current_user: User):

    db_author = session.query(Author).filter(
        Author.first_name == author_three.first_name,
        Author.last_name == author_three.last_name
    ).first()

    response = client.get(f"/authors/{db_author.id}", headers=current_user)
    assert response.status_code == 200
    data = response.json()

    assert data["id"] == db_author.id
    assert data["first_name"] == "Cosmo"
    assert data["last_name"] == "Kramer"


def test_get_authors(client: TestClient, author_two: Author, author_three: Author):

    response = client.get("/authors/")
    assert response.status_code == 200
    data = response.json()

    first_names = ["John", "Cosmo"]

    assert len(data) == 2
    for i in range(len(data)):
        assert data[i]["first_name"] == first_names[i]


def test_update_author(session: Session, client: TestClient, author_two: Author, author_four: AuthorUpdate, current_user: User):

    db_author = session.query(Author).filter(
        Author.first_name == author_two.first_name,
        Author.last_name == author_two.last_name
    ).first()

    response = client.patch(f"/authors/{db_author.id}", json=author_four, headers=current_user)
    data = response.json()

    assert data["first_name"] == "Wayne"
    assert data["last_name"] == "Knight"


def test_update_author_locked(session: Session, client: TestClient, author_two: Author, author_four: AuthorUpdate):

    db_author = session.query(Author).filter(
        Author.first_name == author_two.first_name,
        Author.last_name == author_two.last_name
    ).first()

    response = client.patch(f"/authors/{db_author.id}", json=author_four)
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_delete_author(session: Session, client: TestClient, author_three: Author, current_user: User):

    db_author = session.query(Author).filter(
        Author.first_name == author_three.first_name,
        Author.last_name == author_three.last_name
    ).first()

    response = client.delete(f"/authors/{db_author.id}", headers=current_user)
    assert response.json() == {"message": "Cosmo Kramer was deleted"}


def test_delete_author_locked(session: Session, client: TestClient, author_three: Author):

    db_author = session.query(Author).filter(
        Author.first_name == author_three.first_name,
        Author.last_name == author_three.last_name
    ).first()

    response = client.delete(f"/authors/{db_author.id}")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_delete_author_not_exist(client: TestClient, current_user: User):

    response = client.delete("/authors/100", headers=current_user)
    assert response.json() == {"detail": "Author not found"}
