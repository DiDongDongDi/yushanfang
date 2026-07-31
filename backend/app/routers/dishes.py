from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.dish import Dish
from app.schemas.dish import DishCreate, DishUpdate, DishInDB

router = APIRouter(prefix="/dishes", tags=["菜品"])


@router.post("", response_model=DishInDB)
def create_dish(dish: DishCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_dish = Dish(user_id=current_user.id, name=dish.name, image=dish.image, description=dish.description)
    db.add(db_dish)
    db.commit()
    db.refresh(db_dish)
    return db_dish


@router.get("", response_model=list[DishInDB])
def list_dishes(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Dish).filter(Dish.user_id == current_user.id).order_by(Dish.created_at.desc()).all()


@router.get("/{dish_id}", response_model=DishInDB)
def get_dish(dish_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    dish = db.query(Dish).filter(Dish.id == dish_id, Dish.user_id == current_user.id).first()
    if not dish:
        raise HTTPException(status_code=404, detail="菜品不存在")
    return dish


@router.put("/{dish_id}", response_model=DishInDB)
def update_dish(dish_id: int, dish: DishUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_dish = db.query(Dish).filter(Dish.id == dish_id, Dish.user_id == current_user.id).first()
    if not db_dish:
        raise HTTPException(status_code=404, detail="菜品不存在")
    if dish.name is not None:
        db_dish.name = dish.name
    if dish.image is not None:
        db_dish.image = dish.image
    if dish.description is not None:
        db_dish.description = dish.description
    db.commit()
    db.refresh(db_dish)
    return db_dish


@router.delete("/{dish_id}", status_code=204)
def delete_dish(dish_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_dish = db.query(Dish).filter(Dish.id == dish_id, Dish.user_id == current_user.id).first()
    if not db_dish:
        raise HTTPException(status_code=404, detail="菜品不存在")
    db.delete(db_dish)
    db.commit()
