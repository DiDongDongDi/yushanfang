from pydantic import BaseModel, Field
from datetime import datetime


class UserBase(BaseModel):
    phone: str | None = None
    nickname: str | None = None
    avatar: str | None = None


class UserCreate(BaseModel):
    phone: str
    code: str
    nickname: str | None = None


class UserLogin(BaseModel):
    phone: str
    code: str


class WechatLogin(BaseModel):
    code: str


class UserUpdate(BaseModel):
    nickname: str | None = None
    avatar: str | None = None


class UserInDB(UserBase):
    id: int
    is_active: bool
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class SendCodeRequest(BaseModel):
    phone: str
