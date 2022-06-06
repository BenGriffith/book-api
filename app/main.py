from datetime import datetime, timedelta

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy_utils import database_exists, create_database
from passlib.context import CryptContext
from jose import JWTError, jwt

from app import crud
from app import models
from app.schemas import User, UserCreate, UserUpdate, Author, AuthorCreate, AuthorUpdate, Book, BookCreate, BookUpdate, ReadingList, ReadingListCreate, Token, TokenData
from app.db import SessionLocal, engine, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def on_startup():
    if not database_exists(engine.url):
        create_database(engine.url)

    models.Base.metadata.create_all(bind=engine)


def verify_password(plain_password, password):
    return pwd_context.verify(plain_password, password)


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str, db: Session = Depends(get_db)):
    user = crud.get_user(db=db, username=username)

    if user is None:
        return False
    if verify_password(password, user.password) is None:
        return False

    return user


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(db: Session, token):
    user = crud.get_user(db=db, username=token)
    if user is None:
        return None
    
    return user


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = decode_token(db=db, token=token_data.username)

    if user is None:
        raise credentials_exception

    return user


@app.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(username=form_data.username, password=form_data.password, db=db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=User)
def get_users_me(current_user: User = Depends(get_current_user)):
    return current_user
    

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

    if reading_list.username:
        user_id = crud.get_user(db=db, username=reading_list.username).id

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