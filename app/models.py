from datetime import date, datetime
from typing import Optional, List, Dict
from pydantic import BaseModel


class Book(BaseModel):

    id: int
    title: str
    authors: List[str]
    # publisher: str
    # published_date: date
    # description: str
    # page_count: int
    # categories: List[str]
    # average_rating: float
    # ratings_count: int
    # url: str