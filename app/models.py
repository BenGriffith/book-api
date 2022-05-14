from datetime import date, datetime
from typing import Optional

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