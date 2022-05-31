from decouple import config
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DEBUG = config("DEBUG", default=False, cast=bool)
DEV = config("DEV")
PROD = config("PROD")

dev_engine = create_engine(DEV, echo=DEBUG)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=dev_engine)

prod_engine = create_engine(PROD, echo=DEBUG)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=prod_engine)

Base = declarative_base()