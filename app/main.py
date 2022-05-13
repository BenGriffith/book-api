from sqlmodel import SQLModel, Session, select
from fastapi import FastAPI, HTTPException

from db import create_db_and_tables, engine
from models import Books, BooksRead, BooksUpdate


app = FastAPI()

# fake_db = {}


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


# @app.get("/")
# def root():
#     return dict(message = "Welcome to the Book API!")


@app.get("/books/", response_model=list[Books], status_code=200)
def get_books():
    with Session(engine) as session:
        books = session.exec(select(Books)).all()
        return books


# @app.get("/books/{book_id}", response_model=Book, status_code=200)
# def get_book(book_id: int):
#     return fake_db[book_id]


@app.get("/books/{book_id}", response_model=BooksRead, status_code=200)
def get_book(book_id: int):
    with Session(engine) as session:
        book = session.get(Books, book_id)
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        return book


# @app.post("/books/", response_model=Book, status_code=201)
# def create_book(book: Book):
#     fake_db[book.id] = book
#     return book


@app.post("/books/", response_model=Books, status_code=201)
def create_book(book: Books):
    with Session(engine) as session:
        session.add(book)
        session.commit()
        session.refresh(book)
        return book


# @app.put("/books/{book_id}", response_model=Book)
# def update_book(book_id: int, book: Book):
#     if book_id not in fake_db:
#         raise HTTPException(status_code=404, detail="Book not found")
    
#     fake_db[book.id] = book
#     return fake_db[book.id]


@app.patch("/books/{book_id}", response_model=BooksRead)
def update_book(book_id: int, book: BooksUpdate):
    with Session(engine) as session:
        book_record = session.get(Books, book_id)
        if not book_record:
            raise HTTPException(status_code=404, detail="Book not found")
        book_data = book.dict(exclude_unset=True)
        for key, value in book_data.items():
            setattr(book_record, key, value)
        session.add(book_record)
        session.commit()
        session.refresh(book_record)
        return book_record


# @app.delete("/books/{book_id}")
# def delete_book(book_id: int):
#     if not book_id in fake_db:
#         raise HTTPException(status_code=404, detail="Book not found")

#     del fake_db[book_id]
#     return {"ok": True}