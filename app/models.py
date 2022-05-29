from sqlalchemy import ForeignKey, Table, Column, Integer, String, Float
from sqlalchemy.orm import relationship

from app.db import Base


BookAuthor = Table(
    "book_author",
    Base.metadata,
    Column("book_id", Integer, ForeignKey("books.id")),
    Column("author_id", Integer, ForeignKey("authors.id"))
)

BookList = Table(
    "book_reading_list",
    Base.metadata,
    Column("list_id", Integer, ForeignKey("reading_lists.id")),
    Column("book_id", Integer, ForeignKey("books.id"))
)


class Book(Base):

    __tablename__ = "books"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    publisher = Column(String)
    published_year = Column(Integer)
    description = Column(String)
    page_count = Column(Integer)
    average_rating = Column(Float)

    authors = relationship("Author", secondary="book_author", back_populates="books")
    reading_lists = relationship("ReadingList", secondary="book_reading_list", back_populates="books")


class Author(Base):

    __tablename__ = "authors"

    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)

    books = relationship("Book", secondary="book_author", back_populates="authors")


class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)


class ReadingList(Base):

    __tablename__ = "reading_lists"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User")
    books = relationship("Book", secondary="book_reading_list", back_populates="reading_lists")