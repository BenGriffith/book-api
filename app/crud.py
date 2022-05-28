from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from sqlalchemy import func
from fastapi import HTTPException

from .models import Author, Book, ReadingList
from .schemas import AuthorCreate, AuthorUpdate, BookCreate, BookUpdate, ReadingListCreate


def write_author(db: Session, author: AuthorCreate):

    author = Author(first_name=author.first_name.capitalize(), last_name=author.last_name.capitalize())
    db.add(author)
    db.commit()
    db.refresh(author)

    return author


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


    db_list = ReadingList(
        title = reading_list.title,
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