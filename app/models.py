from sqlalchemy import ForeignKey, Table, Column, Integer, String, Float
from sqlalchemy.orm import relationship

from app.db import Base


BookList = Table(
    "book_reading_list",
    Base.metadata,
    Column("list_id", Integer, ForeignKey("reading_lists.id")),
    Column("book_id", Integer, ForeignKey("books.id"))
)


class Book(Base):

    __tablename__ = "books"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    authors = Column(String)
    publisher = Column(String)
    published_date = Column(String)
    description = Column(String)
    page_count = Column(Integer)
    average_rating = Column(Float)
    google_books_id = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User")
    reading_lists = relationship("ReadingList", secondary="book_reading_list", back_populates="books")


class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(String)
    first_name = Column(String)
    last_name = Column(String)


class ReadingList(Base):

    __tablename__ = "reading_lists"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User")
    books = relationship("Book", secondary="book_reading_list", back_populates="reading_lists")