from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from config import db_credentials



# DATABASE_URL = 'postgresql://{username}:{password}@localhost/{dbname}'

DATABASE_URL = f"postgresql://{db_credentials.db_username}:{db_credentials.db_password}@{db_credentials.db_host}/{db_credentials.db_name}"   

engine = create_engine(DATABASE_URL, pool_size = 10, max_overflow = 20, echo = False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
