from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.ai_config import AIConfig

router = APIRouter(prefix="/settings", tags=["系统设置"])


class AIConfigUpdate(BaseModel):
    base_url: str | None = None
    api_key: str | None = None
    model: str | None = None


@router.get("/ai")
def get_ai_config(db: Session = Depends(get_db)):
    config = db.query(AIConfig).first()
    if not config:
        config = AIConfig()
        db.add(config)
        db.commit()
        db.refresh(config)
    return {
        "base_url": config.base_url,
        "api_key": config.api_key,
        "model": config.model,
    }


@router.put("/ai")
def update_ai_config(
    req: AIConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    config = db.query(AIConfig).first()
    if not config:
        config = AIConfig()
        db.add(config)
        db.commit()
        db.refresh(config)
    if req.base_url is not None:
        config.base_url = req.base_url
    if req.api_key is not None:
        config.api_key = req.api_key
    if req.model is not None:
        config.model = req.model
    db.commit()
    return {"msg": "AI 配置已更新"}
