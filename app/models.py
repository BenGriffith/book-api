from sqlalchemy import ForeignKey, Table, Column, Integer, String
from sqlalchemy.orm import relationship

from db import Base


BookAuthor = Table(
    "book_author",
    Base.metadata,
    Column("book_id", Integer, ForeignKey("books.id")),
    Column("author_id", Integer, ForeignKey("authors.id"))
)


class Book(Base):

    __tablename__ = "books"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    authors = relationship("Author", secondary="book_author", back_populates="books")


class Author(Base):

    __tablename__ = "authors"

    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    books = relationship("Book", secondary="book_author", back_populates="authors")