from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str = None


class BookBase(BaseModel):
    title: str
    authors: Optional[str] = None
    publisher: Optional[str] = None
    published_date: Optional[str] = None
    description: Optional[str] = None
    page_count: Optional[int] = 0
    average_rating: Optional[float] = None
    google_books_id: Optional[str] = None
    user_id: int


class BookBaseReadingList(BaseModel):
    title: str


class BookCreate(BookBase):
    pass


class Book(BookBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True


class BookUpdate(BaseModel):
    publisher: Optional[str] = None
    published_date: Optional[str] = None
    description: Optional[str] = None
    average_rating: Optional[float] = None


class ReadingListBase(BaseModel):
    title: str


class ReadingListCreate(ReadingListBase):
    books: list[str]


class ReadingList(ReadingListBase):
    id: int
    user_id: Optional[int]
    books: list[Book]

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    reading_lists: Optional[list[ReadingList]] = None

    class Config:
        orm_mode = True


class UserUpdate(UserBase):
    password: str