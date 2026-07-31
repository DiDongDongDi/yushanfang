from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi.responses import StreamingResponse

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
import json

router = APIRouter(prefix="/ai", tags=["AI"])


class RecommendRequest(BaseModel):
    preference: str = ""


class GenerateRecipeRequest(BaseModel):
    dish_name: str


class OptimizePlanRequest(BaseModel):
    dishes: list[str]
    plans: list[dict]


def build_recommend_prompt(preference: str, db, user_id: int) -> str:
    """构建推荐 prompt：排除用户已做过的菜，增加多样性"""
    from app.models.dish import Dish
    import random

    # 查询用户历史菜品
    history = db.query(Dish).filter(Dish.user_id == user_id).all()
    history_names = [d.name for d in history]
    history_str = "、".join(history_names) if history_names else "无"

    # 随机种子，让每次推荐不同
    seed = random.randint(1, 100000)
    # 获取当前季节/月份，推荐应季菜品
    month = __import__("datetime").datetime.now().month
    season_map = {1: "冬季", 2: "冬季", 3: "春季", 4: "春季", 5: "春季",
                  6: "夏季", 7: "夏季", 8: "夏季", 9: "秋季", 10: "秋季",
                  11: "秋季", 12: "冬季"}
    season = season_map[month]

    prompt = f"""你是一个专业的美食推荐专家，正在为用户推荐今日菜品。

当前季节：{season}（现在是{month}月）
用户偏好：{preference or "无特别偏好"}

用户之前做过/吃过的菜（请避免重复推荐）：{history_str}

要求：
1. 推荐3道适合当前季节的、与历史菜品尽量不重复的菜
2. 三道菜尽量涵盖不同口味和类型（如荤菜、素菜、汤类、主食等搭配）
3. 推荐的菜要新颖、多样，不要总是推荐番茄炒蛋、红烧肉这类最家常的菜
4. 每道菜用一句话简洁描述特点

随机种子：{seed}（请基于此种子，尽量给出不同的推荐组合）

返回JSON格式：{{"dishes": [{{"name": "菜名", "desc": "描述"}}]}}"""
    return prompt


@router.post("/recommend", summary="AI推荐今日菜品")
def ai_recommend(req: RecommendRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    from app.services.ai_service import ai_chat
    from app.models.dish import Dish
    prompt = build_recommend_prompt(req.preference, db, current_user.id)
    result = ai_chat(prompt, db=db)
    return result


@router.post("/generate-recipe/stream", summary="AI生成菜谱（流式）")
def ai_generate_recipe_stream(req: GenerateRecipeRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    from app.services.ai_service import ai_chat_stream
    prompt = f"""你是一个专业厨师。请为"{req.dish_name}"这道菜生成三部分内容，返回JSON格式：
{{
  "buy_list": "需要购买的食材清单，每行一个",
  "prep_steps": "备菜步骤，每行一个步骤",
  "cook_steps": "烹饪做法，每行一个步骤，每个步骤带预计时间（分钟）"
}}"""

    def generate():
        yield "data: {\"type\":\"start\"}\n\n"
        full_content = ""
        for chunk in ai_chat_stream(prompt, db=db):
            full_content += chunk
            escaped = chunk.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n")
            yield f"data: {{\"type\":\"chunk\",\"content\":\"{escaped}\"}}\n\n"
        import re
        json_match = re.search(r"\{.*\}", full_content, re.DOTALL)
        if json_match:
            yield f"data: {{\"type\":\"done\",\"result\":{json_match.group()}}}\n\n"
        else:
            yield f"data: {{\"type\":\"done\",\"result\":{{\"result\":\"{full_content}\"}}}}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.post("/recommend/stream", summary="AI推荐今日菜品（流式）")
def ai_recommend_stream(req: RecommendRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    from app.services.ai_service import ai_chat_stream
    prompt = build_recommend_prompt(req.preference, db, current_user.id)

    def generate():
        yield "data: {\"type\":\"start\"}\n\n"
        full_content = ""
        for chunk in ai_chat_stream(prompt, db=db):
            full_content += chunk
            escaped = chunk.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n")
            yield f"data: {{\"type\":\"chunk\",\"content\":\"{escaped}\"}}\n\n"
        import re
        json_match = re.search(r"\{.*\}", full_content, re.DOTALL)
        if json_match:
            yield f"data: {{\"type\":\"done\",\"result\":{json_match.group()}}}\n\n"
        else:
            yield f"data: {{\"type\":\"done\",\"result\":{{\"result\":\"{full_content}\"}}}}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.post("/optimize-plan", summary="AI整合多菜流程")
def ai_optimize_plan(req: OptimizePlanRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    from app.services.ai_service import ai_chat
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


@router.post("/optimize-plan/stream", summary="AI整合多菜流程（流式）")
def ai_optimize_plan_stream(req: OptimizePlanRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    from app.services.ai_service import ai_chat_stream
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

    def generate():
        yield "data: {\"type\":\"start\"}\n\n"
        full_content = ""
        for chunk in ai_chat_stream(prompt, db=db):
            full_content += chunk
            # 发送增量内容
            escaped = chunk.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n")
            yield f"data: {{\"type\":\"chunk\",\"content\":\"{escaped}\"}}\n\n"
        # 尝试解析最终 JSON
        import re
        json_match = re.search(r"\{.*\}", full_content, re.DOTALL)
        if json_match:
            yield f"data: {{\"type\":\"done\",\"result\":{json_match.group()}}}\n\n"
        else:
            yield f"data: {{\"type\":\"done\",\"result\":{{\"result\":\"{full_content}\"}}}}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
