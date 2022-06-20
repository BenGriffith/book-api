from decouple import config
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DEBUG = config("DEBUG", default=False, cast=bool)
DATABASE_URL = config("DATABASE_URL", cast=str)
SECRET_KEY = config("SECRET_KEY", cast=str)
ALGORITHM = config("ALGORITHM", cast=str)
ACCESS_TOKEN_EXPIRE_MINUTES = config("ACCESS_TOKEN_EXPIRE_MINUTES", cast=int)
CHECK_SAME_THREAD = config("CHECK_SAME_THREAD", default=False, cast=bool)

if CHECK_SAME_THREAD:
    kwargs = {"connect_args": {"check_same_thread": False}}
else:
    kwargs = {}
engine = create_engine(DATABASE_URL, echo=DEBUG, **kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
