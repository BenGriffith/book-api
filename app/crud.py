from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from fastapi import HTTPException

from models import Author, Book, ReadingList
from schemas import AuthorCreate, BookCreate, BookUpdate, ReadingListCreate


def write_author(db: Session, author: AuthorCreate):

    author = Author(first_name=author.first_name.capitalize(), last_name=author.last_name.capitalize())
    db.add(author)
    db.commit()
    db.refresh(author)

    return author


def write_book(db: Session, book: BookCreate):

    authors = []
    for author in book.authors:

        first_name = author.first_name.capitalize()
        last_name = author.last_name.capitalize()
        
        try:
            db_author = db.query(Author).filter(Author.first_name == first_name, Author.last_name == last_name).one()
        except NoResultFound:
            db_author = None

        if db_author is None:
            raise HTTPException(status_code=404, detail=f"Author not found. Please create an Author entry for {first_name} {last_name}")
        else:
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
    return {"message": f"{book.title} was deleted"}


def write_list(db: Session, reading_list: ReadingListCreate):

    books = []
    for book in reading_list.books:

        db_book = db.query(Book).filter(Book.title == book).first()

        if db_book is None:
            raise HTTPException(status_code=404, detail=f"Book not found. Please create a Book entry for {book.capitalize()}")
        else:
            books.append(db_book)


    db_list = ReadingList(
        title = reading_list.title,
        books = books
    )

    db.add_all(books + [db_list])
    db.commit()
    db.refresh(db_list)

    return db_list


def delete_list(db: Session, reading_list: ReadingList):
    db.delete(reading_list)
    db.commit()
    return {"message": f"{reading_list.title} was deleted"}