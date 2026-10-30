from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from api.deps import get_db
from api.auth import get_current_user, get_current_admin_user
from api.schemas.user_schema import UserOut, UserRoleUpdate
from database.models.user import User

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserOut)
def get_me(current_user=Depends(get_current_user)):
    return current_user

@router.get("/", response_model=list[UserOut])
def list_users(limit: int = Query(50, ge=1, le=200),
               offset: int = Query(0, ge=0),
               db: Session = Depends(get_db),
               admin=Depends(get_current_admin_user)):
    return db.query(User).offset(offset).limit(limit).all()

@router.put("/{user_id}/role", response_model=UserOut)
def update_user_role(user_id: int, data: UserRoleUpdate,
                     db: Session = Depends(get_db),
                     admin=Depends(get_current_admin_user)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "Пользователь не найден")
    user.role = data.role
    db.commit()
    db.refresh(user)
    return user