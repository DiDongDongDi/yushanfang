from sqlalchemy import Column, Integer, String
from app.core.database import Base


class AIConfig(Base):
    __tablename__ = "ai_config"

    id = Column(Integer, primary_key=True, default=1)
    base_url = Column(String(255), default="https://dashscope.aliyuncs.com/compatible-mode/v1")
    api_key = Column(String(255), default="")
    model = Column(String(100), default="qwen-turbo")
