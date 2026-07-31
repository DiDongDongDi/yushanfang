from pydantic import BaseModel, Field
from datetime import datetime


class UserBase(BaseModel):
    username: str
    nickname: str | None = None
    avatar: str | None = None


class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=100, description="密码")
    nickname: str | None = None
    phone: str | None = None


class UserLogin(BaseModel):
    username: str
    password: str


class WechatLogin(BaseModel):
    code: str


class UserUpdate(BaseModel):
    nickname: str | None = None
    avatar: str | None = None


class UserInDB(BaseModel):
    id: int
    username: str
    nickname: str | None = None
    avatar: str | None = None
    is_active: bool
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
