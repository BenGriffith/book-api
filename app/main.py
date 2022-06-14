from datetime import datetime, timedelta

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy_utils import database_exists, create_database
from jose import JWTError, jwt

from app import crud
from app import models
from app import schemas
from app.db import SessionLocal, engine, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

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
    return crud.pwd_context.verify(plain_password, password)


def get_password_hash(password):
    return crud.pwd_context.hash(password)


def authenticate_user(username: str, password: str, db: Session = Depends(get_db)):
    user = crud.get_user(db=db, username=username)

    if user is None:
        return False
    if not verify_password(password, user.password):
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
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = decode_token(db=db, token=token_data.username)

    if user is None:
        raise credentials_exception

    return user


@app.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(username=form_data.username, password=form_data.password, db=db)
    if not user:
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


@app.get("/users/me", response_model=schemas.User)
def get_users_me(current_user: schemas.User = Depends(get_current_user)):
    return current_user
    

@app.post("/users/", response_model=schemas.User, status_code=201)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.write_user(db=db, user=user)


@app.get("/users/{user_id}", response_model=schemas.User, status_code=200)
def get_user(user_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    user = crud.read_user(db=db, user_id=user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@app.put("/users/{user_id}")
def update_user(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    existing_user = crud.read_user(db=db, user_id=user_id)

    if existing_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return crud.update_user(db=db, user=existing_user, updates=user)


@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    user = crud.read_user(db=db, user_id=user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return crud.delete_user(db=db, user=user)

   
@app.post("/books/", response_model=schemas.Book, status_code=201)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):    
    return crud.write_book(db=db, book=book, user_id=current_user.id)


@app.get("/books/", response_model=list[schemas.Book], status_code=200)
def get_books(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    books = crud.read_books(db=db, skip=skip, limit=limit)
    return books


@app.get("/books/{book_id}", response_model=schemas.Book, status_code=200)
def get_book(book_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    book = crud.read_book(db=db, book_id=book_id)

    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    return book


@app.patch("/books/{book_id}")
def update_book(book_id: int, book: schemas.BookUpdate, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    existing_book = crud.read_book(db=db, book_id=book_id)

    if existing_book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    return crud.update_book(db=db, book=existing_book, updates=book)


@app.delete("/books/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    book = crud.read_book(db=db, book_id=book_id)

    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    return crud.delete_book(db=db, book=book)


@app.post("/lists/", response_model=schemas.ReadingList, status_code=201)
def create_list(reading_list: schemas.ReadingListCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):

    return crud.write_list(db=db, user_id=current_user.id, reading_list=reading_list)


@app.get("/lists/{list_id}", response_model=schemas.ReadingList, status_code=200)
def get_list(list_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    reading_list = crud.read_list(db=db, list_id=list_id)

    if reading_list is None:
        raise HTTPException(status_code=404, detail="Reading List not found")

    return reading_list


@app.delete("/lists/{list_id}")
def delete_list(list_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    reading_list = crud.read_list(db=db, list_id=list_id)

    if reading_list is None:
        raise HTTPException(status_code=404, detail="Reading List not found")

    return crud.delete_list(db=db, reading_list=reading_list)