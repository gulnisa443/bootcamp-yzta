from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..schemas.user import UserCreate, UserLogin
from ..crud.user import create_user, get_user_by_email
from ..utils.security import verify_password
from ..database import SessionLocal

router = APIRouter(tags=["auth"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    print(f"🔍 SIGNUP ATTEMPT - Email: {user.email}")
    print(f"📧 Name: {user.name}")
    print(f"🔑 Password: {user.password}")
    
    # Kullanıcı zaten var mı kontrol et
    db_user = get_user_by_email(db, user.email)
    print(f"📋 User already exists: {db_user is not None}")
    
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    try:
        print("🚀 Creating user...")
        created_user = create_user(db, user)
        print(f"✅ User created successfully - ID: {created_user.id}")
        print(f"📧 Created email: {created_user.email}")
        print(f"🔒 Hashed password: {created_user.hashed_password[:20]}...")
        return created_user
    except Exception as e:
        print(f"❌ User creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"User creation failed: {str(e)}")

from ..utils.jwt import create_access_token

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    print(f"🔍 LOGIN ATTEMPT - Email: {user.email}")
    
    # Kullanıcıyı veritabanından bul
    db_user = get_user_by_email(db, user.email)
    
    # DEBUG: Kullanıcı kontrolü
    print(f"📋 User found in DB: {db_user is not None}")
    
    if db_user:
        print(f"✅ DB User ID: {db_user.id}")
        print(f"📧 DB Email: {db_user.email}")
        print(f"🔒 DB Hashed Password: {db_user.hashed_password[:20]}...")  # İlk 20 karakter
        print(f"🔑 Input Password: {user.password}")
        
        # Şifre doğrulama testi
        try:
            password_valid = verify_password(user.password, db_user.hashed_password)
            print(f"🎯 Password verification result: {password_valid}")
        except Exception as e:
            print(f"❌ Password verification error: {str(e)}")
            password_valid = False
    else:
        print("❌ User not found in database")
        print(f"🔍 Searched email: '{user.email}'")
        
        # Tüm kullanıcıları listele (debug için)
        from ..models.user import User
        all_users = db.query(User).all()
        print(f"📊 Total users in DB: {len(all_users)}")
        for u in all_users:
            print(f"   - ID: {u.id}, Email: '{u.email}'")
    
    # Orijinal kontrol
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        print("🚫 Authentication failed!")
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    print("🎉 Authentication successful!")
    access_token = create_access_token(data={"user_id": db_user.id, "sub": db_user.email})
    return {"access_token": access_token, "token_type": "bearer"}