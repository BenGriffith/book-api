from typing import Optional

from pydantic import BaseModel


class AuthorBase(BaseModel):
    first_name: str
    last_name: str


class AuthorCreate(AuthorBase):
    pass


class Author(AuthorBase):
    id: int

    class Config:
        orm_mode = True


class AuthorUpdate(AuthorBase):
    pass


class BookBase(BaseModel):
    title: str
    publisher: Optional[str] = None
    published_year: Optional[int] = None
    description: Optional[str] = None
    page_count: Optional[int] = 0
    average_rating: Optional[float] = None
    authors: list[AuthorBase]


class BookBaseReadingList(BaseModel):
    title: str


class BookCreate(BookBase):
    pass


class Book(BookBase):
    id: int
    authors: list[Author]

    class Config:
        orm_mode = True


class BookUpdate(BaseModel):
    publisher: Optional[str] = None
    published_year: Optional[int] = None
    description: Optional[str] = None
    average_rating: Optional[float] = None


class ReadingListBase(BaseModel):
    title: str


class ReadingListCreate(ReadingListBase):
    books: list[str]
    user_email: Optional[str] = None


class ReadingList(ReadingListBase):
    id: int
    user_id: int
    books: list[Book]

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str
    first_name: str
    last_name: str


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int
    reading_lists: Optional[list[ReadingList]] = None

    class Config:
        orm_mode = True


class UserUpdate(UserBase):
    pass