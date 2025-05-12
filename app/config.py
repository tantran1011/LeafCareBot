import os 
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import urllib.parse

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_URL = DATABASE_URL.encode('utf-8').decode('unicode_escape')

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_db():
    db = SessionLocal()
    try:
        yield db 

    finally:
        db.close()