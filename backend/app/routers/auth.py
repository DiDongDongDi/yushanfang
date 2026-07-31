from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import create_access_token, get_password_hash
from app.core.config import settings
from app.models.user import User
from app.schemas.user import (
    UserCreate, WechatLogin, UserInDB, Token, SendCodeRequest
)

router = APIRouter(prefix="/auth", tags=["认证"])

# 模拟验证码存储（生产环境用 Redis）
fake_code_store: dict[str, str] = {}


@router.post("/send-code", status_code=200)
def send_code(req: SendCodeRequest):
    import random
    code = str(random.randint(100000, 999999))
    fake_code_store[req.phone] = code
    
    # 开发模式：直接返回验证码（方便测试）
    if settings.ENV == "development":
        print(f"[开发模式] 验证码 {code} 发送到 {req.phone}")
        return {"msg": "验证码已发送", "code": code}
    
    # 生产模式：尝试发送短信
    # TODO: 接入腾讯云短信服务
    # 如果未配置短信服务，仍然返回验证码（仅用于测试）
    print(f"[生产模式] 验证码 {code} 发送到 {req.phone}（未配置短信服务）")
    return {"msg": "验证码已发送"}


@router.post("/login", response_model=Token)
def login(req: UserCreate, db: Session = Depends(get_db)):
    code = fake_code_store.get(req.phone)
    if not code or code != req.code:
        raise HTTPException(status_code=400, detail="验证码错误")
    del fake_code_store[req.phone]

    user = db.query(User).filter(User.phone == req.phone).first()
    if not user:
        user = User(phone=req.phone, nickname=req.nickname or "新用户")
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_access_token(user.id)
    return {"access_token": token, "token_type": "bearer"}


@router.post("/wechat-login", response_model=Token)
def wechat_login(req: WechatLogin, db: Session = Depends(get_db)):
    import requests
    appid = "your_wechat_appid"
    secret = "your_wechat_secret"
    resp = requests.get(
        "https://api.weixin.qq.com/sns/jscode2session",
        params={"appid": appid, "secret": secret, "js_code": req.code, "grant_type": "authorization_code"},
    ).json()
    openid = resp.get("openid")
    if not openid:
        raise HTTPException(status_code=400, detail="微信登录失败")

    user = db.query(User).filter(User.wechat_openid == openid).first()
    if not user:
        user = User(wechat_openid=openid, nickname="微信用户")
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_access_token(user.id)
    return {"access_token": token, "token_type": "bearer"}
