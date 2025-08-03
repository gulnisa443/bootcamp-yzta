from sqlalchemy.orm import Session
from ..models.user import User
from ..schemas.user import UserCreate, UserEmailUpdate, UserPasswordUpdate, UserProfileResponse
from ..utils.security import hash_password
from sqlalchemy import func
from ..models.migraine_entry import MigraineEntry
from datetime import datetime

def create_user(db: Session, user: UserCreate):
    hashed_pw = hash_password(user.password)
    db_user = User(name=user.name, email=user.email, hashed_password=hashed_pw)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def update_user_email(db: Session, user: User, email_update: UserEmailUpdate):
    user.email = email_update.email  # type: ignore
    db.commit()
    db.refresh(user)
    return user

def update_user_password(db: Session, user: User, password_update: UserPasswordUpdate):
    user.hashed_password = hash_password(password_update.password)  # type: ignore
    db.commit()
    db.refresh(user)
    return user

def get_user_profile(db: Session, user: User) -> UserProfileResponse:
    total_entries = db.query(func.count(MigraineEntry.id)).filter(MigraineEntry.user_id == user.id).scalar()
    last_login = None  # Eğer login logu tutuluyorsa eklenebilir
    # Use getattr to ensure we get the value, not the Column object
    user_id = getattr(user, 'id', None)
    name = getattr(user, 'name', None)
    email = getattr(user, 'email', None)
    created_at_val = getattr(user, 'created_at', None)
    if user_id is None or email is None:
        raise ValueError("User id or email is None, cannot build profile response.")
    if created_at_val and not isinstance(created_at_val, str):
        created_at = created_at_val.strftime("%d %B %Y %H:%M")
    else:
        created_at = str(created_at_val) if created_at_val else ""
    return UserProfileResponse(
        id=user_id,
        name=name,
        email=email,
        created_at=created_at,
        total_entries=total_entries,
        last_login=last_login
    )
