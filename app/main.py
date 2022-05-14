from sqlmodel import Session, select
from fastapi import FastAPI, HTTPException

from db import create_db_and_tables, engine
from models import Books, BooksRead, BooksUpdate


app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/")
def root():
    return dict(message = "Welcome to the Book API!")


@app.get("/books/", response_model=list[Books], status_code=200)
def get_books():

    with Session(engine) as session:
        books = session.exec(select(Books)).all()
        return books


@app.get("/books/{book_id}", response_model=BooksRead, status_code=200)
def get_book(book_id: int):

    with Session(engine) as session:
        book = session.get(Books, book_id)
        if book is None:
            raise HTTPException(status_code=404, detail="Book not found")
        return book


@app.post("/books/", response_model=Books, status_code=201)
def create_book(book: Books):

    with Session(engine) as session:
        session.add(book)
        session.commit()
        session.refresh(book)

        return book


@app.patch("/books/{book_id}", response_model=BooksRead)
def update_book(book_id: int, book: BooksUpdate):

    with Session(engine) as session:
        book_record = session.get(Books, book_id)
        if book_record is None:
            raise HTTPException(status_code=404, detail="Book not found")

        book_record.title = book.title
        book_record.authors = book.authors

        session.add(book_record)
        session.commit()
        session.refresh(book_record)

        return book_record