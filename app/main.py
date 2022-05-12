from http.client import HTTPException
from fastapi import FastAPI, HTTPException

from app.models import Book

app = FastAPI()

fake_db = {}

@app.get("/")
def root():
    return dict(message = "Welcome to the Book API!")


@app.get("/books/{book_id}", response_model=Book, status_code=200)
def get_book(book_id: int):
    return fake_db[book_id]


@app.post("/books/", response_model=Book, status_code=201)
def create_book(book: Book):
    fake_db[book.id] = book
    return book


@app.put("/books/{book_id}", response_model=Book)
def update_book(book_id: int, book: Book):
    if book_id in fake_db:
        fake_db[book.id] = book
        return fake_db[book.id]
    else:
        raise HTTPException(status_code=404, detail="Book not found")


@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    if book_id in fake_db:
        del fake_db[book_id]
        return {"ok": True}
    else:
        raise HTTPException(status_code=404, detail="Book not found")