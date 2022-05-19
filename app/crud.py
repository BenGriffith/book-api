from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound

from models import Author, Book
from schemas import AuthorCreate, BookCreate


def create_author(db: Session, author: AuthorCreate):
    
    db_author = Author(first_name=author.first_name, last_name=author.last_name)
    db.add(db_author)
    db.commit()
    db.refresh(db_author)

    return db_author


def create_book(db: Session, book: BookCreate):

    for author in book.authors:

        first_name = author.first_name
        last_name = author.last_name
        try:
            result = db.query(Author).filter(Author.first_name == first_name, Author.last_name == last_name).one() # unique constraint on first last names

        except NoResultFound:
            db_author = Author(first_name=first_name, last_name=last_name)
            db_book = Book(title=book.title)
            db_book.authors = [db_author]

            db.add_all([db_author, db_book])
            db.commit()
            db.refresh(db_book)

    return db_book