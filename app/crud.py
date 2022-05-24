from turtle import title
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound

from models import Author, Book, ReadingList
from schemas import BookCreate, BookUpdate, ReadingListCreate


def write_book(db: Session, book: BookCreate):

    authors = []
    for author in book.authors:

        first_name = author.first_name
        last_name = author.last_name
        
        try:
            db_author = db.query(Author).filter(Author.first_name == first_name, Author.last_name == last_name).one()
        except NoResultFound:
            db_author = None

        if db_author is None:
            db_author = Author(first_name=first_name, last_name=last_name)

        authors.append(db_author)

    db_book = Book(
        title=book.title,
        authors=authors,
        publisher=book.publisher,
        published_date=book.published_date,
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

    book.publisher = update_data["publisher"]
    book.published_date = update_data["published_date"]
    book.description = update_data["description"]
    book.average_rating = update_data["average_rating"]

    db.commit()
    db.refresh(book)

    return book


def delete_book(db: Session, book: Book):
    db.delete(book)
    db.commit()
    return {"ok": True}


def write_list(db: Session, reading_list: ReadingListCreate):

    books = []
    for book in reading_list.books:

        db_book = db.query(Book).filter(Book.title == book).first()

        if db_book is None:
            db_book = Book(title=book)

        books.append(db_book)

    db_list = ReadingList(
        title = reading_list.title,
        books = books
    )

    db.add_all(books + [db_list])
    db.commit()
    db.refresh(db_list)

    return db_list

