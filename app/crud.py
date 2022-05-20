from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound

from models import Author, Book
from schemas import AuthorCreate, BookCreate


def create_book(db: Session, book: BookCreate):

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

    db_book = Book(title=book.title)
    db_book.authors = authors
    db.add_all(authors + [db_book])
    db.commit()
    db.refresh(db_book)
        
    return db_book


def get_books(db: Session, skip: int = 0, limit: int = 100):

    return db.query(Book).offset(skip).limit(limit).all()


def get_book(db: Session, book_id: int):

    db_book = db.get(Book, book_id)
    return db_book


def create_author(db: Session, author: AuthorCreate):
    
    db_author = Author(first_name=author.first_name, last_name=author.last_name)
    db.add(db_author)
    db.commit()
    db.refresh(db_author)

    return db_author