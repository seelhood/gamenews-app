"""
/auth/register и /auth/login.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from api.deps import get_db
from api.auth import create_access_token
from api.schemas.user_schema import UserRegister, UserOut, TokenOut
from database.repositories.user_repository import UserRepository


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut)
def register(data: UserRegister, db: Session = Depends(get_db)):
    repo = UserRepository(db)

    if repo.get_by_username(data.username):
        raise HTTPException(400, "Логин занят")
    if repo.get_by_email(data.email):
        raise HTTPException(400, "Email занят")

    user = repo.create(data.username, data.email, data.password)
    return user


@router.post("/login", response_model=TokenOut)
def login(form: OAuth2PasswordRequestForm = Depends(),
          db: Session = Depends(get_db)):
    user = UserRepository(db).authenticate(form.username, form.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
        )

    token = create_access_token({
        "user_id": user.id,
        "username": user.username,
    })
    return {"access_token": token, "token_type": "bearer"}