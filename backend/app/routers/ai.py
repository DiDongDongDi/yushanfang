from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/ai", tags=["AI"])


class RecommendRequest(BaseModel):
    preference: str = ""


class GenerateRecipeRequest(BaseModel):
    dish_name: str


class OptimizePlanRequest(BaseModel):
    dishes: list[str]
    plans: list[dict]


@router.post("/recommend", summary="AI推荐今日菜品")
def ai_recommend(req: RecommendRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    from app.services.ai_service import ai_chat
    prompt = f"你是一个美食推荐专家。用户偏好：{req.preference}。请推荐3道适合今天做的菜，每道菜用一句话描述，返回JSON格式：{{\"dishes\": [{{\"name\": \"菜名\", \"desc\": \"描述\"}}]}}"
    result = ai_chat(prompt, db=db)
    return result


@router.post("/generate-recipe", summary="AI生成菜谱（三部分）")
def ai_generate_recipe(req: GenerateRecipeRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    from app.services.ai_service import ai_chat
    prompt = f"""你是一个专业厨师。请为"{req.dish_name}"这道菜生成三部分内容，返回JSON格式：
{{
  "buy_list": "需要购买的食材清单，每行一个",
  "prep_steps": "备菜步骤，每行一个步骤",
  "cook_steps": "烹饪做法，每行一个步骤，每个步骤带预计时间（分钟）"
}}"""
    result = ai_chat(prompt, db=db)
    return result


@router.post("/optimize-plan", summary="AI整合多菜流程")
def ai_optimize_plan(req: OptimizePlanRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    from app.services.ai_service import ai_chat
    import json
    dishes_str = "、".join(req.dishes)
    plans_str = json.dumps(req.plans, ensure_ascii=False)
    prompt = f"""你是一个专业厨师。用户要做以下菜：{dishes_str}。
各菜的备菜和烹饪计划如下：{plans_str}
请将多道菜的买菜清单去重合并，备菜步骤和烹饪步骤按最优流程重新排序整合，返回JSON格式：
{{
  "buy_list": "整合后的买菜清单",
  "prep_steps": "整合优化后的备菜步骤",
  "cook_steps": "整合优化后的烹饪步骤（带时间）"
}}"""
    result = ai_chat(prompt, db=db)
    return result
