import jwt
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv


load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=2)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)