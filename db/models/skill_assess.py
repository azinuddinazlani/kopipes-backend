from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from pydantic import BaseModel, EmailStr
from typing import Optional
from db.db_connection import Base

class SkillType(BaseModel):
    type: str
    level: str

class Skill_assess(Base):
    __tablename__ = "skill_assess"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String, default = "")
    questions = Column(String, default="")
    options = Column(String, default="")
    answer = Column(String, default="")
    level = Column(String, default="")
    status = Column(String, default="1")