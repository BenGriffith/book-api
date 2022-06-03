from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app import crud
from app import models
from app.schemas import User, UserCreate, UserUpdate, Author, AuthorCreate, AuthorUpdate, Book, BookCreate, BookUpdate, ReadingList, ReadingListCreate
from app.db import SessionLocal, engine


app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def on_startup():
    models.Base.metadata.create_all(bind=engine)


@app.post("/users/", response_model=User, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return crud.write_user(db=db, user=user)


@app.get("/users/{user_id}", response_model=User, status_code=200)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.read_user(db=db, user_id=user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@app.put("/users/{user_id}")
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    existing_user = crud.read_user(db=db, user_id=user_id)

    if existing_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return crud.update_user(db=db, user=existing_user, updates=user)


@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.read_user(db=db, user_id=user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return crud.delete_user(db=db, user=user)


@app.post("/authors/", response_model=Author, status_code=201)
def create_author(author: AuthorCreate, db: Session = Depends(get_db)):
    return crud.write_author(db=db, author=author)


@app.get("/authors/", response_model=list[Author], status_code=200)
def get_authors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    authors = crud.read_authors(db=db, skip=skip, limit=limit)
    return authors


@app.get("/authors/{author_id}", response_model=Author, status_code=200)
def get_author(author_id: int, db: Session = Depends(get_db)):
    author = crud.read_author(db=db, author_id=author_id)

    if author is None:
        raise HTTPException(status_code=404, detail="Author not found")

    return author


@app.patch("/authors/{author_id}")
def update_author(author_id: int, author: AuthorUpdate, db: Session = Depends(get_db)):
    existing_author = crud.read_author(db=db, author_id=author_id)

    if existing_author is None:
        raise HTTPException(status_code=404, detail="Author not found")

    return crud.update_author(db=db, author=existing_author, updates=author)


@app.delete("/authors/{author_id}")
def delete_author(author_id: int, db: Session = Depends(get_db)):
    author = crud.read_author(db=db, author_id=author_id)

    if author is None:
        raise HTTPException(status_code=404, detail="Author not found")

    return crud.delete_author(db=db, author=author)

   
@app.post("/books/", response_model=Book, status_code=201)
def create_book(book: BookCreate, db: Session = Depends(get_db)):    
    return crud.write_book(db=db, book=book)


@app.get("/books/", response_model=list[Book], status_code=200)
def get_books(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    books = crud.read_books(db=db, skip=skip, limit=limit)
    return books


@app.get("/books/{book_id}", response_model=Book, status_code=200)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = crud.read_book(db=db, book_id=book_id)

    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    return book


@app.patch("/books/{book_id}")
def update_book(book_id: int, book: BookUpdate, db: Session = Depends(get_db)):
    existing_book = crud.read_book(db=db, book_id=book_id)

    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    return crud.update_book(db=db, book=existing_book, updates=book)


@app.delete("/books/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = crud.read_book(db=db, book_id=book_id)

    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    return crud.delete_book(db=db, book=book)


@app.post("/lists/", response_model=ReadingList, status_code=201)
def create_list(reading_list: ReadingListCreate, db: Session = Depends(get_db)):
    user_id = None
    if reading_list.user_email:
        user_id = crud.get_user_id(db=db, user_email=reading_list.user_email)

    return crud.write_list(db=db, user_id=user_id, reading_list=reading_list)


@app.get("/lists/{list_id}", response_model=ReadingList, status_code=200)
def get_list(list_id: int, db: Session = Depends(get_db)):
    reading_list = crud.read_list(db=db, list_id=list_id)

    if reading_list is None:
        raise HTTPException(status_code=404, detail="Reading List not found")

    return reading_list


@app.delete("/lists/{list_id}")
def delete_list(list_id: int, db: Session = Depends(get_db)):
    reading_list = crud.read_list(db=db, list_id=list_id)

    if reading_list is None:
        raise HTTPException(status_code=404, detail="Reading List not found")

    return crud.delete_list(db=db, reading_list=reading_list)