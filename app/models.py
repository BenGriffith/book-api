from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel
from sqlmodel import SQLModel, Field


class BooksBase(SQLModel):
    title: str
    authors: str


class Books(BooksBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class BooksRead(BooksBase):
    id: int


class BooksUpdate(BooksBase):
    title: str
    authors: str


# class Book(BaseModel):

#     id: int
#     title: str
#     authors: list[str]
#     publisher: str
#     published_date: date
#     description: str
#     page_count: int
#     categories: list[str]
#     average_rating: float
#     ratings_count: int
#     url: str