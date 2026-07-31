from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.user import UserInDB, UserUpdate

router = APIRouter(prefix="/users", tags=["用户"])


@router.get("/me", response_model=UserInDB)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserInDB)
def update_me(
    req: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if req.nickname is not None:
        current_user.nickname = req.nickname
    if req.avatar is not None:
        current_user.avatar = req.avatar
    db.commit()
    db.refresh(current_user)
    return current_user
