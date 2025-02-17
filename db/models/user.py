from sqlalchemy import Column, Integer, String, ForeignKey, Float, Table
from sqlalchemy.orm import relationship
from pydantic import BaseModel, EmailStr
from typing import Optional
from db.db_connection import Base

class UserRegister(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr

class UserSchema(BaseModel):
    name: Optional[int] = None
    type: str

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)
    type = Column(String, default="Pending")
    about = Column(String, nullable=True)
    resume = Column(String, nullable=True)
    resume_base64 = Column(String, nullable=True)

    skills = relationship('UserSkills', back_populates='user', lazy="joined")
    skill_assess = relationship('UserSkillAssess', back_populates='user', lazy="joined")


class UserSkills(Base):
    __tablename__ = "users_skills"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String, nullable=False)
    level = Column(String, nullable=False)

    user = relationship('User', back_populates='skills')

class UserSkillAssessSchema(BaseModel):
    user_id: int
    version: Optional[str] = "0"
    qs_type: str
    question: str
    option: str
    answer_given: Optional[str] = None
    answer_real: str
    qs_level: str
    user_level: str

class UserSkillAssess(Base):
    __tablename__ = "users_skill_assess"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    version = Column(Integer, default="0")
    qs_type = Column(String, default="")
    question = Column(String, nullable=False, default="")
    option = Column(String, nullable=False, default="")
    answer_given = Column(String, nullable=False, default="")
    answer_real = Column(String, nullable=False, default="")
    qs_level = Column(String, default="0")
    user_level = Column(String, default="0")

    user = relationship('User', back_populates='skill_assess')
