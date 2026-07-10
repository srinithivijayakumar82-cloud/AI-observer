from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime
from sqlalchemy.sql import func
from database import Base
class ObserveLog(Base):
    __tablename__="observe_logs"
    id=Column(Integer, primary_key=True, index=True)
    timestamp=Column(DateTime, default=func.now())
    prompt=Column(Text)
    response=Column(Text)
    temperature=Column(String)
    latency_ms=Column(Float)
    input_tokens=Column(Integer)
    output_tokens=Column(Integer)
    total_tokens=Column(Integer)
    estimated_cost=Column(Float)
    model=Column(String)
    success=Column(Boolean)
    error_message=Column(String, nullable=True)
    prompt_safe_score=Column(Float)
    quality_score=Column(Float)