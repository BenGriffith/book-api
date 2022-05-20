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
    authors: list[AuthorBase]


class BookCreate(BookBase):
    pass


class Book(BookBase):
    id: int
    authors: list[Author]

    class Config:
        orm_mode = True