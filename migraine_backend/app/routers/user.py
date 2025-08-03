from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..schemas.user import UserEmailUpdate, UserPasswordUpdate, UserProfileResponse
from ..crud import user as crud_user
from ..dependencies.auth import get_db, get_current_user
from ..models.user import User
from ..utils.security import get_password_hash
from pydantic import BaseModel

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserProfileResponse)
def get_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return crud_user.get_user_profile(db, current_user)

@router.put("/me/email")
def update_email(
    email_update: UserEmailUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # E-posta zaten kullanılıyor mu kontrolü
    existing = crud_user.get_user_by_email(db, email_update.email)
    if existing and existing.id != current_user.id:
        raise HTTPException(status_code=400, detail="Bu e-posta zaten kullanılıyor.")
    updated = crud_user.update_user_email(db, current_user, email_update)
    return {"message": "E-posta başarıyla güncellendi.", "email": updated.email}

class UserPasswordUpdate(BaseModel):
    new_password: str

@router.put("/me/password")
def update_password(
    password_update: UserPasswordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    current_user.hashed_password = get_password_hash(password_update.new_password)
    db.commit()
    return {"message": "Şifre başarıyla güncellendi."}
