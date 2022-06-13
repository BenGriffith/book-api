from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from sqlalchemy import func
from fastapi import HTTPException
from passlib.context import CryptContext

from app.models import User, Book, ReadingList
from app.schemas import UserCreate, UserUpdate, BookCreate, BookUpdate, ReadingListCreate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def write_user(db: Session, user: UserCreate):

    username = db.query(User).filter(
        func.lower(User.username) == func.lower(user.username)
    ).first()

    if username:
        raise HTTPException(status_code=400, detail="Username already exists. Please use different username")

    email = db.query(User).filter(
        func.lower(User.email) == func.lower(user.email)
        ).first()

    if email:
        raise HTTPException(status_code=400, detail="Email address already exists. Please use different email address")

    user = User(
        username=user.username,
        email=user.email,
        password=pwd_context.hash(user.password),
        first_name=user.first_name,
        last_name=user.last_name
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def read_user(db: Session, user_id: int):
    user = db.get(User, user_id)
    return user


def get_user(db: Session, username: str):


    try:
        user = db.query(User).filter(
            func.lower(User.username) == func.lower(username)
        ).one()
    except NoResultFound:
        return None

    return read_user(db=db, user_id=user.id)


def update_user(db: Session, user: User, updates: UserUpdate):
    update_data = updates.dict(exclude_unset=True)

    user.username = update_data["username"]
    user.email = update_data["email"]
    user.password = pwd_context.hash(update_data["password"])
    user.first_name = update_data["first_name"]
    user.last_name = update_data["last_name"]

    db.commit()
    db.refresh(user)

    return user


def delete_user(db: Session, user: User):
    db.delete(user)
    db.commit()
    return {"message": f"{user.first_name} {user.last_name} was deleted"}


def get_google_book(db: Session, book_id: str):

    db_book = db.query(Book).filter(
        Book.google_books_id == book_id
    ).first()

    return db_book
    

def write_book(db: Session, book: BookCreate, user_id: User):

    db_book = Book( 
        title=book.title.title(),
        authors=book.authors,
        publisher=book.publisher.title(),
        published_date=book.published_date,
        description=book.description,
        page_count=book.page_count,
        average_rating=book.average_rating,
        google_books_id=book.google_books_id,
        user_id=user_id,
    )

    db.add(db_book)
    db.commit()
    db.refresh(db_book)
        
    return db_book


def read_books(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Book).offset(skip).limit(limit).all()


def read_book(db: Session, book_id: int):
    db_book = db.get(Book, book_id)
    return db_book


def update_book(db: Session, book: Book, updates: BookUpdate):    
    update_data = updates.dict(exclude_unset=True)

    book.publisher = update_data["publisher"].title()
    book.published_date = update_data["published_date"]
    book.description = update_data["description"]
    book.average_rating = update_data["average_rating"]

    db.commit()
    db.refresh(book)

    return book


def delete_book(db: Session, book: Book):
    db.delete(book)
    db.commit()
    return {"message": f"{book.title} was deleted"}


def write_list(db: Session, user_id: int, reading_list: ReadingListCreate):

    books = []
    for book in reading_list.books:

        book = book.title()

        db_book = db.query(Book).filter(
            func.lower(Book.title) == func.lower(book)
            ).first()

        if db_book is None:
            raise HTTPException(status_code=404, detail=f"Book not found. Please create a Book entry for {book}")

        books.append(db_book)

    db_list = ReadingList(
        title = reading_list.title,
        books = books,
        user_id = user_id
    )

    db.add_all(books + [db_list])
    db.commit()
    db.refresh(db_list)

    return db_list


def read_list(db: Session, list_id: int):
    reading_list = db.get(ReadingList, list_id)
    return reading_list


def delete_list(db: Session, reading_list: ReadingList):
    db.delete(reading_list)
    db.commit()
    return {"message": f"{reading_list.title} was deleted"}