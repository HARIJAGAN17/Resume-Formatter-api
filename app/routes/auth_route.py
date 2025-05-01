from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app.schema.user import UserCreate,UserOut,Token
from app.model import user_auth
from app.authentication.auth import get_db,get_password_hash,verify_password,create_access_token

router = APIRouter()


@router.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(user_auth.User).filter(user_auth.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(user_auth.User).filter(user_auth.User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    hashed_pw = get_password_hash(user.password)
    new_user = user_auth.User(username=user.username, email=user.email, hashed_password=hashed_pw,user_type = user.user_type)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(user_auth.User).filter(user_auth.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    token = create_access_token(data={"username": user.username}, user_type=user.user_type)
    return {"access_token": token, "token_type": "bearer"}