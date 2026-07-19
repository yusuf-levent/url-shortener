from passlib.context import CryptContext
from jose import jwt,JWTError
from datetime import datetime,timedelta,timezone
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends,HTTPException,status
from sqlalchemy.orm import Session
from database import get_db
from models import User,UserRoles

from config import settings
SECRET_KEY=settings.SECRET_KEY
ACCESS_TOKEN_EXPIRE_MINUTES=settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS=settings.REFRESH_TOKEN_EXPIRE_DAYS
ALGORITHM=settings.ALGORITHM
pwd_context=CryptContext(schemes=["bcrypt"],deprecated="auto")

def hash_password(plain_password):
    return pwd_context.hash(plain_password)
def verify_password(plain_password,hashed_password):
    return pwd_context.verify(plain_password,hashed_password)


def create_access_token(data:dict):
    to_encode=data.copy()
    expire=datetime.now(timezone.utc)+timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire})
    return jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
def create_refresh_token(data:dict):
    to_encode=data.copy()
    expire=datetime.now(timezone.utc)+timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp":expire})
    token= jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return token,expire

outh2_scheme=OAuth2PasswordBearer(tokenUrl="users/login")
def get_current_user(token:str=Depends(outh2_scheme),db:Session=Depends(get_db)):
    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        email=payload.get("email")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="geçersiz token")
        if payload.get("type")!="access":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="invalid token type")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="geçersiz token")
    user=db.query(User).filter(User.email==email).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="kullanıcı yok")
    return user


def require_admin(current_user:User=Depends(get_current_user)):
    role=current_user.role
    if UserRoles.Admin!=role:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="require admin role")
    return current_user

