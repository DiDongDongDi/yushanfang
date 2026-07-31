from pydantic import BaseModel
from datetime import datetime


class DishBase(BaseModel):
    name: str
    image: str | None = None
    description: str | None = None


class DishCreate(BaseModel):
    name: str
    image: str | None = None
    description: str | None = None
    recipe_json: str | None = None


class DishUpdate(BaseModel):
    name: str | None = None
    image: str | None = None
    description: str | None = None
    recipe_json: str | None = None


class DishInDB(DishBase):
    id: int
    user_id: int
    recipe_json: str | None = None
    created_at: datetime | None = None

    class Config:
        from_attributes = True
