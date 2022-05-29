from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from sqlalchemy import func
from fastapi import HTTPException

from .models import User, Author, Book, ReadingList
from .schemas import UserCreate, UserUpdate, AuthorCreate, AuthorUpdate, BookCreate, BookUpdate, ReadingListCreate


def write_user(db: Session, user: UserCreate):

    email = db.query(User).filter(
        func.lower(User.email) == func.lower(user.email)
        ).first()

    if email:
        raise HTTPException(status_code=404, detail="Please use different email address")

    user = User(
        email=user.email,
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


def update_user(db: Session, user: User, updates: UserUpdate):
    update_data = updates.dict(exclude_unset=True)

    user.email = update_data["email"]
    user.first_name = update_data["first_name"]
    user.last_name = update_data["last_name"]

    db.commit()
    db.refresh(user)

    return user


def delete_user(db: Session, user: User):
    db.delete(user)
    db.commit()
    return {"message": f"{user.first_name} {user.last_name} was deleted"}


def write_author(db: Session, author: AuthorCreate):

    author = Author(first_name=author.first_name.capitalize(), last_name=author.last_name.capitalize())
    db.add(author)
    db.commit()
    db.refresh(author)

    return author


def read_author(db: Session, author_id: int):
    author = db.get(Author, author_id)
    return author


def read_authors(db: Session, skip: int, limit: int):
    return db.query(Author).offset(skip).limit(limit).all()


def update_author(db: Session, author: Author, updates: AuthorUpdate):
    update_data = updates.dict(exclude_unset=True)

    author.first_name = update_data["first_name"].capitalize()
    author.last_name = update_data["last_name"].capitalize()

    db.commit()
    db.refresh(author)

    return author


def delete_author(db: Session, author: Author):
    db.delete(author)
    db.commit()
    return {"message": f"{author.first_name} {author.last_name} was deleted"}


def write_book(db: Session, book: BookCreate):

    authors = []
    for author in book.authors:

        first_name = author.first_name
        last_name = author.last_name

        try:
            db_author = db.query(Author).filter(
                func.lower(Author.first_name) == func.lower(first_name), 
                func.lower(Author.last_name) == func.lower(last_name)
                ).one()
        except NoResultFound:
            db_author = None

        if db_author is None:
            raise HTTPException(status_code=404, detail=f"Author not found. Please create an Author entry for {first_name} {last_name}")

        authors.append(db_author)

    db_book = Book(
        title=book.title.title(),
        authors=authors,
        publisher=book.publisher.title(),
        published_year=book.published_year,
        description=book.description,
        page_count=book.page_count,
        average_rating=book.average_rating
    )

    db.add_all(authors + [db_book])
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
    book.published_year = update_data["published_year"]
    book.description = update_data["description"]
    book.average_rating = update_data["average_rating"]

    db.commit()
    db.refresh(book)

    return book


def delete_book(db: Session, book: Book):
    db.delete(book)
    db.commit()
    return {"message": f"{book.title} was deleted"}


def write_list(db: Session, reading_list: ReadingListCreate):

    books = []
    for book in reading_list.books:

        book = book.title()

        db_book = db.query(Book).filter(
            func.lower(Book.title) == func.lower(book)
            ).first()

        if db_book is None:
            raise HTTPException(status_code=404, detail=f"Book not found. Please create a Book entry for {book}")

        books.append(db_book)

    db_user = db.query(User).filter(
        func.lower(User.email) == func.lower(reading_list.user_email)
    ).first()

    db_list = ReadingList(
        title = reading_list.title,
        user_id = db_user.id,
        books = books
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