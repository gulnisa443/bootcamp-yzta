from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Generator

from ..database import SessionLocal
from .. import models
from ..utils.jwt import verify_access_token
from ..models.user import User

# Token'ı login endpointinden alacağız
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Veritabanı bağlantısını sağlayan fonksiyon
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Giriş yapan kullanıcıyı çözen ve doğrulayan fonksiyon
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Kimlik doğrulama başarısız.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        print("DEBUG: token", token)
        payload = verify_access_token(token)
        print("DEBUG: payload", payload)
        user_id = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
        user_id = int(user_id)
    except Exception:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    return user
