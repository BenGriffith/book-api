from decouple import config
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DEBUG = config("DEBUG", default=False, cast=bool)
DEV = config("DEV")
TEST = config("TEST")

dev_engine = create_engine(DEV, echo=DEBUG)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=dev_engine)


test_engine = create_engine(TEST, echo=DEBUG)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


Base = declarative_base()