from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class Book(BaseModel):

    id: int
    title: str
    authors: list[str]
    # publisher: str
    # published_date: date
    # description: str
    # page_count: int
    # categories: list[str]
    # average_rating: float
    # ratings_count: int
    # url: str