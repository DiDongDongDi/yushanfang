from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func

from app.core.database import Base


class CookingRecord(Base):
    __tablename__ = "cooking_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    dishes_json = Column(Text, nullable=True)
    buy_list = Column(Text, nullable=True)
    prep_steps = Column(Text, nullable=True)
    cook_steps = Column(Text, nullable=True)
    status = Column(String(20), default="进行中")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class CookingStep(Base):
    __tablename__ = "cooking_steps"

    id = Column(Integer, primary_key=True, index=True)
    record_id = Column(Integer, ForeignKey("cooking_records.id"), nullable=False)
    title = Column(String(200), nullable=True)
    detail = Column(Text, nullable=True)
    timer_minutes = Column(Integer, nullable=True)
    is_done = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
