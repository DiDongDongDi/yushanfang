from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserRegister, UserLogin, WechatLogin, UserInDB, Token

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register", response_model=UserInDB, status_code=201)
def register(req: UserRegister, db: Session = Depends(get_db)):
    # 检查用户名是否已存在
    if db.query(User).filter(User.username == req.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    if req.phone and db.query(User).filter(User.phone == req.phone).first():
        raise HTTPException(status_code=400, detail="手机号已注册")

    user = User(
        username=req.username,
        nickname=req.nickname or req.username,
        phone=req.phone,
        password_hash=get_password_hash(req.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(req: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == req.username).first()
    if not user or not user.password_hash or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=400, detail="用户名或密码错误")

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
