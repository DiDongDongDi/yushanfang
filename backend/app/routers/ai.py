from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi.responses import StreamingResponse

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
import json
from app.services.ai_service import extract_json

router = APIRouter(prefix="/ai", tags=["AI"])


class RecommendRequest(BaseModel):
    preference: str = ""


class GenerateRecipeRequest(BaseModel):
    dish_name: str


class OptimizePlanRequest(BaseModel):
    dishes: list[str]
    plans: list[dict]


def stream_json_response(prompt: str, db):
    """通用流式 JSON 响应生成器"""
    from app.services.ai_service import ai_chat_stream

    def generate():
        yield "data: {\"type\":\"start\"}\n\n"
        full_content = ""
        for chunk in ai_chat_stream(prompt, db=db):
            full_content += chunk
            escaped = chunk.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n")
            yield f"data: {{\"type\":\"chunk\",\"content\":\"{escaped}\"}}\n\n"
        result = extract_json(full_content)
        if result:
            result_json = json.dumps(result, ensure_ascii=False)
            yield f"data: {{\"type\":\"done\",\"result\":{result_json}}}\n\n"
        else:
            escaped = full_content.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n")
            yield f"data: {{\"type\":\"done\",\"result\":{{\"result\":\"{escaped}\"}}}}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


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

    # 随机挑选一种推荐风格/主题，增加每次推荐的变化
    styles = [
        "家常下饭", "清爽健康", "重口味过瘾", "清淡养生",
        "快手省时", "营养均衡", "创意融合", "传统经典",
        "酸甜开胃", "鲜香浓郁", "素菜为主", "汤汤水水"
    ]
    style = random.choice(styles)

    # 随机限定菜系方向
    cuisines = ["川菜", "粤菜", "湘菜", "江浙菜", "东北菜", "鲁菜", "本帮菜", "闽菜", "家常菜", "融合菜"]
    cuisine = random.choice(cuisines)

    prompt = f"""你是一个专业的美食推荐专家，正在为用户推荐今日菜品。

当前季节：{season}（现在是{month}月）
用户偏好：{preference or "无特别偏好"}
本次推荐主题：{style}（偏{cuisine}风味）

用户之前做过/吃过的菜（请务必避免重复推荐）：{history_str}

要求：
1. 推荐3道适合当前季节、与历史菜品完全不重复的菜
2. 三道菜尽量涵盖不同烹饪方式和食材（如：一道热菜、一道素菜/凉菜、一道汤或主食）
3. 推荐的菜要新颖多样、有创意，绝对不要推荐最常见的家常菜（如番茄炒蛋、土豆丝、红烧肉、蛋炒饭这类）
4. 要符合"本次推荐主题"的风格
5. 每道菜用一句话简洁描述特点

随机种子：{seed}（请基于此种子生成与此前不同的推荐组合）

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

    return stream_json_response(prompt, db)


@router.post("/recommend/stream", summary="AI推荐今日菜品（流式）")
def ai_recommend_stream(req: RecommendRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    from app.services.ai_service import ai_chat_stream
    prompt = build_recommend_prompt(req.preference, db, current_user.id)

    return stream_json_response(prompt, db)


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

    return stream_json_response(prompt, db)
