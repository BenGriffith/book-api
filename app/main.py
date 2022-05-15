from sqlmodel import Session, select
from fastapi import Depends, FastAPI, HTTPException

from app.db import get_session, create_db_and_tables
from app.models import Books, BooksRead, BooksUpdate


app = FastAPI()


@app.on_event("startup")
def on_startup():

    create_db_and_tables()


@app.get("/")
def root():

    return dict(message = "Welcome to the Book API!")


@app.get("/books/", response_model=list[Books], status_code=200)
def get_books(*, session: Session = Depends(get_session)):

        books = session.exec(select(Books)).all()
        return books


@app.get("/books/{book_id}", response_model=BooksRead, status_code=200)
def get_book(*, session: Session = Depends(get_session), book_id: int):

    book = session.get(Books, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@app.post("/books/", response_model=Books, status_code=201)
def create_book(*, session: Session = Depends(get_session), book: Books):

    session.add(book)
    session.commit()
    session.refresh(book)

    return book


@app.patch("/books/{book_id}", response_model=BooksRead)
def update_book(*, session: Session = Depends(get_session), book_id: int, book: BooksUpdate):

    book_record = session.get(Books, book_id)
    if book_record is None:
        raise HTTPException(status_code=404, detail="Book not found")

    book_record.title = book.title
    book_record.authors = book.authors

    session.add(book_record)
    session.commit()
    session.refresh(book_record)

    return book_record


@app.delete("/books/{book_id}")
def delete_book(*, session: Session = Depends(get_session), book_id: int):

    book = session.get(Books, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    session.delete(book)
    session.commit()

    return {"ok": True}