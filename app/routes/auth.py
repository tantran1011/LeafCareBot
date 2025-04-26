from fastapi import APIRouter, HTTPException, Depends, Request
from app.models.user import Login, Register, UserRespone
from app.config import get_db
from sqlalchemy.orm import Session
from app.models.database import User
from app.core.logger import auth_logger

router = APIRouter()

@router.post('/register', response_model=UserRespone)
def register(user: Register, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if not existing_user:
        new_user = User(username = user.username, password=user.password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return UserRespone(username=user.username)
    auth_logger.warning(f"Username {existing_user.username} already registered")
    raise HTTPException(status_code=404, detail="Username already registered")


@router.post('/login', response_model=UserRespone)
def login(request: Request, user: Login, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user:
        auth_logger.warning("Invalid Credentials")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if db_user.password != user.password:
        auth_logger.warning("Invalid Password")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    auth_logger.info(f"{user.username} Sucessfull Login")
    request.session["user_id"] = db_user.id
    return UserRespone(username=db_user.username)


@router.get('/users')
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users