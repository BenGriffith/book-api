from typing import Optional, List
from datetime import date

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


class BookBase(BaseModel):
    title: str
    publisher: Optional[str] = None
    published_date: Optional[date] = None
    description: Optional[str] = None
    # categories: list[CategoryBase]
    page_count: Optional[int] = 0
    average_rating: Optional[float] = None
    authors: Optional[list[AuthorBase]] = None


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
    published_date: Optional[date] = None
    description: Optional[str] = None
    average_rating: Optional[float] = None


class ReadingListBase(BaseModel):
    title: str


class ReadingListCreate(ReadingListBase):
    books: list[str]


class ReadingList(ReadingListBase):
    id: int
    books: list[Book]

    class Config:
        orm_mode = True