from pydantic import BaseModel
from datetime import datetime


class CookingRecordCreate(BaseModel):
    dish_ids: list[int]


class CookingRecordUpdate(BaseModel):
    status: str | None = None
    buy_list: str | None = None
    prep_steps: str | None = None
    cook_steps: str | None = None


class CookingStepUpdate(BaseModel):
    is_done: bool | None = None
    timer_minutes: int | None = None


class CookingStepInDB(BaseModel):
    id: int
    record_id: int
    title: str | None = None
    detail: str | None = None
    timer_minutes: int | None = None
    is_done: bool = False
    sort_order: int = 0

    class Config:
        from_attributes = True


class CookingRecordInDB(BaseModel):
    id: int
    user_id: int
    dishes_json: str | None = None
    buy_list: str | None = None
    prep_steps: str | None = None
    cook_steps: str | None = None
    status: str = "进行中"
    steps: list[CookingStepInDB] = []
    created_at: datetime | None = None

    class Config:
        from_attributes = True
