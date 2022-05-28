from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


dev_sqlite_file_name = "dev.db"
dev_sqlite_url = f"sqlite:///{dev_sqlite_file_name}"

connect_args = {"check_same_thread": False}
dev_engine = create_engine(dev_sqlite_url, echo=False, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=dev_engine)


test_sqlite_file_name = "test.db"
test_sqlite_url = f"sqlite:///{test_sqlite_file_name}"

test_engine = create_engine(test_sqlite_url, echo=False, connect_args=connect_args)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

Base = declarative_base()